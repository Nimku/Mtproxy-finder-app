"""Real MTProto proxy verification — a port of the app's MtprotoChecker.kt.

Why this exists at all: the obvious "is it alive" test is to open a TCP socket,
send some bytes and see whether anything comes back. That passes for *any*
server that answers — a web server, an SSH daemon, a captive portal — so lists
built that way are full of addresses that are reachable but are not Telegram
proxies, or do not accept the secret they were published with.

This does what Telegram itself does:

    TCP  →  (FakeTLS handshake if the secret starts with ee)
         →  obfuscated2 handshake
         →  req_pq_multi
         →  parse resPQ and verify the nonce we sent comes back

A server only gets through all of that if it really is an MTProto proxy and the
secret is correct, so a proxy that passes here is genuinely usable.

Keep this in sync with app/src/main/java/com/nimku/proxy/MtprotoChecker.kt — the
whole point is that the bot and the app agree on what "working" means.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import socket
import struct
import time
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PROTO_ABRIDGED = b"\xef\xef\xef\xef"
PROTO_INTERMEDIATE = b"\xee\xee\xee\xee"
PROTO_SECURE = b"\xdd\xdd\xdd\xdd"

REQ_PQ_MULTI = 0xBE7E8EF1
RES_PQ = 0x05162463
MAX_FRAME = 2 * 1024 * 1024

FAKETLS_HELLO_LEN = 517
FAKETLS_CCS = b"\x14\x03\x03\x00\x01\x01"
FAKETLS_APP_PREFIX = b"\x17\x03\x03"
FAKETLS_MAX_APP = 1425
DEFAULT_DOMAIN = "www.google.com"

# Telegram DC to advertise in the handshake. The app uses 2; anything valid works,
# but matching it keeps the two implementations behaving identically.
DC_ID = 2

_HEX_DIGITS = set("0123456789abcdef")


@dataclass(frozen=True)
class Secret:
    raw: bytes           # the 16 bytes that actually key the connection
    is_faketls: bool     # ee-prefixed secrets wrap everything in a fake TLS session
    domain: str = DEFAULT_DOMAIN


@dataclass(frozen=True)
class CheckResult:
    ok: bool
    rtt_ms: int
    error: str | None = None


# ─────────────────────────────────────────────────────────────
#  Secret / link parsing
# ─────────────────────────────────────────────────────────────

def decode_secret(secret: str) -> Secret | None:
    """Accepts every form these lists publish: raw hex, dd-prefixed hex,
    ee-prefixed hex with a trailing domain, and base64/base64url."""
    s = secret.strip()
    if not s:
        return None
    lower = s.lower()

    if all(c in _HEX_DIGITS for c in lower):
        try:
            if lower.startswith("ee"):
                if len(lower) < 34:
                    return None
                raw = bytes.fromhex(lower[2:34])
                domain = DEFAULT_DOMAIN
                if len(lower) > 34:
                    try:
                        tail = bytes.fromhex(_even(lower[34:])).decode("ascii", "ignore")
                        domain = _extract_domain(tail)
                    except ValueError:
                        pass
                return Secret(raw, True, domain)
            if lower.startswith("dd"):
                if len(lower) < 34:
                    return None
                return Secret(bytes.fromhex(lower[2:34]), False)
            data = bytes.fromhex(_even(lower))
            if len(data) >= 16:
                return Secret(data[:16], False)
        except ValueError:
            pass

    try:
        b64 = s.replace("-", "+").replace("_", "/")
        b64 += "=" * ((4 - len(b64) % 4) % 4)
        raw = base64.b64decode(b64)
    except Exception:
        return None

    if len(raw) == 16:
        return Secret(raw, False)
    if len(raw) >= 17 and raw[0] == 0xDD:
        return Secret(raw[1:17], False)
    if len(raw) >= 17 and raw[0] == 0xEE:
        tail = raw[17:].decode("ascii", "ignore")
        cleaned = "".join(c for c in tail if c.isalnum() or c in ".-")
        return Secret(raw[1:17], True, _extract_domain(cleaned))
    if len(raw) > 16:
        return Secret(raw[:16], False)
    return None


def _even(hex_str: str) -> str:
    return hex_str if len(hex_str) % 2 == 0 else "0" + hex_str


def _extract_domain(text: str) -> str:
    """Pulls the SNI domain out of the tail of an ee secret.

    Deliberately differs from MtprotoChecker.kt on one point: the Kotlin keeps
    the *shortest* TLD match, so "www.google.com" comes out as "www.google.co"
    (".co" matches at the same position as ".com" and is shorter). Here the
    earliest match wins, and the longest TLD at that position, which is what the
    encoded domain actually is. It only affects the SNI we present — the FakeTLS
    HMAC covers the bytes we send either way — so the two implementations still
    agree on whether a proxy passes.
    """
    cleaned = text.strip().strip("\x00")
    if not cleaned:
        return DEFAULT_DOMAIN
    tlds = (".com", ".net", ".org", ".ru", ".io", ".co", ".dev", ".app",
            ".cloud", ".me", ".info", ".homes", ".shop")
    low = cleaned.lower()
    best_pos: int | None = None
    best_end = 0
    for tld in tlds:
        pos = low.find(tld)
        if pos <= 0:
            continue
        end = pos + len(tld)
        if best_pos is None or pos < best_pos or (pos == best_pos and end > best_end):
            best_pos, best_end = pos, end
    if best_pos is None:
        return cleaned[:64] or DEFAULT_DOMAIN
    return cleaned[:best_end].lstrip("^`~!@#$%&*()_+=[]{}|;:'\",<>/?\\ ") or DEFAULT_DOMAIN


# ─────────────────────────────────────────────────────────────
#  obfuscated2
# ─────────────────────────────────────────────────────────────

class _AesCtr:
    """AES-CTR keeps running state across calls — the stream position must carry
    over between the handshake and every frame after it."""

    def __init__(self, key: bytes, iv: bytes) -> None:
        self._ctx = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()

    def update(self, data: bytes) -> bytes:
        return self._ctx.update(data)


_FORBIDDEN_FIRST4 = {
    b"GET ", b"POST", b"HEAD", b"OPTI", b"\x00\x00\x00\x00",
    PROTO_ABRIDGED, PROTO_INTERMEDIATE, PROTO_SECURE,
}


def _make_handshake(secret: bytes, faketls: bool) -> tuple[bytes, _AesCtr, _AesCtr]:
    """Builds the 64-byte obfuscated2 init packet plus the two cipher streams.

    The first bytes are constrained so the packet can't be mistaken for HTTP or
    for one of the plain transport tags — that's what makes it look like noise.
    """
    while True:
        init = bytearray(os.urandom(64))
        if init[0] == 0xEF:
            continue
        if bytes(init[:4]) in _FORBIDDEN_FIRST4:
            continue
        if init[4:8] == b"\x00\x00\x00\x00":
            continue
        break

    init[56:60] = PROTO_SECURE
    init[60] = DC_ID & 0xFF
    init[61:64] = b"\x00\x00\x00"

    enc_key_material = bytes(init[8:40])
    enc_iv = bytes(init[40:56])
    dec_key_material = bytes(init[55 - i] for i in range(32))
    dec_iv = bytes(init[23 - i] for i in range(16))

    enc = _AesCtr(hashlib.sha256(enc_key_material + secret).digest(), enc_iv)
    dec = _AesCtr(hashlib.sha256(dec_key_material + secret).digest(), dec_iv)

    # Only bytes 56..64 of the init packet travel encrypted; the rest goes plain.
    encrypted = enc.update(bytes(init))
    init[56:64] = encrypted[56:64]
    return bytes(init), enc, dec


def _make_req_pq_multi() -> tuple[bytes, bytes]:
    nonce = os.urandom(16)
    payload = struct.pack("<I", REQ_PQ_MULTI) + nonce
    msg_id = (int(time.time() * 4294967296.0)) & ~3
    message = b"\x00" * 8 + struct.pack("<q", msg_id) + struct.pack("<I", len(payload)) + payload
    return nonce, message


def _frame(data: bytes) -> bytes:
    pad_len = int.from_bytes(os.urandom(1), "big") % 4
    padding = os.urandom(pad_len)
    return struct.pack("<I", len(data) + pad_len) + data + padding


def _parse_res_pq(frame: bytes, expected_nonce: bytes) -> None:
    if len(frame) < 40:
        raise ValueError(f"short response ({len(frame)} bytes)")
    if frame[:8] != b"\x00" * 8:
        raise ValueError("not an unencrypted message")
    msg_len = struct.unpack_from("<I", frame, 16)[0]
    if not 1 <= msg_len <= len(frame) - 20:
        raise ValueError(f"bad message length {msg_len}")
    body = frame[20:20 + msg_len]
    if len(body) < 36:
        raise ValueError("short body")
    constructor = struct.unpack_from("<I", body, 0)[0]
    if constructor != RES_PQ:
        raise ValueError(f"not resPQ (0x{constructor:08x})")
    if body[4:20] != expected_nonce:
        raise ValueError("nonce mismatch")


# ─────────────────────────────────────────────────────────────
#  Transports
# ─────────────────────────────────────────────────────────────

class _Plain:
    def __init__(self, sock: socket.socket) -> None:
        self._sock = sock

    def write(self, data: bytes) -> None:
        self._sock.sendall(data)

    def read_exact(self, n: int) -> bytes:
        return _recv_exact(self._sock, n)


class _FakeTls:
    """ee secrets: the proxy pretends to be an HTTPS server, so we have to speak
    enough TLS to get past the front door before the real handshake starts."""

    def __init__(self, sock: socket.socket, secret: bytes, domain: str) -> None:
        self._sock = sock
        self._secret = secret
        self._domain = domain
        self._buffer = b""
        self._offset = 0
        self._wrote_ccs = False

    def handshake(self) -> None:
        hello, client_random = _make_client_hello(self._secret, self._domain)
        self._sock.sendall(hello)

        first_header = _recv_exact(self._sock, 5)
        rec_type, payload_len = _parse_tls_header(first_header)
        if rec_type != 0x16:
            raise ValueError(f"expected ServerHello, got 0x{rec_type:02x}")
        first_payload = _recv_exact(self._sock, payload_len)

        ccs = _recv_exact(self._sock, len(FAKETLS_CCS))
        if ccs != FAKETLS_CCS:
            raise ValueError("bad ChangeCipherSpec")

        app_header = _recv_exact(self._sock, 5)
        app_type, app_len = _parse_tls_header(app_header)
        if app_type != 0x17:
            raise ValueError(f"expected application data, got 0x{app_type:02x}")
        app_payload = _recv_exact(self._sock, app_len)

        response = first_header + first_payload + ccs + app_header + app_payload
        _validate_faketls_server(self._secret, client_random, response)

    def write(self, data: bytes) -> None:
        out = bytearray()
        if not self._wrote_ccs:
            out += FAKETLS_CCS
            self._wrote_ccs = True
        for i in range(0, len(data), FAKETLS_MAX_APP):
            chunk = data[i:i + FAKETLS_MAX_APP]
            out += FAKETLS_APP_PREFIX + len(chunk).to_bytes(2, "big") + chunk
        self._sock.sendall(bytes(out))

    def read_exact(self, n: int) -> bytes:
        out = bytearray()
        while len(out) < n:
            if self._offset >= len(self._buffer):
                self._buffer = self._read_app_payload()
                self._offset = 0
            take = min(n - len(out), len(self._buffer) - self._offset)
            out += self._buffer[self._offset:self._offset + take]
            self._offset += take
        return bytes(out)

    def _read_app_payload(self) -> bytes:
        while True:
            header = _recv_exact(self._sock, 5)
            rec_type, length = _parse_tls_header(header)
            payload = _recv_exact(self._sock, length)
            if rec_type == 0x14 and payload == b"\x01":
                continue  # another ChangeCipherSpec, skip it
            if rec_type != 0x17:
                raise ValueError(f"expected application data, got 0x{rec_type:02x}")
            if payload:
                return payload


def _parse_tls_header(header: bytes) -> tuple[int, int]:
    if len(header) != 5:
        raise ValueError("short TLS header")
    if header[1:3] not in (b"\x03\x01", b"\x03\x03"):
        raise ValueError("bad TLS version")
    return header[0], int.from_bytes(header[3:5], "big")


def _make_grease() -> list[int]:
    greases = [(b & 0xF0) + 0x0A for b in os.urandom(7)]
    for i in range(1, len(greases), 2):
        if greases[i] == greases[i - 1]:
            greases[i] ^= 0x10
    return greases


def _make_client_hello(secret: bytes, domain: str) -> tuple[bytes, bytes]:
    """A byte-for-byte imitation of a real Chrome ClientHello, with the client
    random replaced by an HMAC of the whole packet — that HMAC is how the proxy
    recognises us, and how we later recognise the proxy."""
    if len(secret) != 16:
        raise ValueError("secret must be 16 bytes")
    domain_bytes = domain.encode()
    g = _make_grease()
    out = bytearray()

    out += bytes([0x16, 0x03, 0x01, 0x02, 0x00, 0x01, 0x00, 0x01, 0xFC, 0x03, 0x03])
    random_offset = len(out)
    out += b"\x00" * 32
    out += b"\x20" + os.urandom(32)
    out += b"\x00\x22"
    out += bytes([g[0], g[0]])
    out += bytes([
        0x13, 0x01, 0x13, 0x02, 0x13, 0x03, 0xC0, 0x2B, 0xC0, 0x2F,
        0xC0, 0x2C, 0xC0, 0x30, 0xCC, 0xA9, 0xCC, 0xA8, 0xC0, 0x13,
        0xC0, 0x14, 0x00, 0x9C, 0x00, 0x9D, 0x00, 0x2F, 0x00, 0x35,
        0x00, 0x0A, 0x01, 0x00, 0x01, 0x91,
    ])
    out += bytes([g[2], g[2]])
    out += b"\x00\x00\x00\x00"
    out += (len(domain_bytes) + 5).to_bytes(2, "big")
    out += (len(domain_bytes) + 3).to_bytes(2, "big")
    out += b"\x00"
    out += len(domain_bytes).to_bytes(2, "big")
    out += domain_bytes
    out += bytes([0x00, 0x17, 0x00, 0x00, 0xFF, 0x01, 0x00, 0x01, 0x00,
                  0x00, 0x0A, 0x00, 0x0A, 0x00, 0x08])
    out += bytes([g[4], g[4]])
    out += bytes([
        0x00, 0x1D, 0x00, 0x17, 0x00, 0x18, 0x00, 0x0B, 0x00, 0x02, 0x01, 0x00,
        0x00, 0x23, 0x00, 0x00, 0x00, 0x10, 0x00, 0x0E, 0x00, 0x0C, 0x02, 0x68,
        0x32, 0x08, 0x68, 0x74, 0x74, 0x70, 0x2F, 0x31, 0x2E, 0x31, 0x00, 0x05,
        0x00, 0x05, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0D, 0x00, 0x14, 0x00,
        0x12, 0x04, 0x03, 0x08, 0x04, 0x04, 0x01, 0x05, 0x03, 0x08, 0x05, 0x05,
        0x01, 0x08, 0x06, 0x06, 0x01, 0x02, 0x01, 0x00, 0x12, 0x00, 0x00, 0x00,
        0x33, 0x00, 0x2B, 0x00, 0x29,
    ])
    out += bytes([g[4], g[4]])
    out += bytes([0x00, 0x01, 0x00, 0x00, 0x1D, 0x00, 0x20])
    out += os.urandom(32)
    out += bytes([0x00, 0x2D, 0x00, 0x02, 0x01, 0x01, 0x00, 0x2B, 0x00, 0x0B, 0x0A])
    out += bytes([g[6], g[6]])
    out += bytes([0x03, 0x04, 0x03, 0x03, 0x03, 0x02, 0x03, 0x01,
                  0x00, 0x1B, 0x00, 0x03, 0x02, 0x00, 0x02])
    out += bytes([g[3], g[3]])
    out += bytes([0x00, 0x01, 0x00, 0x00, 0x15])

    padding_length = FAKETLS_HELLO_LEN - 2 - len(out)
    if padding_length < 0:
        raise ValueError("ClientHello too long")
    out += padding_length.to_bytes(2, "big")
    out += b"\x00" * padding_length

    hello = bytearray(out)
    if len(hello) != FAKETLS_HELLO_LEN:
        raise ValueError(f"bad ClientHello length {len(hello)}")

    digest = hmac.new(secret, bytes(hello), hashlib.sha256).digest()
    timestamp = int(time.time())
    tail = struct.unpack_from("<I", digest, 28)[0]
    client_random = bytearray(digest[:28]) + struct.pack("<I", (tail ^ timestamp) & 0xFFFFFFFF)
    hello[random_offset:random_offset + 32] = client_random
    return bytes(hello), bytes(client_random)


def _validate_faketls_server(secret: bytes, client_random: bytes, response: bytes) -> None:
    """The proxy proves it knows the secret by putting an HMAC where the server
    random would normally be. A real TLS server can't produce this."""
    if len(response) < 43:
        raise ValueError("short FakeTLS response")
    server_random = response[11:43]
    zeroed = bytearray(response)
    zeroed[11:43] = b"\x00" * 32
    expected = hmac.new(secret, client_random + bytes(zeroed), hashlib.sha256).digest()
    if server_random != expected:
        raise ValueError("FakeTLS HMAC mismatch — not a proxy, or wrong secret")


def _recv_exact(sock: socket.socket, n: int) -> bytes:
    if n < 0:
        raise ValueError("negative read length")
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError(f"closed while reading {n} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


# ─────────────────────────────────────────────────────────────
#  Public entry point
# ─────────────────────────────────────────────────────────────

def check(
    host: str,
    port: int,
    secret: Secret,
    connect_timeout: float = 2.5,
    response_timeout: float = 3.5,
) -> CheckResult:
    """Blocking. Run it in a thread pool — see scraper.verify_all()."""
    started = time.monotonic()
    sock = None
    try:
        sock = socket.create_connection((host, port), timeout=connect_timeout)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(response_timeout)

        if secret.is_faketls:
            transport: _FakeTls | _Plain = _FakeTls(sock, secret.raw, secret.domain)
            transport.handshake()
        else:
            transport = _Plain(sock)

        init, enc, dec = _make_handshake(secret.raw, secret.is_faketls)
        transport.write(init)

        nonce, request = _make_req_pq_multi()
        transport.write(enc.update(_frame(request)))

        length_bytes = dec.update(transport.read_exact(4))
        frame_len = struct.unpack("<I", length_bytes)[0]
        if frame_len > 0x80000000:
            frame_len -= 0x80000000
        if not 1 <= frame_len <= MAX_FRAME:
            raise ValueError(f"bad frame length {frame_len}")
        _parse_res_pq(dec.update(transport.read_exact(frame_len)), nonce)

        rtt = int((time.monotonic() - started) * 1000)
        return CheckResult(True, max(rtt, 1))
    except Exception as exc:
        rtt = int((time.monotonic() - started) * 1000)
        return CheckResult(False, rtt, str(exc) or exc.__class__.__name__)
    finally:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass


def check_link(host: str, port: int, secret_str: str, **kwargs) -> CheckResult:
    secret = decode_secret(secret_str)
    if secret is None:
        return CheckResult(False, -1, "unparseable secret")
    return check(host, port, secret, **kwargs)


# ─────────────────────────────────────────────────────────────
#  Self-test:  python -m mtproto
# ─────────────────────────────────────────────────────────────

def _selftest() -> int:
    """Proves the checker works on a machine with real network egress.

    A Telegram data centre speaks plain obfuscated2 with no proxy secret, so it
    exercises the whole path — handshake, req_pq_multi, resPQ, nonce check —
    against a server that is definitely not lying to us. If these pass, a
    "dead" verdict on a real proxy is the proxy's fault, not this code's.
    """
    dcs = [("149.154.167.51", "DC2 Amsterdam"),
           ("149.154.175.53", "DC1 Miami"),
           ("91.108.56.130", "DC5 Singapore")]
    print("Checking against real Telegram data centres (empty secret, port 443):")
    passed = 0
    for ip, label in dcs:
        r = check(ip, 443, Secret(raw=b"", is_faketls=False))
        print(f"  {'PASS' if r.ok else 'FAIL'}  {label:16} {r.rtt_ms:5}ms  "
              f"{r.error or 'resPQ received, nonce verified'}")
        passed += r.ok
    if passed:
        print(f"\n{passed}/{len(dcs)} reachable — the MTProto implementation is working.")
        return 0
    print("\nNo data centre answered. Either this host has no direct network access, "
          "or Telegram itself is blocked here — run this on the VPS.")
    return 1


if __name__ == "__main__":
    raise SystemExit(_selftest())

package com.nimku.proxy.ui.theme

import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.ui.Modifier

/** Keeps top bars, content and floating actions outside display cutouts and system gestures. */
fun Modifier.mtSafeScreen(): Modifier = safeDrawingPadding()

/** Keeps persistent actions reachable above gesture navigation and the on-screen keyboard. */
fun Modifier.mtBottomActions(): Modifier = navigationBarsPadding().imePadding()

/** Keeps editable dialogs usable on short screens while the IME is visible. */
fun Modifier.mtImeAware(): Modifier = navigationBarsPadding().imePadding()


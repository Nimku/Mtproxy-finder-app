package com.nimku.proxy.ui

import android.content.Intent
import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Language
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.lifecycleScope
import com.nimku.proxy.MainActivity
import com.nimku.proxy.R
import com.nimku.proxy.core.locale.AppLocaleManager
import com.nimku.proxy.core.util.TelegramIntents
import com.nimku.proxy.license.LicenseManager
import com.nimku.proxy.ui.theme.MtproxyFinderTheme
import com.nimku.proxy.ui.theme.mtSafeScreen
import kotlinx.coroutines.launch

/**
 * Paywall / subscription check. Shown instead of [MainActivity] whenever
 * [LicenseManager.cachedResult] (or a fresh [LicenseManager.refresh]) says the current device
 * isn't covered by an active Telegram Stars subscription. The app never talks to the bot or the
 * VPS here — it only reads license/status.json from GitHub/CDN mirrors; payment itself happens
 * entirely inside the Telegram bot.
 */
class SubscriptionGateActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent { MtproxyFinderTheme { GateScreen() } }
    }

    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    private fun GateScreen() {
        var telegramIdInput by remember {
            mutableStateOf(LicenseManager.savedTelegramId(this) ?: "")
        }
        var editingId by remember { mutableStateOf(LicenseManager.savedTelegramId(this) == null) }
        var checking by remember { mutableStateOf(false) }
        var result by remember { mutableStateOf(LicenseManager.cachedResult(this)) }
        var error by remember { mutableStateOf<String?>(null) }
        var languageDialogVisible by remember { mutableStateOf(false) }

        fun goToApp() {
            startActivity(Intent(this@SubscriptionGateActivity, MainActivity::class.java))
            finish()
        }

        suspend fun doRefresh() {
            checking = true
            error = null
            val fresh = LicenseManager.refresh(this@SubscriptionGateActivity)
            result = fresh
            checking = false
            if (fresh.usable) goToApp()
        }

        LaunchedEffect(Unit) {
            if (LicenseManager.savedTelegramId(this@SubscriptionGateActivity) != null) {
                doRefresh()
            }
        }

        Scaffold(modifier = Modifier.mtSafeScreen()) { padding ->
            Column(
                modifier =
                    Modifier.fillMaxSize()
                        .padding(padding)
                        .padding(24.dp)
                        .verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                TextButton(
                    onClick = { languageDialogVisible = true },
                    modifier = Modifier.align(Alignment.End),
                ) {
                    Icon(
                        Icons.Filled.Language,
                        contentDescription = stringResource(R.string.settings_language),
                        modifier = Modifier.size(18.dp),
                    )
                    Text(
                        AppLocaleManager.supportedLocales
                            .firstOrNull { it.languageTag == AppLocaleManager.currentTag() }
                            ?.nativeName ?: stringResource(R.string.language_follow_system),
                        modifier = Modifier.padding(start = 6.dp),
                    )
                }
                Icon(
                    Icons.Filled.Star,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.primary,
                )
                Text(
                    stringResource(R.string.subscription_title),
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )
                Text(
                    stringResource(R.string.subscription_body),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        Modifier.fillMaxWidth().padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(10.dp),
                    ) {
                        if (editingId) {
                            OutlinedTextField(
                                value = telegramIdInput,
                                onValueChange = { telegramIdInput = it.filter(Char::isDigit) },
                                label = { Text(stringResource(R.string.subscription_id_label)) },
                                placeholder = { Text("123456789") },
                                singleLine = true,
                                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                                modifier = Modifier.fillMaxWidth(),
                            )
                            Text(
                                stringResource(R.string.subscription_id_hint),
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                            )
                            Button(
                                onClick = {
                                    if (LicenseManager.isValidTelegramId(telegramIdInput)) {
                                        LicenseManager.linkTelegramId(this@SubscriptionGateActivity, telegramIdInput)
                                        editingId = false
                                        error = null
                                        result = LicenseManager.cachedResult(this@SubscriptionGateActivity)
                                        // Linking clears any cached status, so check immediately instead of
                                        // making the user separately tap "Check now" right after Save.
                                        lifecycleScope.launch { doRefresh() }
                                    } else {
                                        error = getString(R.string.subscription_id_invalid)
                                    }
                                },
                                modifier = Modifier.fillMaxWidth(),
                                enabled = !checking,
                            ) { Text(stringResource(R.string.subscription_id_save)) }
                        } else {
                            Text(
                                stringResource(R.string.subscription_linked_as, telegramIdInput),
                                fontWeight = FontWeight.SemiBold,
                            )
                            Text(
                                when (result.state) {
                                    LicenseManager.State.ACTIVE ->
                                        stringResource(R.string.subscription_status_active)
                                    LicenseManager.State.OFFLINE_GRACE ->
                                        stringResource(R.string.subscription_status_grace)
                                    else -> stringResource(R.string.subscription_status_inactive)
                                },
                                color =
                                    if (result.usable) MaterialTheme.colorScheme.primary
                                    else MaterialTheme.colorScheme.error,
                            )
                            TextButton(onClick = { editingId = true }) {
                                Text(stringResource(R.string.subscription_change_id))
                            }
                        }
                        error?.let {
                            Text(it, color = MaterialTheme.colorScheme.error)
                        }
                    }
                }

                Button(
                    onClick = {
                        TelegramIntents.openTelegramBot(this@SubscriptionGateActivity)
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text(stringResource(R.string.subscription_open_bot)) }

                OutlinedButton(
                    onClick = {
                        if (!editingId) lifecycleScope.launch { doRefresh() }
                    },
                    enabled = !checking && !editingId,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    if (checking) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(16.dp).padding(end = 8.dp),
                            strokeWidth = 2.dp,
                        )
                        Text(stringResource(R.string.subscription_checking))
                    } else {
                        Text(stringResource(R.string.subscription_check_now))
                    }
                }
            }
        }

        if (languageDialogVisible) {
            val selectedTag = AppLocaleManager.currentTag()
            AlertDialog(
                onDismissRequest = { languageDialogVisible = false },
                title = { Text(stringResource(R.string.language_dialog_title)) },
                text = {
                    LazyColumn {
                        item {
                            LanguageOptionRow(
                                title = stringResource(R.string.language_follow_system),
                                selected = selectedTag == null,
                                onClick = {
                                    languageDialogVisible = false
                                    AppLocaleManager.apply(null)
                                },
                            )
                        }
                        items(AppLocaleManager.supportedLocales, key = { it.languageTag }) { locale ->
                            LanguageOptionRow(
                                title = locale.nativeName,
                                selected = selectedTag == locale.languageTag,
                                onClick = {
                                    languageDialogVisible = false
                                    AppLocaleManager.apply(locale.languageTag)
                                },
                            )
                        }
                    }
                },
                confirmButton = {
                    TextButton(onClick = { languageDialogVisible = false }) {
                        Text(stringResource(R.string.cancel))
                    }
                },
            )
        }
    }

    @Composable
    private fun LanguageOptionRow(title: String, selected: Boolean, onClick: () -> Unit) {
        Row(
            modifier = Modifier.fillMaxWidth().clickable(onClick = onClick).padding(vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            RadioButton(selected = selected, onClick = onClick)
            Text(title, modifier = Modifier.padding(start = 8.dp))
        }
    }
}

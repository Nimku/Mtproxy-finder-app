package com.nimku.proxy.ui.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.SegmentedButton
import androidx.compose.material3.SegmentedButtonDefaults
import androidx.compose.material3.SingleChoiceSegmentedButtonRow
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.nimku.proxy.core.locale.AppLocaleManager

/**
 * One-tap language switcher for the app's core audience: no dropdown/dialog, so it also works for
 * someone who can't read the English word "Language" well enough to find a menu in the first
 * place. Deliberately limited to 4 languages (rather than all of [AppLocaleManager.supportedLocales])
 * to keep every label legible at this width; the full list is still reachable from Settings.
 */
private val QUICK_LANGUAGE_TAGS = listOf("ru", "en", "ar", "fa")

@Composable
fun QuickLanguageRow(modifier: Modifier = Modifier) {
    var current by remember { mutableStateOf(AppLocaleManager.currentTag() ?: "en") }
    val locales = remember {
        QUICK_LANGUAGE_TAGS.mapNotNull { tag ->
            AppLocaleManager.supportedLocales.firstOrNull { it.languageTag == tag }
        }
    }
    SingleChoiceSegmentedButtonRow(modifier = modifier.fillMaxWidth()) {
        locales.forEachIndexed { index, locale ->
            SegmentedButton(
                modifier = Modifier.weight(1f),
                selected = current == locale.languageTag,
                onClick = {
                    current = locale.languageTag
                    AppLocaleManager.apply(locale.languageTag)
                },
                shape = SegmentedButtonDefaults.itemShape(index, locales.size),
                label = { Text(locale.nativeName, maxLines = 1) },
            )
        }
    }
}

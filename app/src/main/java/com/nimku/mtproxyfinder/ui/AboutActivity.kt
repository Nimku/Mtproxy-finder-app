package com.nimku.mtproxyfinder.ui

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.nimku.mtproxyfinder.R
import com.nimku.mtproxyfinder.core.util.TelegramIntents
import com.nimku.mtproxyfinder.ui.components.channel.AboutChannelSection
import com.nimku.mtproxyfinder.ui.theme.MtproxyFinderTheme
import com.nimku.mtproxyfinder.ui.theme.mtSafeScreen

class AboutActivity : AppCompatActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MtproxyFinderTheme {
                Scaffold(
                    modifier = Modifier.mtSafeScreen(),
                    topBar = {
                        TopAppBar(
                            title = { Text(stringResource(R.string.about)) },
                            navigationIcon = {
                                IconButton(onClick = { finish() }) {
                                    Icon(
                                        Icons.AutoMirrored.Filled.ArrowBack,
                                        contentDescription = null,
                                    )
                                }
                            },
                        )
                    },
                ) { padding ->
                    Box(
                        modifier = Modifier.fillMaxSize().padding(padding),
                        contentAlignment = Alignment.TopCenter,
                    ) {
                        AboutChannelSection(
                            cardModifier = Modifier.padding(24.dp),
                            onOpen = { TelegramIntents.openTelegramChannel(this@AboutActivity) },
                        )
                    }
                }
            }
        }
    }
}


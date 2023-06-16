import json
from pathlib import Path
from typing import Optional

from discord import Locale
from discord.app_commands import (
    locale_str as _T,
    Translator,
    TranslationContext
)

from utils.lumberjack import get_lumberjack

log = get_lumberjack(__name__)


class SoybotTranslator(Translator):
    supported_locales = ('en-US', 'zh-TW')

    async def load(self):
        log.info('Loading translations...')
        self.translations: dict[str, dict] = dict()

        translations_dir = Path('./translations')
        for path in (p for p in translations_dir.glob('*.json')):
            with open(path, 'r', encoding='utf-8') as f:
                locale = path.stem
                self.translations[locale] = json.load(f)
            log.info(f'locale {locale} loaded')

    async def unload(self):
        del self.translations

    async def translate(
        self,
        string: _T,
        locale: Locale,
        context: TranslationContext
    ) -> Optional[str]:
        """
        `locale_str` is the string that is requesting to be translated
        `locale` is the target language to translate to
        `context` is the origin of this string, eg TranslationContext.command_name, etc
        This function must return a string (that's been translated), or `None` to signal no available translation available, and will default to the original.
        """

        log.info(context.data)

        msg = string.message
        locale = locale.value
        command_name = context.data.name
        location = context.location.name

        if locale not in self.supported_locales:
            return None

        log.info(f'Translaing: {msg} | {locale} | {location}')

        try:
            translated_str = self.translations[locale][location][msg]
            log.info(f'Translated: {translated_str}')
            return translated_str
        except KeyError as e:
            log.exception(e)
            log.info('Translation Failed')
            return None

# IMPORTANT! put this in your `setup_hook` function
# await bot.tree.set_translator(MyCustomTranslator())
# Optional, but helps save a lot of typing
# from discord.app_commands import locale_str as _T
# @app_commands.command(name=_T("bonk"))
# @app_commands.describe(user=_T("The user to bonk."))
# async def bonk(interaction: discord.Interaction, user: discord.User):
#   await interaction.response.send_message(f":hammer: {user.mention}")

import json
from pathlib import Path
from typing import Optional

from discord import app_commands as ac, Locale
from discord.app_commands import (
    locale_str as _T,
    Translator,
    TranslationContext,
    Command
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

        msg = string.message
        locale = locale.value
        origin = context.data
        location = context.location.name

        if locale not in self.supported_locales:
            return None

        try:
            if string.extras.get('shared'):
                return translations['shared'][msg]

            translations = self.translations[locale]['app_commands']

            if location == 'choice_name':
                command_name, choice = msg.split('_')
                res = translations[command_name][location][choice]
            elif location in (
                'command_name',
                'command_description',
                'group_name',
                'group_description'
            ):
                command_name = origin.name
                res = translations[command_name][location]
            elif location in (
                'parameter_name',
                'parameter_description'
            ):
                command_name = origin.command.name
                res = translations[command_name][location][msg]

            log.info(
                f'Translated: {msg} -> {res} | {locale} | {location}'
            )

            return res

        except (KeyError, AttributeError) as e:
            log.exception(
                f'Translation failed: {msg} | {locale} | {location} | {e}'
            )
            return None

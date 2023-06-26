import json
from pathlib import Path
from typing import Optional

from discord import app_commands as ac, Locale
from discord.app_commands import (
    locale_str as _T,
    Translator,
    TranslationContext,
)

from utils.lumberjack import get_lumberjack

log = get_lumberjack(__name__)


class SoybotTranslator(Translator):
    supported_locales = ('en-US', 'zh-TW')

    async def load(self):
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
        `context` is the origin of this string, 
            eg TranslationContext.command_name, etc
        ---
        This function must return a string (that's been translated), 
        or `None` to signal no available translation available, 
        and will default to the original.
        """
        if context.location.name == 'other':
            log.warning(f'{string} | {context} | {context.data}')

        locale = locale.value
        location = context.location.name
        if locale not in self.supported_locales:
            if location == 'other':
                locale = 'en-US'
            else:
                return None

        msg = string.message
        origin = context.data
        try:
            translations = self.translations[locale]

            if string.extras.get('shared'):
                res = translations['shared'][msg]
            else:
                translations = translations['app_commands']
                command_name, key = self._translation_resolution(
                    origin, location, msg
                )
                res = translations[command_name][location]
                if key is not None:
                    res = res[key]

            log.info(f'Translated: {msg} -> {res} | {locale} | {location}')
            return res

        except (KeyError, AttributeError, ValueError) as e:
            log.exception(
                f'Translation failed: {msg} | {locale} | {location} | {e}')
            return None

    def _translation_resolution(self, origin, location: str, message: str):
        if location in (
            'command_name',
            'command_description',
            'group_name',
            'group_description'
        ):
            command_name, key = origin.name, None
        elif location in ('parameter_name', 'parameter_description'):
            command_name, key = origin.command.name, message
        elif location == 'choice_name':
            command_name, key = message.split('_')
        elif location == 'other':
            command_name, key = origin.name, message
        else:
            raise ValueError('Unrecognized location')

        return command_name, key

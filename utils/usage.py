import abc

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from discord import Emoji, Sticker, Message, Reaction, Member

custom_emoji_regex = r'<(a?):([a-zA-Z0-9_]{2,32}):([0-9]{18,22})>'


class EmojiUsageType(Enum):
    IN_TEXT = "in_text"
    REACTION = "reaction"


@dataclass(slots=True)
class BaseUsage(abc.ABC):
    _item: Emoji | Sticker
    user_id: int
    channel_id: int
    message_id: int
    timestamp: datetime

    @property
    def id(self):
        return self._item.id

    @property
    def guild_id(self):
        return self._item.guild_id

    @property
    def name(self):
        return self._item.name


@dataclass(slots=True)
class EmojiUsage(BaseUsage):
    usage_type: EmojiUsageType

    @property
    def emoji(self) -> Emoji:
        return self._item

    @classmethod
    def from_in_text_emoji(cls, emoji: Emoji, msg: Message):
        return cls(
            _item=emoji,
            user_id=msg.author.id,
            channel_id=msg.channel.id,
            message_id=msg.id,
            timestamp=msg.created_at,
            usage_type=EmojiUsageType.IN_TEXT
        )

    @classmethod
    def from_on_reaction(cls, rxn: Reaction, user: Member):
        return cls(
            _item=rxn.emoji,
            user_id=user.id,
            channel_id=rxn.message.channel.id,
            message_id=rxn.message.id,
            timestamp=rxn.message.created_at,  # I'm assuming this is the correct timestamp
            usage_type=EmojiUsageType.REACTION
        )


@dataclass(slots=True)
class StickerUsage(BaseUsage):

    @property
    def sticker(self) -> Sticker:
        return self._item

    @classmethod
    def from_message(cls, msg: Message):
        return cls(
            _item=msg.stickers[0],  # I'm assuming this is the correct sticker
            user_id=msg.author.id,
            guild_id=msg.guild.id,
            channel_id=msg.channel.id,
            message_id=msg.id,
            timestamp=msg.created_at
        )

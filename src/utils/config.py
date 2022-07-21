import os
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()


@dataclass(frozen=True)
class Guild:
    id: int
    bot_nick: str = None
    bot_roles: tuple[str] | None = None


@dataclass(frozen=True)
class SoyReact():
    emoji_tags: tuple[str]
    count: int = 1
    activation_probability: float = 1.0


@dataclass(frozen=True)
class SoyReply():
    messages_pool: tuple[str]
    activation_probability: float = 1.0


@dataclass(frozen=True)
class User:
    id: int
    soy_reply: SoyReply = None
    soy_react: SoyReact = None


@dataclass(frozen=True)
class Emoji:
    # id if custom dc emoji, else str repr
    id: int | str
    tags: tuple[str]


class Config:
    TOKEN = os.environ.get('TOKEN')

    guilds = {'nthu': Guild(id=771595191638687784, bot_nick=None,
                            bot_roles={771595191638687784, 771681968886251543, 771675662531428374, 955800304492871741}),
              'debug': Guild(id=874556062815100938)}

    guild_ids = tuple(guild.id for guild in guilds.values())

    users = {
        'soymilk': User(
            id=202249480148353025,
            soy_react=SoyReact(emoji_tags=('soymilk', 'pineapplebun'),
                               activation_probability=0.1)),
        'gay_dog': User(
            id=284350778087309312,
            soy_react=SoyReact(emoji_tags=('disgusted',),
                               activation_probability=0.4)),
        'howard': User(
            id=613683023300395029,
            soy_react=SoyReact(emoji_tags=('wtf',),
                               activation_probability=0.3)),
        'ayu': User(
            id=557591275227054090,
            soy_react=SoyReact(emoji_tags=('gay',),
                               activation_probability=0.4)),
        'snow': User(
            id=565862991061581835,
            soy_react=SoyReact(emoji_tags=('gay',),
                               activation_probability=0.3)),
        'paper': User(
            id=402060040518762497,
            soy_react=SoyReact(emoji_tags=('gay',),
                               activation_probability=0.3)),
        'feilin': User(
            id=388739972343267329,
            soy_react=SoyReact(emoji_tags=('feilin',),
                               activation_probability=0.3)),
        'shili': User(
            id=777196949903376396,
            soy_react=SoyReact(emoji_tags=('pineapplebun',),
                               activation_probability=0.3)),
        # 'carl_bot': User(
        #     id=235148962103951360,
        #     soy_react=SoyReact(emoji_tags=('gay',),
        #                        activation_probability=0.1)),
    }

    emojis = {
        'bulbasaur': Emoji(931022665790144542,
                           ('wtf', 'soymilk')),
        'detective_dog': Emoji(953983783995068436, ('angry', 'dog')),
        'notangry_dog': Emoji(976082704275763210, ('sad', 'dog')),
        'party_dog': Emoji(976082704275763210, ('party', 'dog')),
        'gay_lao': Emoji(786891103722930206, ('gay', 'ayu', 'snow', 'paper')),
        'kekw': Emoji(778670717784293386, ('lol',)),
        'pineapplebun': Emoji(956009591374741575, ('pineapplebun',)),
        'watson_drive': Emoji(791299125114568764, ('feilin',)),
        'aqua_cry': Emoji(823469189493686272, ('feilin',)),
        'fubuki': Emoji(823469218648948746, ('feilin',)),
        'miko': Emoji(823469253923569686, ('feilin',)),
        'pekora': Emoji(802139497567223808, ('feilin',)),

        'joy': Emoji('😂', ('lol')),
        'nauseated_face': Emoji('🤢', ('gay_dog', 'disgusted')),
        'face_vomitting': Emoji('🤮', ('gay_dog', 'disgusted')),
        'partying_face': Emoji('🥳', ('party',)),
        'grinning': Emoji('😀', ('feilin',))
    }

    emoji_ids_by_tag = {}

    # keywords_responses = (
    #     (('甲', '阿玉', '阿衡', '阿雪', '雪夜', '紙袋', '袋袋',
    #      '阿袋', 'ayu'), (SoyReact(0.3, 1, ['gay']))),
    # )

    @staticmethod
    def get_action_by_user_id(id: int) -> tuple[SoyReact | None, SoyReply | None] | None:
        return next(
            ((u.soy_react, u.soy_reply)
             for u in Config.users.values() if id == u.id), (None, None)
        )

    @staticmethod
    def get_emoji_ids_by_tags(*tags):
        result_emoji_ids = []

        for t in tags:
            if t not in Config.emoji_ids_by_tag:
                Config.emoji_ids_by_tag[t] = [
                    e.id for e in Config.emojis.values() if t in e.tags
                ]
            result_emoji_ids += Config.emoji_ids_by_tag[t]

        return result_emoji_ids

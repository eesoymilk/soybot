import os
from dotenv import load_dotenv
from dataclasses import dataclass


load_dotenv()


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

    guilds = {
        'nthu': 771595191638687784,
        'debug': 874556062815100938,
        'trap_lovers': 202599307755388929,
        'lanm': 1010521652079120384,
    }

    guild_ids = [id for id in guilds.values()]

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
        'dodo': User(
            id=618679878144753664,
            soy_react=SoyReact(emoji_tags=('dodo',),
                               activation_probability=0.3)),
    }

    emojis = {
        'bulbasaur': Emoji(931022665790144542,
                           ('wtf', 'soymilk')),

        'angry_dog': Emoji(946700998024515635, ('angry', 'dog', 'dog_bundle')),
        'sleeping_dog': Emoji(991677470216552620, ('angry', 'dog', 'dog_bundle', 'sleeping')),
        'detective_dog': Emoji(953983783995068436, ('angry', 'dog', 'dog_bundle', 'detective')),
        'notangry_dog': Emoji(976082704275763210, ('sad', 'dog', 'dog_bundle')),
        'cowboy_dog': Emoji(991677468794703914, ('party', 'dog', 'dog_bundle')),
        'starburst_dog': Emoji(991676592533295164, ('party', 'dog', 'dog_bundle')),
        'rainbow_dog': Emoji(991676465764638810, ('a', 'party', 'dog', 'dog_bundle')),
        'shaking_dog': Emoji(991676443174129764, ('a', 'shaking', 'party', 'dog', 'dog_bundle')),

        'party_dog': Emoji(930768322226716672, ('party', 'dog', 'dog_bundle')),


        'gay_lao': Emoji(786891103722930206, ('gay', 'ayu', 'snow', 'paper')),
        'kekw': Emoji(778670717784293386, ('lol',)),
        'pineapplebun': Emoji(956009591374741575, ('pineapplebun',)),
        'watson_drive': Emoji(791299125114568764, ('feilin',)),
        'aqua_cry': Emoji(823469189493686272, ('feilin',)),
        'fubuki': Emoji(823469218648948746, ('feilin',)),
        'miko': Emoji(823469253923569686, ('feilin',)),
        'pekora': Emoji(802139497567223808, ('feilin',)),
        'watson_eat_sand': Emoji(793809340997828609, ('feilin',)),

        'joy': Emoji('😂', ('lol')),
        'nauseated_face': Emoji('🤢', ('gay_dog', 'disgusted')),
        'face_vomitting': Emoji('🤮', ('gay_dog', 'disgusted')),
        'partying_face': Emoji('🥳', ('party',)),
        'grinning': Emoji('😀', ('feilin',)),

        'flushed_face': Emoji('😳', ('dodo',)),
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

from dataclasses import dataclasses

import discord


@dataclasses()
class Guild:
    id: int
    bot_roles: tuple[str]


@dataclasses()
class SoyResponse:
    activation_probability: float


@dataclasses()
class SoyReact(SoyResponse):
    count: int
    emoji_tags: tuple[str]


@dataclasses()
class SoyReply(SoyResponse):
    messages_pool: tuple[str]


@dataclasses()
class User:
    id: int
    soy_reply: SoyReply
    soy_react: SoyReact


@dataclasses()
class Emoji:
    id: int | str
    tags: tuple[str]


class Config:
    guilds = {'nthu': Guild(id=771595191638687784,
                            bot_roles={771595191638687784, 771681968886251543, 771675662531428374, 955800304492871741}),
              'debug': Guild(id=874556062815100938)}

    users = {
        'soymilk': User(id=202249480148353025),
        'howard': User(id=613683023300395029),
        'snow': User(id=565862991061581835),
        'paper': User(id=402060040518762497),
        'gay_dog': User(id=284350778087309312),
        'feilin': User(id=388739972343267329),
        'carl_bot': User(id=235148962103951360),
    }

    emojis = {
        'wtf': Emoji(848135201439612978, ('wtf', 'soymilk')),
        'bulbasaur': Emoji(931022665790144542, ('wtf', 'soymilk')),
        'detective_dog': Emoji(953983783995068436, ('angry', 'dog')),
        'notangry_dog': Emoji(976082704275763210, ('sad', 'dog')),
        'party_dog': Emoji(976082704275763210, ('party', 'dog')),
        'gay_lao': Emoji(786891103722930206, ('gay', 'ayu', 'snow', 'paper')),
        'kekw': Emoji(778670717784293386, ('lol',)),
        'pineapplebun': Emoji(956009591374741575, ('pineapplebun',)),

        'joy': Emoji('😂', ('lol')),
        'nauseated_face': Emoji('🤢', ('gay_dog', 'disgusted')),
        'face_vomitting': Emoji('🤮', ('gay_dog', 'disgusted')),
        'partying_face': Emoji('🥳', ('party',))
    }

    # keywords_responses = (
    #     (('甲', '阿玉', '阿衡', '阿雪', '雪夜', '紙袋', '袋袋',
    #      '阿袋', 'ayu'), (SoyReact(0.3, 1, ['gay']))),
    # )

    @property
    def guild_ids(self):
        return [guild.id for guild in self.guilds.values()]

    def emoji_ids_by_tags(cls, *tags):
        return [e.id for e in cls.emojis.values()
                if any([t in e.tags for t in tags])]


emojis = {
    'angry_dog':
        [953983783995068436,
         946700998024515635,
         991677468794703914,
         991676465764638810,
         991676443174129764,
         991677470216552620,
         991676592533295164],
    'wtf': [931022665790144542, 848135201439612978],
    'ayu': [994198292382634025, 989934658454183946],
    'gay': [786891103722930206],
    'fuck': [958223671779024950],
    'heart': [955830885448564776, ],
    'sad': [847493674664460329],
    'feilin_set': [823469218648948746, 823469253923569686, 802139497567223808, 804392022172499999, 791299125114568764, '😀'],
}

keywords = {
    'gay': ['甲', '阿玉', '阿欲', '阿郁', '阿衡', '阿雪', '雪夜', '紙袋', '袋袋', '阿袋', 'ayu'],
}

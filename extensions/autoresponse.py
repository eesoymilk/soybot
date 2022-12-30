import discord
import re
import asyncio
from emoji import emoji_list
from dataclasses import dataclass
from discord import app_commands
from discord.ext import commands
from random import random, choice
from datetime import datetime
from utils import get_lumberjack

log = get_lumberjack(__name__)
loaded = False
custom_emoji_regex = r'<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):\b(?P<id>[0-9]{18,22})\b>'


@dataclass(frozen=True)
class Response():
    rate: float
    responses: list[str]


# type aliasing
AuthorResponses = dict[int, Response]
KeywordResponses = tuple[tuple[str], Response]

# # global caches
# guild_author_reactions: dict[int, AuthorResponses] = dict()
# guild_author_replies: dict[int, AuthorResponses] = dict()

# TODO: Command to add new auto replies
# TODO: Message.content -> react
# TODO: Message.content -> reply


async def emojis_to_str(
    reactions: list[str | int],
    guild: discord.Guild
) -> list[str]:
    emoji_strs = []
    for reaction in reactions:
        if isinstance(reaction, str):
            emoji_strs.append(reaction)
            continue

        try:
            emoji_strs.append(str(await guild.fetch_emoji(reaction)))
        except:
            print(reaction)

    return emoji_strs


async def fetch_author_responses(
    bot: commands.Bot,
    guild: discord.Guild = None
) -> None:

    # fetch all
    if guild is None:
        await asyncio.gather(*[
            fetch_author_responses(bot, g)
            for g in bot.guilds if g.id not in bot.author_reactions
        ])
        return

    # already fetched
    if guild.id in bot.author_reactions:
        return

    # fetch for a guild
    collection = bot.db.authorReactions
    query = {'guildId': guild.id}
    if await collection.count_documents(query) == 0:
        return

    bot.author_reactions[guild.id] = {
        feed['authorId']:
        Response(
            feed['rate'],
            await emojis_to_str(
                feed['responses'],
                guild
            )
        )
        async for feed in collection.find(query).sort('rate', -1)
    }


def extract_emojis(content: str) -> list[str | int]:
    unicode_emojis = {emoji['emoji'] for emoji in emoji_list(content)}
    custom_emoji_ids = {
        int(matches[2]) for matches in re.findall(custom_emoji_regex, content)
    }
    return list(unicode_emojis | custom_emoji_ids)


class AutoResponseCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        log.info('cog initialized')

    @commands.Cog.listener(name='on_message')
    async def react_author(self, message: discord.Message):
        if message.author.bot:
            return

        await fetch_author_responses(self.bot, message.guild)

        reaction = self.bot.author_reactions[message.guild.id].get(
            message.author.id)
        if reaction is None or reaction.rate < random():
            return

        try:
            await message.add_reaction(choice(reaction.responses))
        except:
            ...

    # @commands.Cog.listener(name='on_message')
    # async def reply_author(self, message: discord.Message):
    #     guild_id = message.guild.id
    #     if guild_id not in guild_author_replies:
    #         collection = self.bot.db.authorReplies
    #         if await collection.count_documents({'guildId': guild_id}) == 0:
    #             return

    #         async for feed in collection.find({'guildId': guild_id}):
    #             cache_author_replies(
    #                 feed['guildId'],
    #                 feed['authorId'],
    #                 feed['rate'],
    #                 feed['responses'],
    #             )

    #     reply = guild_author_replies[guild_id].get(message.author.id)
    #     if reply is not None and reply.rate > random():
    #         await message.reply(choice(reply.responses))

    @commands.Cog.listener(name='on_message')
    async def debugging_listener(self, message: discord.Message):
        guild_id = message.guild.id
        if guild_id != 874556062815100938 or message.author.id == self.bot.user.id:
            return

    @commands.Cog.listener(name='on_message')
    async def reply_keyword(self, message: discord.Message):
        guild_id = message.guild.id


class AutoResponseGroup(app_commands.Group, name='soyfeed'):

    @app_commands.command(name='新的自動按表情', description='讓豆漿ㄐㄐ人幫你按表情吧！')
    @app_commands.describe(author='群裡指定一個人', emojis_str='要按甚麼表情呢？', rate='請輸入0~1的浮點數')
    @app_commands.rename(author='按表情對象', emojis_str='反映表情', rate='觸發機率')
    @app_commands.check(
        lambda interaction:
            interaction.user.id == 202249480148353025
    )
    async def new_autoreact(
        self,
        interaction: discord.Interaction,
        author: discord.Member,
        emojis_str: str,
        rate: float = None,
    ):
        await interaction.response.defer()
        await fetch_author_responses(interaction.client, interaction.guild)

        unicode_emojis = {emoji['emoji'] for emoji in emoji_list(emojis_str)}
        custom_emojis_parts = re.findall(custom_emoji_regex, emojis_str)
        custom_emojis_ids = {int(parts[2]) for parts in custom_emojis_parts}

        guild_author_reactions = interaction.client.author_reactions[interaction.guild.id]
        collection = interaction.client.db.authorReactions
        query = {
            'authorId': author.id,
            'guildId': interaction.guild.id,
        }

        # insert
        if guild_author_reactions is None or guild_author_reactions.get(author.id) is None:
            await collection.insert_one(query | {
                'responses': list(unicode_emojis | custom_emojis_ids),
                'rate': rate if rate is not None else 0.3,
            })

        # update
        else:
            document = {
                '$addToSet': {
                    'responses': {
                        '$each': list(unicode_emojis | custom_emojis_ids)
                    }
                }
            }
            if rate is not None:
                document['$set'] = {'rate': rate}
            await collection.find_one_and_update(query, document)

        await interaction.followup.send(f'**已成功幫 {author.display_name} 加上自動按表情服務**\n表情一覽: {emojis_str} (觸發機率{rate if rate is not None else 0.3})')
        await fetch_author_responses(interaction.client, interaction.guild)

    @app_commands.command(name='自動表情一覽', description='看看豆漿ㄐㄐ人幫誰按表情吧！')
    # @app_commands.describe(sneak='選是的話則只有你看的到')
    # @app_commands.rename(sneak='偷偷看')
    @app_commands.check(
        lambda interaction:
            interaction.user.id == 202249480148353025
    )
    async def check_autoreact(
        self,
        interaction: discord.Interaction,
    ):
        await interaction.response.defer()
        await fetch_author_responses(interaction.client, interaction.guild)

        embed = discord.Embed(
            title='eeSoybot 自動表情受害者清單',
            color=interaction.client.user.color,
            timestamp=datetime.now(),
        ).set_thumbnail(
            url=interaction.client.user.display_avatar
        ).set_footer(
            text=f'以上名單只在 {interaction.guild.name} 有效',
            icon_url=interaction.guild.icon,
        )

        for k, v in interaction.client.author_reactions[interaction.guild.id].items():
            embed.add_field(
                name=f'{interaction.guild.get_member(k).display_name} : {str(v.rate * 100).rstrip("0").rstrip(".")}%',
                value=' '.join(v.responses),
                inline=False
            )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoResponseCog(bot))
    bot.tree.add_command(AutoResponseGroup())
    log.info('loaded')

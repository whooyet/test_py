import discord, os
import pymysql
from distutils.sysconfig import PREFIX
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()


TOKEN = os.environ['TOKEN']

PHOST = os.environ['PHOST']
PUSER = os.environ['PUSER']
PPS = os.environ['PPS']
PPORT = os.environ['PPORT']
PDB = os.environ['PDB']

db = pymysql.connect(host=PHOST, user=PUSER, password=PPS, port=int(PPORT), database=PDB, charset='utf8')
cursor = db.cursor()
try:
    cursor.execute("CREATE TABLE user_info (name char(30), nickname char(30))")
except pymysql.err.OperationalError as e:
    if e.args[0] == 1050:  # Table already exists
        pass  # do nothing
    else:
        raise e 


intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}.')


@client.command(name='구인')
async def aa(ctx, arg, *arg2):
    voice_channel = ctx.author.voice

    if voice_channel is None:
        await ctx.channel.send("먼저 음성 채널에 들어가주세요.")
    else:
        aa = ctx.author.voice.channel
        #invite = await aa.create_invite(unique=False, max_uses=100)

        parameter = ' '.join(arg2)
        members = ctx.author.voice.channel.members

        embed=discord.Embed(title=f"{arg}", description=f"{ctx.author.mention} 님이 구인중")
        embed.add_field(name="채널명", value=f"{aa.mention}", inline=True)
        embed.add_field(name="맴버", value=f"{len(members)}명", inline=True)
        embed.set_footer(text=f"{parameter}")

        await ctx.message.delete()
        await ctx.send(embed=embed)
        #await embed.add_reaction('👍')

@aa.error
async def aa_error(ctx, error):
    print(f'구인 {error}')
    await ctx.send(f"!구인 할말 추가할말")

@client.command(name='저장')
async def usave(ctx, arg):
    user_id = ctx.author.id

    cursor.execute("SELECT * FROM user_info WHERE name = %s", (str(user_id),))
    result = cursor.fetchone()
    if result:
        cursor.execute("UPDATE user_info SET nickname = %s", (arg), )
        await ctx.send(f'서버에 닉네임이 업데이트되었습니다. ({arg})')
        db.commit()
    else:
        save_nickname(user_id, arg)
        await ctx.send('서버에 저장이되었습니다.')

@usave.error
async def usave_error(ctx, error):
    print(f'저장 {error}')
    await ctx.send(f"!저장 닉네임")


# 닉네임 저장
def save_nickname(niname, nickname):
    sql = "INSERT INTO user_info (name, nickname) VALUES (%s, %s)"
    cursor.execute(sql, (niname, nickname))
    db.commit()

@client.command(name='정보')
async def uload(ctx, member: discord.Member):
    user_id = member.id
    sql = "SELECT nickname FROM user_info WHERE name = %s"
    cursor.execute(sql, (str(user_id),))
    result = cursor.fetchone()
    if result:
        await ctx.send(f'닉네임: {result[0]}')
    else:
        await ctx.send('정보를 찾을 수 없습니다.')

@uload.error
async def uload_error(ctx, error):
    print(f'정보 {error}')
    await ctx.send(f"!정보 멘션")

@client.command(name='이건알기가정말힘들지몰라하지만난멋있어')
async def uload(ctx):
    await ctx.message.delete()
    cursor.execute("SELECT * FROM user_info ORDER BY name")
    result = cursor.fetchall()

    for row in result:
        user_id = row[0]  # 유저의 고유 ID를 가져옴
        nickname = row[1]
        user = await client.fetch_user(user_id)
        await ctx.send(f"{user.name}#{user.discriminator}: {nickname}")

#cursor.close()

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass


try:
    client.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")

import base64
import json
import os
import random
from random import randint
import re
import signal
import sys
import urllib.parse
import datetime
import youtube_dl
from urllib import parse, request

import discord
from discord.ext import commands
import youtube_dl
import os

from PIL import Image
import requests
import discord
from discord.ext import commands

if "TOKEN_DISCORD" in os.environ:
    TOKEN_DISCORD = os.environ['TOKEN_DISCORD']
elif len(sys.argv) >= 2:
    TOKEN_DISCORD = sys.argv[1]
elif os.path.isfile('token_discord.txt'):
    TOKENFILE = open('token_discord.txt', 'r')
    TOKEN_DISCORD = TOKENFILE.read()
    TOKENFILE.close()
else:
    print('Please provide a token')
    sys.exit(1)

BOT = commands.Bot(command_prefix='!', case_insensitive=True)

BOT.remove_command("help")

LISTENING = ['...']
PLAYING = ['CS:GO, Life, Fortnite']
WATCHING = ['...']
ACTIVITYTYPE = {'LISTENING': discord.ActivityType.listening,
                'PLAYING': discord.ActivityType.playing,
                'WATCHING': discord.ActivityType.watching}
PRESENCELISTS = ['LISTENING', 'PLAYING', 'WATCHING']
PRESENCE = random.choice(PRESENCELISTS)

INFO = open('commands.md', 'r')
INFOTEXT = INFO.read()
INFO.close()


@BOT.event
async def on_ready():
    # Сообщение о запуске
    print('Bot 1.0')
    print('Загружен как: ' + BOT.user.name)
    print('Клиент ID : ' + str(BOT.user.id))
    await BOT.change_presence(activity=discord.Activity(
        type=ACTIVITYTYPE[PRESENCE], name=(random.choice(globals()[PRESENCE]) + ' | !info')))


def sigterm_handler():
    BOT.logout()
    print('Выключение...')
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)


@BOT.command(helpinfo='Информация о боте', aliases=['help', 'about'])
async def info(ctx):
    # Выводит информацию о боте
    await ctx.send(INFOTEXT)


@BOT.command(helpinfo='xD, !kill username#0000')
async def kill(ctx, *, user='You'):
    await ctx.send((user) + ' выпал из мира')


@BOT.command(helpinfo='Выбор рандомного числа из списка | !choose int:numbers')
async def choose(ctx, *choices: str):
    # Выбор рандомного числа из предложенного списка
    await ctx.send((random.choice(choices)))


@BOT.command(helpinfo='Повторят все что напишешь | !echo text')
async def echo(ctx, *, message):
    # Воспроезведет все что напишешь
    await ctx.send(message)


@BOT.command(helpinfo='Кик с сервера | !kick username#0000')
async def kick(ctx, usr: discord.Member, *, rsn=''):
    # Кик пользователя с сервера
    try:
        if ctx.author.guild_permissions.kick_members:
            await usr.kick(reason='Кем кикнут: {}, Причина: {}'
                           .format('{}#{}'
                                   .format(ctx.author.name,
                                           ctx.author.discriminator)
                                   , rsn))
            await ctx.send(file=discord.File('WhatAreYouDoingInMySwamp.gif'))
        else:
            await ctx.send('Извините, у вас нет на это разрешения')
    except discord.errors.Forbidden:
        await ctx.send('Извините, но у меня нет на это разрешения')


@BOT.command(helpinfo='Рандомный цвет', aliases=['hex', 'colour'])
async def color(ctx, inputcolor=''):
    # Скидывает в чат андомный цвет
    if inputcolor == '':
        randgb = lambda: random.randint(0, 255)
        hexcode = '%02X%02X%02X' % (randgb(), randgb(), randgb())
        rgbcode = str(tuple(int(hexcode[i:i + 2], 16) for i in (0, 2, 4)))
        await ctx.send('`Hex: #' + hexcode + '`\n`RGB: ' + rgbcode + '`')
        heximg = Image.new("RGB", (64, 64), '#' + hexcode)
        heximg.save("color.png")
        await ctx.send(file=discord.File('color.png'))
    else:
        if inputcolor.startswith('#'):
            hexcode = inputcolor[1:]
            if len(hexcode) == 8:
                hexcode = hexcode[:-2]
            elif len(hexcode) != 6:
                await ctx.send('Убедитесь, что код имеет этот формат: `#7289DA`')
            rgbcode = str(tuple(int(hexcode[i:i + 2], 16) for i in (0, 2, 4)))
            await ctx.send('`Hex: #' + hexcode + '`\n`RGB: ' + rgbcode + '`')
            heximg = Image.new("RGB", (64, 64), '#' + hexcode)
            heximg.save("color.png")
            await ctx.send(file=discord.File('color.png'))
        else:
            await ctx.send('Убедитесь, что код имеет этот формат: `#7289DA`')


@BOT.command(helpinfo='Ping')
async def ping(ctx):
    # Проверка пинга
    await ctx.send("🏓 Pong: **{}ms**".format(round(BOT.latency * 1000, 2)))


@BOT.command(helpinfo='Игра на удачу', aliases=['roll', 'random'])
async def dice(ctx, number=6):
    # Выбирает случайное число от 1 до числа

    await ctx.send("You rolled a __**{}**__!".format(randint(1, number)))


@BOT.command(helpinfo='Поиск в гугле (и картинок)', aliases=['search'])
async def google(ctx, *, searchquery: str):
    # Запрос в гугл
    searchquerylower = searchquery.lower()
    if searchquerylower.startswith('images '):
        await ctx.send('<https://www.google.com/search?tbm=isch&q={}>'
                       .format(urllib.parse.quote_plus(searchquery[7:])))
    else:
        await ctx.send('<https://www.google.com/search?q={}>'
                       .format(urllib.parse.quote_plus(searchquery)))


@BOT.command(helpinfo='Вывод текста смайликами букв')
async def emojify(ctx, *, text: str):
    # Вывод текста смайликами букв
    author = ctx.message.author
    emojified = '⬇ Скопируйте и вставьте: ⬇\n'
    formatted = re.sub(r'[^A-Za-z ]+', "", text).lower()
    if text == '':
        await ctx.send('Не забудьте написать, что вы хотите конвертировать!')
    else:
        for i in formatted:
            if i == ' ':
                emojified += '     '
            else:
                emojified += ':regional_indicator_{}: '.format(i)
        if len(emojified) + 2 >= 2000:
            await ctx.send('Ваше сообщение имеет больше 2000 символов!')
        if len(emojified) <= 25:
            await ctx.send('Ваше сообщение не может быть сконвертировано')
        else:
            await author.send('`' + emojified + '`')


@BOT.command(helpinfo='Скрывает текст')
async def spoilify(ctx, *, text: str):
    # Скрывает текст
    author = ctx.message.author
    spoilified = '⬇ Скопируйте и вставьте: ⬇\n'
    if text == '':
        await ctx.send('Remember to say what you want to convert!')
    else:
        for i in text:
            spoilified += '||{}||'.format(i)
        if len(spoilified) + 2 >= 2000:
            await ctx.send('Ваше сообщение имеет больше 2000 символов!')
        if len(spoilified) <= 4:
            await ctx.send('Ваше сообщение не может быть сконвертировано')
        else:
            await author.send('`' + spoilified + '`')


@BOT.command(helpinfo='Клонирование слов')
async def clone(ctx, *, message):
    # Клонирование слов
    pfp = requests.get(ctx.author.avatar_url_as(format='png', size=256)).content
    hook = await ctx.channel.create_webhook(name=ctx.author.display_name,
                                            avatar=pfp)

    await hook.send(message)
    await hook.delete()


@BOT.command(helpinfo='Поиск видео на YouTube', aliases=['yt'])
async def youtube(ctx, *, search):
    # Поиск видео на YouTube
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
    search_results = re.findall(r'/watch\?v=(.{11})', html_content.read().decode())
    print(search_results)
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[1])


@BOT.command(helpinfo='Кто создал бота?')
async def owner(ctx):
    # Кто создал бота?
    await ctx.send('Мой создатель: `JusT#6854`')


@BOT.command(helpinfo='Поиск на Википедии', aliases=['w', 'wiki'])
async def wikipedia(ctx, *, query: str):
    # Поиск на Википедии
    sea = requests.get(
        ('https://en.wikipedia.org//w/api.php?action=query'
         '&format=json&list=search&utf8=1&srsearch={}&srlimit=5&srprop='
         ).format(query)).json()['query']

    if sea['searchinfo']['totalhits'] == 0:
        await ctx.send('Нет данных по вашему запросу')
    else:
        for x in range(len(sea['search'])):
            article = sea['search'][x]['title']
            req = requests.get('https://en.wikipedia.org//w/api.php?action=query'
                               '&utf8=1&redirects&format=json&prop=info|images'
                               '&inprop=url&titles={}'.format(article)).json()['query']['pages']
            if str(list(req)[0]) != "-1":
                break
        else:
            await ctx.send('Нет данных по вашему запросу')
            return
        article = req[list(req)[0]]['title']
        arturl = req[list(req)[0]]['fullurl']
        artdesc = requests.get('https://en.wikipedia.org/api/rest_v1/page/summary/' + article).json()['extract']
        lastedited = datetime.datetime.strptime(req[list(req)[0]]['touched'], "%Y-%m-%dT%H:%M:%SZ")
        embed = discord.Embed(title='**' + article + '**', url=arturl, description=artdesc, color=0x3FCAFF)
        embed.set_footer(text='Wiki entry last modified',
                         icon_url='https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png')
        embed.set_author(name='Wikipedia', url='https://en.wikipedia.org/',
                         icon_url='https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png')
        embed.timestamp = lastedited
        await ctx.send('**Результат поиска для:** ***"{}"***:'.format(query), embed=embed)


@BOT.command(helpinfo='Ищет последовательность чисел', aliases=['numbers', 'integers'])
async def oeis(ctx, *, number: str):
    # Ищет последовательность чисел
    req = requests.get('https://oeis.org/search?q={}&fmt=json'.format(number)).json()['results'][0]
    numid = 'A' + str(req['number']).zfill(6)
    embed = discord.Embed(title='**' + numid + '**', url='https://oeis.org/{}'.format(numid),
                          description='**' + req['name'] + '**', color=0xFF0000)
    embed.add_field(name="Numbers:", value=str(req['data']), inline=False)
    embed.set_image(url='https://oeis.org/{}/graph?png=1'.format(numid))
    embed.set_thumbnail(url='https://oeis.org/oeis_logo.png')
    embed.set_footer(text='OEIS', icon_url='https://oeis.org/oeis_logo.png')
    embed.set_author(name='OEIS.org', url='https://oeis.org/', icon_url='https://oeis.org/oeis_logo.png')
    embed.timestamp = datetime.datetime.utcnow()
    await ctx.send('**Результат поиска для:** ***{}...***'.format(number), embed=embed)


@BOT.command(helpinfo='Прослушать видос, через войс чат')
async def play(ctx, url: str):
    # Прослушать видос, через войс чат
    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
    except PermissionError:
        await ctx.send("Подождите пока закнчится текущее проигрываение или напишите команду !stop")
        return

    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name='General')
    await voiceChannel.connect()
    voice = discord.utils.get(BOT.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            os.rename(file, "song.mp3")
    voice.play(discord.FFmpegPCMAudio("song.mp3"))


@BOT.command(helpinfo='Остановка')
async def stop(ctx):
    # Остановка
    voice = discord.utils.get(BOT.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()
    else:
        await ctx.send("Бот не подключен к голосовому каналу")


@BOT.command(helpinfo='Пауза')
async def pause(ctx):
    # Пауза
    voice = discord.utils.get(BOT.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Видео не воспроизводится")


@BOT.command(helpinfo='Продолжить воспроезведение')
async def resume(ctx):
    # Продолжить воспроезведение
    voice = discord.utils.get(BOT.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Видео не на паузе")

@BOT.command(helpinfo='сумма двух чисел')
async def sum(ctx, numOne: int, numTwo: int):
    # сумма двух чисел
    await ctx.send(numOne + numTwo)

BOT.run(TOKEN_DISCORD)

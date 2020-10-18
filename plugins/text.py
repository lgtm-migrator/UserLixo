import asyncio
from config import cmds

from pyrogram import Client, filters


@Client.on_message(filters.command("text", prefixes=".") & filters.me)
async def text(client, message):
    ch = ''
    txt = message.text.split(' ', 1)[1]
    ms = await message.edit('`|`')
    for i in txt:
        ch += i
        ms = await ms.edit(f'`{ch}|`')
        await asyncio.sleep(0.1)
        ms = await ms.edit(f'`{ch.strip()}`')
        await asyncio.sleep(0.1)

cmds.update({'.text':'Show text being typed'})

from pyrogram_mod import Client, Filters

from config import cmds

import desciclopedia
import wikipedia

@Client.on_message(Filters.command("dwiki", prefixes='.') & Filters.me)
async def dwiki(client, message):
    txt = message.text[7:]
    a = desciclopedia.search(txt)
    a = desciclopedia.page(a[0])
    await message.edit(f'[{a.title}]({a.url}):\n\n{a.content[:910]+"..."}')


@Client.on_message(Filters.command("wiki", prefixes='.') & Filters.me)
async def wiki(client, message):
    txt = message.text[6:]
    a = wikipedia.search(txt)
    wikipedia.set_lang('pt')
    a = wikipedia.page(a[0])
    await message.edit(f'[{a.title}]({a.url}):\n\n{a.content[:910]+"..."}')

cmds.update({'.wiki':'Search meaning of a word on wikipedia',
             '.dwiki':'Search meaning of a word on desciclopedia'})

import os
import time

import httpx
from pyrogram import Client, filters

from plugins.kibe import resize_photo


def emoji(x):
    txt = x.encode("unicode-escape").decode()
    res = ""
    print(txt.split("\\"))
    for i in txt.split("\\")[1:]:
        if "U" in i:
            i = "u" + i[4:]
        res += i + "-"
    return res[:-1]


@Client.on_message(filters.command("emojimix", prefixes=".") & filters.me)
async def emojimix(client, message):
    text = message.text.split(" ", 1)[1].split("+")
    emoji1, emoji2 = emoji(text[0]), emoji(text[1])
    ctime = time.time()
    cod = 20210218 if "-" in emoji1 or "-" in emoji2 else 20201001
    async with httpx.AsyncClient() as session:
        im1 = f"https://www.gstatic.com/android/keyboard/emojikitchen/{cod}/{emoji1}/{emoji1}_{emoji2}.png"
        im2 = f"https://www.gstatic.com/android/keyboard/emojikitchen/{cod}/{emoji2}/{emoji2}_{emoji1}.png"
        if (await session.head(im1)).headers.get("content-type") == "image/png":
            im = im1
        elif (await session.head(im2)).headers.get("content-type") == "image/png":
            im = im2
        else:
            await message.edit("These emojis cannot be combined.")
            return
        r = await session.get(im)
        with open(f"{ctime}.png", "wb") as f:
            f.write(r.read())
    photo = await resize_photo(f"{ctime}.png", ctime)
    await message.delete()
    await client.send_document(
        message.chat.id,
        photo,
        reply_to_message_id=None
        if not message.reply_to_message
        else message.reply_to_message.message_id,
    )
    os.remove(photo)
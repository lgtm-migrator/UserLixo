# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from userlixo.database import Message


@Client.on_inline_query(filters.sudoers & filters.regex("^(?P<index>\d+)"))
async def on_index(c: Client, iq: InlineQuery):
    index = int(iq.matches[0]["index"])
    message = await Message.get_or_none(key=index)
    if not message:
        results = [
            InlineQueryResultArticle(
                title="undefined index",
                input_message_content=InputTextMessageContent(
                    f"Undefined index {index}"
                ),
            )
        ]
        return await iq.answer(results, cache_time=0)

    keyboard = ikb(message.keyboard)
    text = message.text

    results = [
        InlineQueryResultArticle(
            title="index",
            input_message_content=InputTextMessageContent(
                text, disable_web_page_preview=True
            ),
            reply_markup=keyboard,
        )
    ]

    await iq.answer(results, cache_time=0)
    await (await Message.get(key=message.key)).delete()

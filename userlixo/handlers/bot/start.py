# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from typing import Union

from pyrogram import Client, filters
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message


@Client.on_message(filters.sudoers & filters.regex("^/start$"))
async def on_start_m(c: Client, m: Message):
    await on_start_u(c, m)


async def on_start_u(c: Client, u: Union[Message, CallbackQuery]):
    is_query = hasattr(u, "data")
    lang = u._lang
    keyb = ikb(
        [
            [(lang.upgrade, "upgrade"), [lang.restart, "restart"]],
            [(lang.commands, "list_commands 0"), (lang.plugins, "list_plugins")],
            [(lang.help, "help"), (lang.settings, "settings")],
        ]
    )
    text = lang.start_text
    kwargs = {}
    if not is_query:
        kwargs["quote"] = True
    await (u.edit if is_query else u.reply)(text, keyb, **kwargs)


@Client.on_callback_query(filters.sudoers & filters.regex("^start"))
async def on_start_cb(c: Client, cq: CallbackQuery):
    await on_start_u(c, cq)

# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

from pyrogram import Client, filters
from pyrogram.types import Message

from userlixo.handlers.bot.help import on_help_u


@Client.on_message(filters.su_cmd("help"))
async def on_help_m(c: Client, m: Message):
    await on_help_u(c, m)

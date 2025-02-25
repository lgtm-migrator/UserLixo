# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import os

from pyrogram import Client
from pyrogram.types import CallbackQuery

from userlixo.config import langs


# Getting the language to use
@Client.on_callback_query(group=-2)
async def deflang(c: Client, cq: CallbackQuery):
    cq._lang = langs.get_language(os.getenv("LANGUAGE"))

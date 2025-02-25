# SPDX-License-Identifier: MIT
# Copyright (c) 2018-2022 Amano Team

import html
import io
import os
import re
import traceback
from contextlib import redirect_stdout

from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.su_cmd(r"(?P<cmd>ex(ec)?)\s+(?P<code>.+)", flags=re.S))
async def on_exec_user(c: Client, m: Message):
    await execs(c, m)


async def execs(c: Client, m: Message):
    lang = m._lang
    act = m.edit if await filters.me(c, m) else m.reply
    strio = io.StringIO()
    cmd = m.matches[0]["cmd"]
    code = m.matches[0]["code"]

    # Shortcuts that will be available for the user code
    reply = m.reply_to_message
    user = (reply or m).from_user
    chat = m.chat

    code_function = "async def __ex(c, m, reply, user, chat):"
    for line in code.split("\n"):
        code_function += f"\n    {line}"
    exec(code_function)

    with redirect_stdout(strio):
        try:
            await locals()["__ex"](c, m, reply, user, chat)
        except BaseException:
            traceback_string = traceback.format_exc()
            text = f"<b>{html.escape(traceback_string)}</b>"
            if cmd == "exec":
                return await act(text)
            return await m.reply(text)

    text = lang.executed_cmd
    output = strio.getvalue()
    if output:
        if len(output) > 4096:
            with open("output.txt", "w") as f:
                f.write(output)
            await m.reply_document("output.txt", quote=True)
            return os.remove("output.txt")
        output = html.escape(output)  # escape html special chars
        text = "".join(f"<code>{line}</code>\n" for line in output.splitlines())
        if cmd == "exec":
            return await act(text)
        await m.reply(text)

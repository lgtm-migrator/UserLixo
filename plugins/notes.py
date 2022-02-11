import html
import json
import os

from pyrogram import Client, filters
from pyrogram.types import Message

from config import cmds
from db import db, save


@Client.on_message(filters.command("note", prefixes=".") & filters.me)
async def onnote(client: Client, message: Message):
    parts = message.text.split(" ", 2)
    if len(parts) == 1:
        return
    elif len(parts) == 2:
        note_key = parts[1]
        exists = note_key in db["notes"]

        if message.reply_to_message:
            msg = message.reply_to_message
            if msg.text:
                note_obj = dict(type="text", value=msg.text)
            elif msg.media:
                media = (
                    msg.audio
                    or msg.document
                    or msg.photo
                    or msg.sticker
                    or msg.video
                    or msg.animation
                    or msg.voice
                    or msg.video_note
                )
                if not media:
                    return await message.edit("Non-supported media")
                note_value = {"file_id": media.file_id, "file_ref": media.file_ref}
                if msg.caption:
                    note_value["caption"] = msg.caption
                note_obj = dict(type="media", value=note_value)
            else:
                return await message.edit("Nothing to save here.")

            db["notes"][note_key] = note_obj
            save(db)
            action = "updated" if exists else "created"
            await message.edit(f"Note '<code>{html.escape(note_key)}</code>' {action}.")
        else:
            if exists:
                note_obj = db["notes"][note_key]
                if note_obj["type"] == "text":
                    await message.edit(note_obj["value"])
                elif note_obj["type"] == "media":
                    await message.delete()
                    await client.send_cached_media(
                        message.chat.id,
                        note_obj["value"]["file_id"],
                        reply_to_message_id=(
                            message.reply_to_message.message_id
                            if message.reply_to_message
                            else None
                        ),
                    )
            else:
                await message.edit(
                    f"There isn't a note named '<code>{html.escape(note_key)}</code>'."
                )
    else:
        note_key = parts[1]
        note_value = parts[2]
        exists = note_key in db["notes"]

        note_obj = dict(type="text", value=note_value)

        db["notes"][note_key] = note_obj
        save(db)
        action = "updated" if exists else "created"
        await message.edit(f"Note '<code>{html.escape(note_key)}</code>' {action}.")


@Client.on_message(filters.command("notes", prefixes=".") & filters.me)
async def onnotes(client: Client, message: Message):
    notes = db["notes"]

    parts = message.text.split(" ", 2)
    if len(parts) == 1:
        if not len(notes):
            await message.edit("No notes have been created yet.")
        else:
            text = "Saved notes:\n" + "\n".join(
                [
                    "- <code>{}</code>".format(html.escape(note_key))
                    for note_key in notes.keys()
                ]
            )
            await message.edit(text)
    else:
        command = parts[1]
        if command == "backup":
            with open("notes.json", "w") as fp:
                json.dump(notes, fp, indent=2)
            await client.send_document("me", document="notes.json")
            os.remove("notes.json")
            await message.edit("notes.json sent to Saved Messages.")
        elif command == "remove":
            if len(parts) == 3:
                note_key = parts[2]
                if note_key in notes:
                    del db["notes"][note_key]
                    save(db)
                    await message.edit(
                        f"Note '<code>{html.escape(note_key)}</code>' deleted."
                    )
                else:
                    await message.edit(
                        f"There isn't a note named '<code>{html.escape(note_key)}</code>'."
                    )
            else:
                keys = list(notes.keys())
                if len(keys):
                    example_key = keys[0]
                else:
                    example_key = "note_key"
                await message.edit(
                    f"Missing argument: you need to specify the note you want to remove.\nExample: <code>.notes remove {html.escape(example_key)}</code>"
                )
        elif command == "restore":
            if (
                not message.reply_to_message
                or not message.reply_to_message.document
                or message.reply_to_message.document.file_name != "notes.json"
            ):
                return await message.edit(
                    "Reply to a notes.json generated by <code>.notes backup</code>"
                )
            path = await message.reply_to_message.download("restore.json")
            try:
                with open(path) as fp:
                    restore = json.load(fp)

                added_notes = []
                for note_key, note_obj in restore.items():
                    if (
                        not note_key
                        or "type" not in note_obj
                        or "value" not in note_obj
                    ):
                        return await message.edit("Invalid notes.json")

                    added_notes.append(note_key)
                    db["notes"][note_key] = {
                        key: note_obj[key]
                        for key in note_obj.keys() & ["type", "value"]
                    }
                save(db)
                await message.edit("Notes restored:\n - " + "\n - ".join(added_notes))
            except:
                return await message.edit("An error ocurred while opening the json.")


@Client.on_message(filters.regex("^#") & filters.me)
async def onsharp(client: Client, message: Message):
    note_key = message.text[1:]
    exists = note_key in db["notes"]

    if exists:
        note_obj = db["notes"][note_key]
        if note_obj["type"] == "text":
            text = note_obj["value"]
            msg = await message.edit(text)

            if text.startswith(".exec"):
                from plugins.execs import execs

                await execs(client, msg)
            elif text.startswith(".cmd"):
                from plugins.cmd import cmd

                await cmd(client, msg)
        elif note_obj["type"] == "media":
            await message.delete()
            await client.send_cached_media(
                message.chat.id,
                note_obj["value"]["file_id"],
                reply_to_message_id=(
                    message.reply_to_message.message_id
                    if message.reply_to_message
                    else None
                ),
            )


cmds.update(
    {
        ".note": "Add/update a note. Pass the name of the note as second parameter and the value after (or reply to a message to use its contents)",
        ".notes": "List the saved notes.",
        ".notes backup": "Backup the notes into Saved Messages",
        ".notes remove": "Remove the specified note",
        "#<note>": html.escape("Get a note. Replace '<note>' with the note key"),
    }
)

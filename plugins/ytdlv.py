from pyrogram import Client, Filters
import youtube_dl
import os
import time
import requests

@Client.on_message(Filters.command("ytdlv"))
def ytdlv(client, message):
    url = message.text[7:]
    ydl = youtube_dl.YoutubeDL({'outtmpl': 'dls/%(title)s.%(ext)s', 'noplaylist': True})
    if 'youtu.be' not in url and 'youtube.com' not in url:
        yt = ydl.extract_info('ytsearch:' + url, download=False)['entries'][0]
        url = 'https://www.youtube.com/watch?v=' + yt['id']
    yt = ydl.extract_info(url, download=False)
    m = message.reply(f'Downloading `{yt["title"]}`')
    yt = ydl.extract_info(url, download=True)
    client.send_chat_action(message.chat.id,'UPLOAD_VIDEO')
    a = f'Sending `{yt["title"]}`'
    m.edit(a)
    ctime = time.time()
    r = requests.get(yt['thumbnail'])
    with open(f'{ctime}.png', 'wb') as f:
        f.write(r.content)
    client.send_video(message.chat.id,ydl.prepare_filename(yt),caption=yt["title"],duration=yt['duration'],thumb=f'{ctime}.png',progress=progress,progress_args=(m,a),supports_streaming=True,reply_to_message_id=message.message_id)
    m.delete()
    os.remove(ydl.prepare_filename(yt))
    os.remove(f'{ctime}.png')
    
def progress(current, total, m, a):
    m.edit(a + '\n' + "{:.1f}%".format(current * 100 / total))
import os
import shutil

import requests

from .utils import xml_caption_to_srt


def download_audio_content(yt, output_path):
    audio = yt.streams.filter(only_audio=True).order_by('abr').last()
    audio.download(output_path=output_path)


def download_progressive_content(yt, output_path):
    stream = yt.streams.filter(progressive=True).order_by('resolution').last()
    stream.download(output_path=output_path)
    return stream.default_filename # safe filename for save operation


def download_adaptive_content(yt, output_path):
    video = yt.streams.filter(adaptive=True).order_by('resolution').last()
    audio = yt.streams.filter(only_audio=True).order_by('abr').last()

    video_filename = f'video.{video.mime_type.split("/")[-1]}'
    audio_filename = f'audio.{audio.mime_type.split("/")[-1]}'
    thumbnail_filename = 'thumbnail.png'
    title = video.default_filename

    video.download(output_path=output_path, filename=video_filename)
    audio.download(output_path=output_path, filename=audio_filename)
    download_thumbnail(yt.thumbnail_url, thumbnail_filename, output_path)

    return video_filename, audio_filename, thumbnail_filename, title


def download_thumbnail(thumbnail_url, thumbnail_filename, output_path):
    r = requests.get(thumbnail_url, stream=True)
    if r.status_code == 200:
        with open(os.path.join(output_path, thumbnail_filename), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


def download_subtitles(captions, output_path):
    sub_files = []
    for caption in captions:
        sub = captions[caption.code]
        srt = xml_caption_to_srt(sub.xml_captions)
        filename = os.path.join(output_path, f'{caption.code}.srt')
        sub_files.append(filename)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(srt)
    return sub_files

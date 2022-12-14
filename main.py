import os
import sys
import argparse
from urllib.parse import urlparse, parse_qs

from pytube import YouTube, Playlist, Channel
from pytube.exceptions import VideoUnavailable, VideoPrivate, MembersOnly, RecordingUnavailable, LiveStreamError

from utils import download_audio_content, download_progressive_content,\
                  download_adaptive_content, download_thumbnail, download_subtitles,\
                  target_directory, delete_files, multiplex, add_sub


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', dest='input', type=str,
                        help='Link to video, playlist, channel')
    parser.add_argument('-o', '--output', dest='output', type=str,
                        help='Output path')
    parser.add_argument('-b', '--best-quality', dest='best', action='store_true',
                        help='Download in best quality (default)')
    parser.set_defaults(best=False)
    parser.add_argument('-l', '--low-quality', dest='low', action='store_true',
                        help='Download in low quality')
    parser.set_defaults(low=False)
    parser.add_argument('-s', '--subtitles', dest='subtitles', action='store_true',
                        help='Download subtitles, if available (ignored if download only audio)')
    parser.set_defaults(subtitles=False)
    parser.add_argument('-a', '--authentication', dest='authentication', action='store_true',
                        help='Use authentication to download protected content')
    parser.set_defaults(authentication=False)
    parser.add_argument('-m', '--music', dest='music', action='store_true',
                        help='Download only audio')
    parser.set_defaults(music=False)
    return parser.parse_args()


def on_progress(stream, data_chunk, remaining_bytes):
    total_size = stream.filesize
    completed_bytes = total_size - remaining_bytes
    print(f'\rStatus: {round(completed_bytes / total_size * 100, 2)}%', end='')


def single_video(link, output_path, best_quality=True, subtitle=False, use_oauth=False, music=False):
    yt = YouTube(link, on_progress_callback=on_progress, use_oauth=use_oauth)
    try:
        yt.check_availability()
        yt.streams
    except VideoPrivate:
        print(f'Video {yt.title} is private.')
    except MembersOnly:
        print(f'Video {yt.title} is members-only content.')
    except (RecordingUnavailable, LiveStreamError):
        print(f'Live stream recording {yt.title} is unavailable.')
    except VideoUnavailable:
        print(f'Video {yt.title} is unavailable.')
    except:
        print(f'Video {yt.title} is unavailable.')
    else:
        print(f'Downloading {yt.title}')

        if music:
            return download_audio_content(yt, output_path)

        if best_quality:
            video_filename, audio_filename, thumbnail_filename, title = download_adaptive_content(yt, output_path)
            multiplex(video_filename, audio_filename, thumbnail_filename, title, output_path)
            delete_files(output_path, [video_filename, audio_filename, thumbnail_filename])
        else:
            title = download_progressive_content(yt, output_path)

        if subtitle:
            sub_files = download_subtitles(yt.captions, output_path)
            subtitled_filename = add_sub(title, sub_files, output_path)
            delete_files(output_path, [title, *sub_files])
            os.rename(os.path.join(output_path, f'sub_{subtitled_filename}'),
                      os.path.join(output_path, subtitled_filename))


def playlist(link, output_path, best_quality=True, subtitle=False, use_oauth=False, music=False):
    p = Playlist(link)
    try:
        print(f'Downloading {p.title}')
    except KeyError:
        print('Playlist unavailable.')
    else:
        for url in p.video_urls:
            single_video(url, output_path, best_quality=best_quality, subtitle=subtitle, use_oauth=use_oauth, music=music)


def channel(link, output_path, best_quality=True, subtitle=False, use_oauth=False, music=False):
    c = Channel(link)
    print(f'Downloading videos by: {c.channel_name}')
    for url in c.video_urls:
        single_video(url, output_path, best_quality=best_quality, subtitle=subtitle, use_oauth=use_oauth, music=music)


def get_type(link):
    is_playlist = parse_qs(urlparse(link).query).get('list') is not None
    is_channel = False
    return is_playlist, is_channel


if __name__ == '__main__':
    args = parse_args()

    if args.input is None:
        print('Use: python -h')
        sys.exit()

    best = True
    if args.low and not args.best:
        best = False

    is_playlist, is_channel = get_type(args.input)

    output_path = target_directory(args.output)

    if is_playlist:
        playlist(args.input, output_path, best, args.subtitles, args.authentication, args.music)
    elif is_channel:
        channel(args.input, output_path, best, args.subtitles, args.authentication, args.music)
    else:
        single_video(args.input, output_path, best, args.subtitles, args.authentication, args.music)

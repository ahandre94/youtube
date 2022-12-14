import os
from collections import OrderedDict

from ffmpy import FFmpeg


def multiplex(video, audio, thumbnail, title, output_path):
    _, output_extension = os.path.splitext(video)

    output_options = '-map 0 -map 1 -map 2 -c copy -disposition:v:1 attached_pic'
    if output_extension == '.webm':
        output_options = '-c copy'

    ff = FFmpeg(
        global_options='-y',
        inputs=OrderedDict([
            (os.path.join(output_path, video), None),
            (os.path.join(output_path, audio), None),
            (os.path.join(output_path, thumbnail), None)
        ]),
        outputs={os.path.join(output_path, title): output_options}
    )
    ff.run()


def _get_output_settings_with_sub(file, subtitles):
    filename, output_extension = os.path.splitext(file)
    output_filename = f'{file}'
    output_options = ' '.join(map(lambda x : f'-map {x}', range(len(subtitles) + 1))) + ' -c copy -c:s mov_text'
    if output_extension == '.webm': # webm does not support subtitles
        output_filename = f'{filename}.mkv'
        output_options = output_options.removesuffix(' -c:s mov_text')
    return output_filename, output_options


def add_sub(file, sub_files, output_path):
    subtitles = [(os.path.join(output_path, sub), None) for sub in sub_files]
    inputs = OrderedDict([(os.path.join(output_path, file), None), *subtitles])
    output_filename, output_options = _get_output_settings_with_sub(file, subtitles)

    ff = FFmpeg(
        global_options='-y',
        inputs=inputs,
        outputs={os.path.join(output_path, f'sub_{output_filename}'): output_options}
    )
    ff.run()
    return output_filename

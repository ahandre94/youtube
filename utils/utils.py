import os
import math
import time
from html import unescape
import xml.etree.ElementTree as ElementTree


def target_directory(output_path=None):
    """
    Function for determining target directory of a download.
    Returns an absolute path (if relative one given) or the current
    path (if none given). Makes directory if it does not exist.
    :type output_path: str
        :rtype: str
    :returns:
        An absolute directory path as a string.
    """
    if output_path:
        if not os.path.isabs(output_path):
            output_path = os.path.join(os.getcwd(), output_path)
    else:
        output_path = os.getcwd()
    os.makedirs(output_path, exist_ok=True)
    return output_path


def float_to_srt_time_format(d):
    """Convert decimal durations into proper srt format.

    :rtype: str
    :returns:
        SubRip Subtitle (str) formatted time duration.

    float_to_srt_time_format(3.89) -> '00:00:03,890'
    """
    fraction, whole = math.modf(d / 1000)
    time_fmt = time.strftime('%H:%M:%S,', time.gmtime(whole))
    ms = f'{fraction:.3f}'.replace('0.', '')
    return time_fmt + ms


def xml_caption_to_srt(xml_captions):
    """Convert xml caption tracks to "SubRip Subtitle (srt)".

    :param str xml_captions:
        XML formatted caption tracks.
    """
    segments = []
    root = ElementTree.fromstring(xml_captions)
    for i, child in enumerate(list(root.findall('body/p'))):
        text = child.text or ''
        caption = unescape(text.replace('\n', ' ').replace('  ', ' '),)
        try:
            duration = float(child.attrib['d'])
        except KeyError:
            duration = 0.0
        start = float(child.attrib['t'])
        end = start + duration
        sequence_number = i + 1  # convert from 0-indexed to 1.
        line = '{seq}\n{start} --> {end}\n{text}\n'.format(
            seq=sequence_number,
            start=float_to_srt_time_format(start),
            end=float_to_srt_time_format(end),
            text=caption,
        )
        segments.append(line)
    return '\n'.join(segments).strip()


def _delete_file(output_path, file):
    os.remove(os.path.join(output_path, file))


def delete_files(output_path, files):
    for file in files:
        _delete_file(output_path, file)

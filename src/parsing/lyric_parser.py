import re
import html
import logging


def _remove_double_blank_lines(song_body):
    song_body = \
        re.sub('\\\\r\\\\n\\\\r\\\\n\\\\r\\\\n', '\\\\r\\\\n\\\\r\\\\n', song_body)
    return song_body


# Removes [tab] and [ch] tags around chords and lyrics
def _remove_tags(song_body):
    song_body_without_tags = re.sub('\[\/?tab\]|\[\/?ch\]', '', song_body)
    return song_body_without_tags


# Splits lines at \r and \n characters
# Takes a single string and returns  a list of lines consisting of both chords and lyrics
def split_song_body_into_lines(song_body):
    p = _compile_regex('\\\\r\\\\n')
    lines = re.split(p, song_body)
    return lines


# Strips HTML tags and removes double blank lines
def _replace_html_special_chars(song_body):
    song_body = re.sub('&.*?;', lambda x: html.unescape(x.group()), song_body)
    song_body = song_body.encode('latin-1', 'ignore').decode('latin-1')
    return song_body


def clean_song_body(song_body):
    song_body = _remove_double_blank_lines(song_body)
    song_body = _remove_tags(song_body)
    song_body = _replace_html_special_chars(song_body)
    return song_body


def _compile_regex(regex):
    return re.compile(regex)


def get_song_body_from_response(response):
    p = _compile_regex('(\[Verse.* ?)\[/tab\]')
    content = re.search(p, response)

    # If the lyrics don't contain a [Verse] at the beginning, search for an "Intro"
    if content is None:
        alternative_p = _compile_regex('\\\\n(\[?Intro.*\[/tab\])')
        content = re.search(alternative_p, response)

    if content is None:
        alternative_p = _compile_regex('(\[ch.*)\[/tab\]')
        content = re.search(alternative_p, response)

    if content is None:
        logging.error(f"Song could not be parsed: {response}")
        exit(0)

    return content.group(1)

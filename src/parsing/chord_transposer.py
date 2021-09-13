import re
import operator

chords_sharp = [
    'A', 'A#', 'B', 'C', 'C#',
    'D', 'D#', 'E', 'F', 'F#',
    'G', 'G#'
]


chords_flat = [
    'A', 'Bb', 'B', 'C', 'Db',
    'D', 'Eb', 'E', 'F', 'Gb',
    'G', 'Ab'
]

ops = {
    '+': operator.add,
    '-': operator.sub
}


def _get_chord_regex():
    return re.compile('([A-G]?\/?[A-G](#|b){0,2})m?(sus|maj|min)?\d*?[ |\n]')


def _transpose_chord(operation, steps, chord):
    if '/' in chord:
        sub_chords = re.split('/', chord)
        for chord in sub_chords:
            return _transpose_chord(operation, steps, chord)
    if '#' in chord:
        chord_index = chords_sharp.index(chord)
        chord_transposed = chords_sharp[operation(chord_index, steps) % len(chords_sharp)]
    else:
        chord_index = chords_flat.index(chord)
        chord_transposed = chords_flat[operation(chord_index, steps) % len(chords_sharp)]
    return chord_transposed


# TODO figure out what to do with slash chords (G/B)
def transpose(mode, steps, song):
    chord_regex = _get_chord_regex()
    for i in range(len(song)):
        if (re.search(chord_regex, song[i])) is not None:
            song[i] = re.sub(chord_regex, lambda x: _transpose_chord(ops[mode], steps, x.group(1)), song[i])
    return song

import fpdf
import config


def initialize_pdf():
    initialized_pdf = fpdf.FPDF(format='A4', unit='mm')
    initialized_pdf.add_page()
    return initialized_pdf


def _write_title(pdf, title, conf):
    pdf.set_font(conf['font'], size=conf['size'], style=conf['style'])
    pdf.cell(200, 8, txt=title, ln=1, align="L")


def _write_artist(pdf, artist, conf):
    pdf.set_font(conf['font'], size=conf['size'], style=conf['style'])
    pdf.cell(200, 6, txt=artist, ln=1, align="L")


def _write_body(pdf, song, conf):
    pdf.set_font(conf['font'], size=conf['size'])
    for i in range(len(song)):
        pdf.cell(100, 4, txt=f"{song[i]}", ln=1, align="L")


def write_song(song_metadata, song_body):
    song_title = song_metadata['title']
    song_artist = song_metadata['artist']
    pdf = initialize_pdf()

    _write_title(pdf, song_title, config.get_config_element('pdf.title'))
    _write_artist(pdf, song_artist, config.get_config_element('pdf.artist'))

    pdf.cell(200, 4, txt='', ln=1)

    _write_body(pdf, song_body, config.get_config_element('pdf.body'))
    return pdf.output(dest='S')

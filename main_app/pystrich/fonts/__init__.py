import os

from PIL import ImageFont


def get_font(font_name, font_size):
    fontdir = os.path.dirname(os.path.abspath(__file__))
    fontfile = os.path.join(fontdir, "%s%02d.pil" % (font_name, font_size))
    font = ImageFont.load_path(fontfile)
    return font

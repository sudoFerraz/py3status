# -*- coding: utf-8 -*-
from __future__ import division

import ast
import os
import re

from hashlib import md5
from subprocess import check_output

from PIL import Image, ImageFont, ImageDraw
from fontTools.ttLib import TTFont


WIDTH = 650
TOP_BAR_HEIGHT = 5
BAR_HEIGHT = 24
HEIGHT = TOP_BAR_HEIGHT + BAR_HEIGHT
X_OFFSET = 5
PADDING = 4

SEP_PADDING_LEFT = 4
SEP_PADDING_RIGHT = SEP_PADDING_LEFT + 1

SEP_BORDER = 4
TEXT_PADDING = 0
BORDER_TOP = 1

FONT = 'DejaVu Sans Mono'
FONT_STYLES = ['Regular', 'Book']

FONT_SIZE = BAR_HEIGHT - (PADDING * 2)

# Pillow does poor font rendering so we are best of creating huge text and then
# shrinking with anti-aliasing.  SCALE is how many times bigger we render the
# test
SCALE = 8

COLOR = '#FFFFFF'
COLOR_BG = '#000000'

COLOR_SEP = '#666666'

COLOR_URGENT = '#FFFFFF'
COLOR_BG_URGENT = '#900000'

COLOR_PY3STATUS = '#FFFFFF'


def get_color_for_name(module_name):
    """
    Create a custom color for a given string.
    This allows the screenshots to each have a unique color but for that color
    to be consistent.
    """
    # all screenshots of the same module should be a uniform color
    module_name = module_name.split('-')[0]

    saturation = 0.5
    value = 243.2
    try:
        module_name = module_name.encode('utf-8')
    except:
        pass
    hue = int(md5(module_name).hexdigest(), 16) / 16**32
    hue *= 6
    hue += 3.708
    r, g, b = (
        (value, value - value * saturation * abs(1 - hue % 2), value - value *
         saturation) * 3)[5**int(hue) // 3 % 3::int(hue) % 2 + 1][:3]
    return '#' + '%02x' * 3 % (int(r), int(g), int(b))


def init_fonts():
    font_data = []
    output = check_output('fc-list').decode('utf-8').splitlines()
    for font in output:
        font_info = font.split(':')
        name = font_info[1].strip()
        styles = font_info[2][6:].split(',')

        # only get fonts that are in allowed styles
        if not set(FONT_STYLES) & set(styles):
            print(name, styles)
            continue
        font_data.append((name, font_info[0], styles))
    print('fonts available')
    for font in sorted(font_data):
        print(font[0])
    return font_data



FONTS = init_fonts()
ttf_font_cache = {}

def get_font_path(font):
    for name, path, styles in FONTS:
        if name == font:
            return path


def glyph_font(char, font=None):
    char = ord(char)
    if font is None:
        font = FONT

    if font not in ttf_font_cache:
        font_path = get_font_path(font)
        ttf_font_cache[font] = TTFont(font_path)
    font = ttf_font_cache[font]

    for cmap in font['cmap'].tables:
        if cmap.isUnicode():
            if char in cmap.cmap:
                return True
    return False


def glyph_search(char):
    for name, path, styles in FONTS:
        if not path.endswith('.ttf'):
            continue
        if glyph_font(char, font=name):
            return name


def sort_missing_unicode(data):
    sorted_data = []
    for part in data:
        fix = []
        missing_char = False
        for char in part.get('full_text', ''):
            if glyph_font(char):
                fix.append((char, None))
            else:
                found_in = glyph_search(char)
                if found_in:
                    missing_char = True
                fix.append((char, found_in))

        if missing_char:
            base = part.copy()
            if 'separator' in base:
                del base['separator']
            current = part.copy()
            font_current = None
            out = []
            full_text = u''
            for char, font in fix:
                if font_current != font:
                    if full_text:
                        current['full_text'] = full_text
                        if font_current:
                            current['_font'] = font_current
                        out.append(current)
                        current = base.copy()
                        full_text = u''
                    font_current = font
                full_text += char
            if full_text:
                current['full_text'] = full_text
                if font:
                    current['_font'] = font
                out.append(current)
            sorted_data.extend(out)
            print(out)
        else:
            sorted_data.append(part)
    return sorted_data


def create_screenshot(name, data, path, module=True):
    img = Image.new('RGB', (WIDTH, HEIGHT), COLOR_BG)
    d = ImageDraw.Draw(img)

    # top bar
    desktop_color = get_color_for_name(name)
    d.rectangle((0, 0, WIDTH, TOP_BAR_HEIGHT), fill=desktop_color)
    if not isinstance(data, list):
        data = [data]

    if module:
        data.append(
            {
                'full_text': name.split('-')[0],
                'color': desktop_color,
                'separator': True,
            }
        )
        data.append(
            {
                'full_text': 'py3status',
                'color': COLOR_PY3STATUS,
                'separator': True,
            }
        )
    data = sort_missing_unicode(data)

    x = X_OFFSET

    font = False
    for part in reversed(data):
        text = part.get('full_text')
        color = part.get('color', COLOR)
        background = part.get('background')
        separator = part.get('separator')
        urgent = part.get('urgent')

        if urgent:
            color = COLOR_URGENT
            background = COLOR_BG_URGENT

        font_block = part.get('_font')
        if font_block != font:
            font_path = get_font_path(font_block or FONT)
            fnt = ImageFont.truetype(font_path, FONT_SIZE * SCALE)
            font = font_block

        size = fnt.getsize(text)

        if background:
            d.rectangle((WIDTH - x - size[0],
                         TOP_BAR_HEIGHT + PADDING,
                         WIDTH - x - 1,
                         HEIGHT - PADDING,
                         ), fill=background)

        x += size[0] // SCALE

        txt = Image.new('RGB', size, background or COLOR_BG)
        d_text = ImageDraw.Draw(txt)
        d_text.text((0, 0), text, font=fnt, fill=color)
        txt = txt.resize((size[0] // SCALE, size[1] // SCALE), Image.ANTIALIAS)
        img.paste(txt, (WIDTH - x, TOP_BAR_HEIGHT + PADDING))

        if separator:
            x += SEP_PADDING_RIGHT
            d.line(((WIDTH - x, TOP_BAR_HEIGHT + PADDING),
                    (WIDTH - x, TOP_BAR_HEIGHT + 1 + PADDING + FONT_SIZE)),
                    fill=COLOR_SEP, width=1)
            x += SEP_PADDING_LEFT

    img.save(os.path.join(path, '%s.png' % name))
    print(os.path.join(path, '%s.png' % name))


data = [
    {'color': '#FF0000', 'full_text': 'module 1', 'separator': True},
    {'color': '#CCFF00', 'full_text': 'module 2', 'separator': True},
    {'color': '#00FF66', 'full_text': 'module 3', 'separator': True},
    {'color': '#0066FF', 'full_text': 'module 4', 'separator': True},
    {'color': '#CC00FF', 'full_text': 'module 5', 'separator': True}
]
#make_screenshot(data)
## get a font
## get a drawing context
#
## draw text, half opacity
#d.text((10,10), "Hello", font=fnt, fill=(255,255,255,128))
## draw text, full opacity
#d.text((10,60), "World", font=fnt, fill=(255,255,255,255))
#
#txt = txt.resize((400, 30))
#print(txt)
#out = Image.alpha_composite(img, txt)
#
#txt.show()



def parse_sample_data(sample_data, module_name):
    """
    Parse sample output definitions and return a dict
    {screenshot_name: sample_output}
    """
    samples = {}
    name = None
    data = ''
    count = 0
    for line in sample_data.splitlines() + ['']:
        if line == '':
            if data:
                if name:
                    name = u'%s-%s-%s' % (module_name, count, name)
                else:
                    name = module_name
                try:
                    samples[name] = ast.literal_eval(data)
                except:
                    samples[name] = 'SAMPLE DATA ERROR'
                name = None
                data = ''
                count += 1
            continue
        if name is None and data == '' and not line[0] in ['[', '{']:
            name = line
            continue
        else:
            data += line
    return samples


def get_samples():
    '''
    Look in all core modules and get any samples from the docstrings.
    return a dict {screenshot_name: sample_output}
    '''
    samples = {}
    module_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'modules')
    for file in sorted(os.listdir(module_dir)):
        if file.endswith('.py') and file != '__init__.py':
            module_name = file[:-3]
            with open(os.path.join(module_dir, file)) as f:
                module = ast.parse(f.read())
                raw_docstring = ast.get_docstring(module)
                if raw_docstring is None:
                    continue
                parts = re.split('^SAMPLE OUTPUT$', raw_docstring, flags=re.M)
                if len(parts) == 1:
                    continue
                sample_data = parts[1]
                samples.update(parse_sample_data(sample_data, module_name))
    return samples


def create_screenshots(quiet=False):
    """
    create screenshots for all core modules.
    The screenshots directory will have all .png files deleted before new shots
    are created.
    """

    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'doc', 'screenshots'
    )
    path = '../doc/screenshots'
    # create dir if not exists
    try:
        os.makedirs(path)
    except OSError:
        pass
##    # delete all existing screenshots
##    test = os.listdir(path)
##
##    for item in test:
##        if item.endswith(".png"):
##            os.remove(os.path.join(path, item))

    print('Creating screenshots...')
    samples = get_samples()
    for k, v in samples.items():
        create_screenshot(k, v, path)

#    modules = ['github', 'dpms', 'xrandr', 'clock']
#
#    others = {}
#    out = []
#    for module in modules:
#        data = samples.get(module)
#        if data:
#            if isinstance(data, list):
#                data[-1]['separator'] = True
#                out.extend(data)
#            else:
#                data['separator'] = True
#                out.append(data)
#    others['main'] = out
#
#    for k, v in others.items():
#        image_maker.create_screenshot(k, v, quiet=quiet, module=False)


if __name__ == '__main__':
    create_screenshots()

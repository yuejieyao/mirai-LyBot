import re
import uuid
import string
from PIL import Image, ImageFont, ImageDraw


def text_to_img(str):
    info_font = ImageFont.truetype('modules/resource/font/sarasa-mono-sc-bold.ttf', 26)
    info_color = "#474747"
    bg_color = "#F5F5F7"
    lines = get_cut_str(str, 60)
    text = '\n'.join(lines)
    w, h = info_font.getsize_multiline(text)
    img_new = Image.new("RGB", (w+10, h+10), bg_color)
    draw = ImageDraw.Draw(img_new)
    draw.text((5, 5), text, info_color, info_font)
    path = f"modules/resource/temp/{uuid.uuid1()}.png"
    img_new.save(path)
    return path


def get_cut_str(str, cut):
    '''
    自动断行，用于 Pillow 等不会自动换行的场景
    '''
    punc = """，,、。.？?）》】“"‘'；;：:！!·`~%^& """
    si = 0
    i = 0
    next_str = str
    str_list = []

    while re.search(r'\n\n\n\n\n', next_str):
        next_str = re.sub(r'\n\n\n\n\n', "\n", next_str)
    for s in next_str:
        if s in string.printable:
            si += 1
        else:
            si += 2
        i += 1
        if next_str == "":
            break
        elif next_str[0] == "\n":
            next_str = next_str[1:]
        elif s == "\n":
            str_list.append(next_str[:i-1])
            next_str = next_str[i-1:]
            si = 0
            i = 0
            continue
        if si > cut:
            try:
                if next_str[i] in punc:
                    i += 1
            except IndexError:
                str_list.append(next_str)
                return str_list
            str_list.append(next_str[:i])
            next_str = next_str[i:]
            si = 0
            i = 0
    str_list.append(next_str)
    i = 0
    non_wrap_str = []
    for p in str_list:
        if p == "":
            break
        elif p[-1] == "\n":
            p = p[:-1]
        non_wrap_str.append(p)
        i += 1
    return non_wrap_str

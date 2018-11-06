#!/usr/bin/python3

import operator
import argparse
from PIL import Image,ImageFont
from jinja2 import Template

ascii_char = list("MNHQ$OC?7>!:-;. ")
WIDTH = 540
HEIGHT = 300

def get_char(r,g,b,alpha=256):
    if alpha == 0 :
        return ' '
    lenght = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
    unit = (256.0 + 1)/lenght
    return ascii_char[int(gray/unit)]

def _green_screen_check(rgb, sensibility, reverse=False):
    if sensibility is None:
        return False
    op = operator.gt if reverse else operator.le
    for x in rgb:
        if not op(x, sensibility):
            return False
    return True
def gif2txt(filename, maxLen=80, output_file='out.html', with_color=False,
        green_screen_sensibility=None, reverse_green_screen=False):
    try:
        maxLen = int(maxLen)
    except:
        maxLen = 80
    try:
        img = Image.open(filename)
    except IOError:
        exit("file not found: {}".format(filename))
    width, height = img.size
    rate = float(maxLen) / max(width, height)
    width = int(rate * width)
    height = int(rate * height)
    palette = img.getpalette()
    strings = []
    try:
        while 1:
            img.putpalette(palette)
            im = Image.new('RGB', img.size)
            im.paste(img)
            im = im.resize((width, height))
            string = ''
            for h in range(height):
                for w in range(width):
                    rgb = im.getpixel((w, h))
                    if _green_screen_check(rgb,
                                           green_screen_sensibility,
                                           reverse_green_screen):
                        rgb = (0, 255, 0)
                    if with_color:
                        string += "<span style=\"color:rgb%s;\">▇</span>" % str(rgb)
                    else:
                        string += ascii_char[int(sum(rgb) / 3.0 / 256.0 * len(ascii_char))]
                string += '\n'
            if isinstance(string, bytes):
                string = string.decode('utf8')
            strings.append(string)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    with open('template.jinja') as tpl_f:
        template = Template(tpl_f.read())
        html = template.render(strings=strings)
    with open(output_file, 'w') as out_f:
        if not isinstance(html, str):
            html = html.encode('utf8')
        out_f.write(html)

def getAsciiFile(inputFile, outputFile, maxLen):
    try:
        maxLen = int(maxLen)
    except:
        maxLen = 80
    try:
        img = Image.open(inputFile)
    except IOError:
        exit("file not found: {}".format(inputFile))

    txt = ""
    height = img.size[0]
    width = img.size[1]
    img = img.resize((width, height), Image.ANTIALIAS)
    palette = img.getpalette()
    print("h="+str(height)+" w="+str(width))
    for h in range(height):
        for w in range(width):
            # im.getpixel:根据坐标取得RGB对应的r，g，b三个值,这里的getpixel((i,j))的两个括号非常重要
            # print("h=" + str(w) + " w=" + str(h))
            txt += get_char(*img.getpixel((w, h)))
        txt += '\n'
    print(txt)

    with open(outputFile, 'w') as f:
        f.write(txt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input',
                        help='Gif input file')

    parser.add_argument('-m', '--maxLen', type=int,
                        help='Max width of the output gif')

    parser.add_argument('-o', '--output',
                        help='Name of the output file')

    parser.add_argument('-c', '--color', action='store_true',
                        default=False,
                        help='With color')

    parser.add_argument('-g', '--green-screen-sensibility',
                        type=int, default=None,
                        help='convert black and grey into green, '
                             'sensibility between 1 and 255, suggested 128')

    parser.add_argument('-r', '--reverse-green-screen',
                        action='store_true', default=False,
                        help='white (instead of black) is converted into '
                             'green, you can still use -g option to set sensibility')

    args = parser.parse_args()

    if not args.maxLen:
        args.maxLen = 80

    if not args.output:
        args.output = 'out.html'

    if args.reverse_green_screen and not args.green_screen_sensibility:
        args.green_screen_sensibility = 128

    if args.green_screen_sensibility:
        args.color = True

    # getAsciiFile(inputFile=args.input, outputFile=args.output)

    gif2txt(

        filename=args.input,

        maxLen=args.maxLen,

        output_file=args.output,

        with_color=args.color,

        green_screen_sensibility=args.green_screen_sensibility,

        reverse_green_screen=args.reverse_green_screen,

    )


if __name__ == '__main__':
    main()
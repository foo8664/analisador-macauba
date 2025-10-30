#!/usr/bin/env python
import os
import argparse
from shlex import split as shsplit
from sys import argv
from PIL import Image, ImageShow
from colorsys import rgb_to_hls

# Returns a dictionary of the parsed arguments, pass None as an argument to
# default to sys.argv
def get_args(argv):
    parser = argparse.ArgumentParser(description='Analisa folhas de macaúba',
                                       add_help=False)
    parser.add_argument('-h', '--help', action='help',
                        help='Mostra essa mensagem e fecha o programa')
    parser.add_argument('path', default='.',
                        help='Caminho para arquivo/pasta a ser analisado')
    parser.add_argument('--tamanho', metavar='TAMANHO',
                        help='Mostra o tamanho de cada parte da  folha, TAMANHO' +
                            ' deve estar no formato <altura>,<comprimento>, onde' +
                            ' os dois são valores reais. A medida é a mesma da' +
                            ' altura e comprimento')
    parser.add_argument('--mostrar-imagens', action='store_true',
                        help='Mostra todas as imagens processadas')
    parser.add_argument('--mostrar-mapas', action='store_true',
                        help='Mostra o mapa das imagens processadas')
    map = vars(parser.parse_args(argv))
    if map['tamanho'] and len(map['tamanho'].split(',')) == 2:
        nums = map['tamanho'].split(',')
        map['tamanho'] = float(nums[0]) * float(nums[1])
    return map

def scan_recursive(path):
    if not os.path.exists(path):
        raise ValueError('File does not exist')
    elif os.path.isfile(path):
        yield scan(path)
    elif os.path.isdir(path):
        for newpath in os.listdir(path):
            yield from scan_recursive(os.path.join(path, newpath))

def scan(path):
    try:
        img = Image.open(path)
    except:
        return
    imgmap = Image.new(img.mode, img.size)

    # scans image ands fills the map of it
    stats = {'good':0, 'bad':0}
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pixel = img.getpixel((x, y)) # get's pixel's RGB values
            try:
                hsl_pixel = rgb_to_hls(pixel[0], pixel[1], pixel[2])
            except (ZeroDivisionError, ValueError):
                imgmap.putpixel((x,y), value=(0,0,255))
                continue
            if pixel[1] > pixel[0]-10 and pixel[1] > pixel[2]-10 and hsl_pixel[0] < 150:
                stats['good'] += 1
                imgmap.putpixel((x,y), value=(0,255,0))

            elif pixel[0] > pixel[1] and pixel[0] > pixel[2]:
                stats['bad'] += 1
                imgmap.putpixel((x,y), value=(255,0,0))
            else:
                imgmap.putpixel((x,y), value=(0,0,255))

    return {'good':stats['good'], 'bad':stats['bad'],
            'path':path, 'img':img, 'imgmap':imgmap}

# Displays
def display(stat, args):
    pixtot = stat['good'] + stat['bad']
    size = stat['img'].size[0] * stat['img'].size[1]

    print('imagem {0}:'.format(stat['path']))
    print('saudável: {:.3f}%'.format(stat['good'] / pixtot * 100))
    print('doente: {:.3f}%'.format(stat['bad'] / pixtot * 100))

    # ImageShow.show() was not working for me on linux. This is somewhat of a temporary fix
    viewer = ImageShow.DisplayViewer() if os.name == 'posix' else ImageShow

    if args['tamanho']:
        print('Área saúdavel: {:.3f}'.format(stat['good'] / size * args['tamanho']))
        print('Área doente: {:.3f}'.format(stat['bad'] / size * args['tamanho']))
    if args['mostrar_imagens'] or (args['interativo'] and input('mostrar imagem (s/n)?: ').strip().lower() == 's'):
        viewer.show(stat['img'])
    if args['mostrar_mapas'] or (args['interativo'] and input('mostrar mapa (s/n)?: ').strip().lower() == 's'):
        viewer.show(stat['imgmap'])
    print()

    stat['img'].close()
    stat['imgmap'].close()

# Runs in interactive mode
def run_interactive():
    while True:
        cmd = input('cmd: ').strip()
        if cmd.lower() == "sair":
            exit()
        args = get_args(shsplit(cmd))
        args['interativo'] = True
        for st in scan_recursive(args['path']):
            display(st, args)
        print()

if __name__ == '__main__':
    try:
        if len(argv) == 1:
            run_interactive()
        args = get_args(None)
        args['interativo'] = False
        for st in scan_recursive(args['path']):
            display(st, args)
    except KeyboardInterrupt:
        exit('\n')

#!/usr/bin/env python
import os
import argparse
from PIL import Image
from colorsys import rgb_to_hls

# Returns a dictionary with the arguments passed to the program
def get_args():
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
    map = vars(parser.parse_args())
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

def display(stat, args):
    pixtot = stat['good'] + stat['bad']
    size = stat['img'].size[0] * stat['img'].size[1]

    print('imagem {0}:'.format(stat['path']))
    print('saudável: {:.3f}%'.format(stat['good'] / pixtot * 100))
    print('doente: {:.3f}%'.format(stat['bad'] / pixtot * 100))

    if 'tamanho' in args:
        print('Área saúdavel: {:.3f}'.format(stat['good'] / size * args['tamanho']))
        print('Área doente: {:.3f}'.format(stat['bad'] / size * args['tamanho']))
    print()

    stat['img'].close()
    stat['imgmap'].close()

def scan(path):
    try:
        img = Image.open(path)
    except:
        return
    imgmap = Image.new(img.mode, img.size)

    # scans image to fill the img map
    stats = {'good':0, 'bad':0}
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            pixel = img.getpixel((x, y)) # get's pixel (RGB)
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

if __name__ == '__main__':
    args = get_args()
    for st in scan_recursive(args['path']):
        display(st, args)

#!/usr/bin/env python
import os
from PIL import Image
from colorsys import rgb_to_hls
from sys import argv

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
            # good
            if pixel[1] > pixel[0]-10 and pixel[1] > pixel[2]-10 and hsl_pixel[0] < 150:
                stats['good'] += 1
                imgmap.putpixel((x,y), value=(0,255,0))

            elif pixel[0] > pixel[1] and pixel[0] > pixel[2]:
                    stats['bad'] += 1
                    imgmap.putpixel((x,y), value=(255,0,0))
            else: # none
                imgmap.putpixel((x,y), value=(0,0,255))

    return {'stats':stats, 'img':img, 'imgmap':imgmap}

if __name__ == "__main__":
    print(scan(argv[1]))

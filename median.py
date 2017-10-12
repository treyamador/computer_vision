# medium filter algorithm
from PIL import Image
import numpy as np
from copy import deepcopy
import sys


def init_img(filepath):
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    img = np.asarray(Image.open(filepath))
    pixels = np.array([[col[0] for col in row] for row in img])
    return pixels


def save_img(filepath,pixels):
    img = Image.fromarray(pixels)
    img.save(filepath)


def median(a,n):
    a.sort()
    return a[n]


# good median blur, probably
def apply_filter(img,dim):
    off = int(dim/2)
    fltrd = deepcopy(img)
    w = [0 for x in range(dim*dim)]
    n = int((dim*dim)/2+1)
    for i in range(off,len(img)-off):
        for j in range(off,len(img[i])-off):
            for s in range(i-off,i+off+1):
                for t in range(j-off,j+off+1):
                    w[(s-i+off)*dim+(t-j+off)] = img[s][t]
            fltrd[i][j] = median(w,n)
    return fltrd


def driver():
    size = 3
    img = init_img('img/sample.jpg')
    fltrd = apply_filter(img,size)
    save_img('img/sample_out.jpg',fltrd)


if __name__ == '__main__':
    driver()


# median filter
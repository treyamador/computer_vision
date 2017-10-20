from copy import deepcopy
from PIL import Image
import numpy as np
import math
from math import radians
from math import degrees
import time
import sys
import scipy
from scipy.ndimage.filters import gaussian_filter



def init_img(filepath):
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    img = np.asarray(Image.open(filepath).convert('L'))
    pixels = np.array(img)
    return pixels


def new_pixels(img):
    return np.zeros(shape=(len(img),len(img[0])),dtype=np.uint8)


def new_gradient(img):
    return np.zeros(shape=(len(img),len(img[0])))


def gen_kernels():
    kx = [[1,0,-1],[2,0,-2],[1,0,-1]]
    ky = [[1,2,1],[0,0,0],[-1,-2,-1]]
    return kx,ky


def compass():
    return [(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1)]


def round_angle(rad):
    deg = degrees(rad)
    if -22.5 <= deg <= 22.5:
        return 0,1
    elif 22.5 < deg <= 67.5:
        return 1,1
    elif -67.5 <= deg < -22.5:
        return 1,-1
    elif 67.5 < deg <= 112.5:
        return 1,0
    elif -112.5 <= deg < -67.5:
        return 1,0
    elif 112.5 < deg <= 157.5:
        return 1,-1
    elif -157.5 <= deg < -112.5:
        return 1,0
    elif 157.5 < deg <= 180.0:
        return 0,1
    elif -180.0 <= deg < -157.5:
        return 1,1
    else:
        return 0,1


def are_similar(a,b):
    if len(a) != len(b) or len(a[0]) != len(b[0]):
        return False
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] != b[i][j]:
                return False
    return True


def gaussian_smooth(img,dim):
    off = int(dim/2)
    fltrd = new_pixels(img)
    for i in range(off,len(img)-off):
        for j in range(off,len(img[i])-off):
            fltr_sum = 0
            for s in range(i-off,i+off+1):
                for t in range(j-off,j+off+1):
                    fltr_sum += img[s][t]
            fltrd[i][j] = fltr_sum/(dim*dim)
    return fltrd


def cv_gauss_smooth(img):
    return gaussian_filter(img,1)


def sobel_filter(img):
    dx = new_gradient(img)
    dy = new_gradient(img)
    kx,ky = gen_kernels()
    for i in range(1,len(img)-1):
        for j in range(1,len(img[i])-1):
            s,t = 0.0,0.0
            for m in range(len(kx)):
                for n in range(len(kx[m])):
                    s += img[i+m-1][j+n-1] * kx[m][n]
                    t += img[i+m-1][j+n-1] * ky[m][n]
            dx[i][j] = s
            dy[i][j] = t
    return dx,dy


def derivative_xy(img):
    dx = new_gradient(img)
    dy = new_gradient(img)
    k = [1,-1]
    for i in range(1,len(img)-1):
        for j in range(1,len(img[i])-1):
            dx[i][j] = (k[0]*img[i][j]+k[1]*img[i][j+1])
            dy[i][j] = (k[0]*img[i][j]+k[1]*img[i+1][j])
    return dx,dy


def gradient_magnitude(dx,dy):
    rho = new_pixels(dx)
    theta = new_gradient(dx)
    for i in range(len(dx)):
        for j in range(len(dx[i])):
            rho[i][j] = math.sqrt(math.pow(dx[i][j],2)+math.pow(dy[i][j],2))
            theta[i][j] = math.atan2(dy[i][j],dx[i][j])
    return rho,theta


def non_max_suppress(rho,theta):
    for i in range(1,len(theta)-1):
        for j in range(1,len(theta[i])-1):
            p,q = round_angle(theta[i][j])
            if rho[i][j] < rho[i+p][j+q] or rho[i][j] < rho[i-p][j-q]:
                rho[i][j] = 0
    return rho


def hysteresis(rho,theta,high,low):
    edge = new_pixels(rho)
    for i in range(1,len(rho)-1):
        for j in range(1,len(rho[i])-1):
            if rho[i][j] > high:
                edge[i][j] = 255
            elif rho[i][j] < low:
                edge[i][j] = 0
            else:
                p,q = round_angle(theta[i][j])
                if rho[i+p][j+q] > high or rho[i-p][j-q] > high:
                    edge[i][j] = 255
                if rho[i+p][j+q] < low or rho[i-p][j-q] < low:
                    edge[i][j] = 0
    return edge


def print_matrix(matrix):
    for row in matrix:
        for pixel in row:
            print(pixel,end=' ')
        print('')


def save_img(filepath,pixels):
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    t = filepath.split('.')
    filepath = '.'.join(t[:-1])+'_canny.'+t[-1]
    img = Image.fromarray(pixels)
    img.save(filepath)


def driver():
    filepath = 'img/valve.png'
    img = init_img(filepath)
    smt = gaussian_smooth(img,3)
    sx,sy = sobel_filter(smt)
    rho,theta = gradient_magnitude(sx,sy)
    save_img('img/valve_magnitude.png',rho)
    thin = non_max_suppress(rho,theta)
    save_img('img/valve_suppressed.png',thin)
    #edge = hysteresis(thin,theta,20,10)
    #save_img('img/valve_canny.png',edge)



if __name__ == '__main__':
    driver()









# canny filter

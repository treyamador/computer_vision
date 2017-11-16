# image blending
# this works!



'''

import sys
import os
import numpy as np
import cv2
import scipy
from scipy.stats import norm
from scipy.signal import convolve2d
import math

def split_rgb(image):
  red = None
  green = None
  blue = None
  (blue, green, red) = cv2.split(image)
  return red, green, blue

def generating_kernel(a):
  w_1d = np.array([0.25 - a/2.0, 0.25, a, 0.25, 0.25 - a/2.0])
  return np.outer(w_1d, w_1d)

def ireduce(image):
  out = None
  kernel = generating_kernel(0.4)
  outimage = scipy.signal.convolve2d(image,kernel,'same')
  out = outimage[::2,::2]
  return out

def iexpand(image):
  out = None
  kernel = generating_kernel(0.4)
  outimage = np.zeros((image.shape[0]*2, image.shape[1]*2), dtype=np.float64)
  outimage[::2,::2]=image[:,:]
  out = 4*scipy.signal.convolve2d(outimage,kernel,'same')
  return out

def gauss_pyramid(image, levels):
  output = []
  output.append(image)
  tmp = image
  for i in range(0,levels):
    tmp = ireduce(tmp)
    output.append(tmp)
  return output

def lapl_pyramid(gauss_pyr):
  output = []
  k = len(gauss_pyr)
  for i in range(0,k-1):
    gu = gauss_pyr[i]
    egu = iexpand(gauss_pyr[i+1])
    if egu.shape[0] > gu.shape[0]:
       egu = np.delete(egu,(-1),axis=0)
    if egu.shape[1] > gu.shape[1]:
      egu = np.delete(egu,(-1),axis=1)
    output.append(gu - egu)
  output.append(gauss_pyr.pop())
  return output

def blend(lapl_pyr_white, lapl_pyr_black, gauss_pyr_mask):
  blended_pyr = []
  k= len(gauss_pyr_mask)
  for i in range(0,k):
   p1= gauss_pyr_mask[i]*lapl_pyr_white[i]
   p2=(1 - gauss_pyr_mask[i])*lapl_pyr_black[i]
   blended_pyr.append(p1 + p2)
  return blended_pyr

def collapse(lapl_pyr):
  output = None
  output = np.zeros((lapl_pyr[0].shape[0],lapl_pyr[0].shape[1]), dtype=np.float64)
  for i in range(len(lapl_pyr)-1,0,-1):
    lap = iexpand(lapl_pyr[i])
    lapb = lapl_pyr[i-1]
    if lap.shape[0] > lapb.shape[0]:
      lap = np.delete(lap,(-1),axis=0)
    if lap.shape[1] > lapb.shape[1]:
      lap = np.delete(lap,(-1),axis=1)
    tmp = lap + lapb
    lapl_pyr.pop()
    lapl_pyr.pop()
    lapl_pyr.append(tmp)
    output = tmp
  return output

def main():

 image1 = cv2.imread('img/apple.jpg')
 image2 = cv2.imread('img/orange.jpg')
 mask = cv2.imread('img/mask512.jpg')
 r1= None
 g1= None
 b1= None
 r2= None
 g2= None
 b2= None
 rm= None
 gm = None
 bm = None

 (r1,g1,b1) = split_rgb(image1)
 (r2,g2,b2) = split_rgb(image2)
 (rm,gm,bm) = split_rgb(mask)

 r1 = r1.astype(float)
 g1 = g1.astype(float)
 b1 = b1.astype(float)

 r2 = r2.astype(float)
 g2 = g2.astype(float)
 b2 = b2.astype(float)

 rm = rm.astype(float)/255
 gm = gm.astype(float)/255
 bm = bm.astype(float)/255

 # Automatically figure out the size
 min_size = min(r1.shape)
 depth = int(math.floor(math.log(min_size, 2))) - 4 # at least 16x16 at the highest level.

 gauss_pyr_maskr = gauss_pyramid(rm, depth)
 gauss_pyr_maskg = gauss_pyramid(gm, depth)
 gauss_pyr_maskb = gauss_pyramid(bm, depth)

 gauss_pyr_image1r = gauss_pyramid(r1, depth)
 gauss_pyr_image1g = gauss_pyramid(g1, depth)
 gauss_pyr_image1b = gauss_pyramid(b1, depth)

 gauss_pyr_image2r = gauss_pyramid(r2, depth)
 gauss_pyr_image2g = gauss_pyramid(g2, depth)
 gauss_pyr_image2b = gauss_pyramid(b2, depth)

 lapl_pyr_image1r  = lapl_pyramid(gauss_pyr_image1r)
 lapl_pyr_image1g  = lapl_pyramid(gauss_pyr_image1g)
 lapl_pyr_image1b  = lapl_pyramid(gauss_pyr_image1b)

 lapl_pyr_image2r = lapl_pyramid(gauss_pyr_image2r)
 lapl_pyr_image2g = lapl_pyramid(gauss_pyr_image2g)
 lapl_pyr_image2b = lapl_pyramid(gauss_pyr_image2b)

 print([x.shape for x in lapl_pyr_image2r])
 print([x.shape for x in gauss_pyr_maskr])

 outpyrr = blend(lapl_pyr_image2r, lapl_pyr_image1r, gauss_pyr_maskr)
 outpyrg = blend(lapl_pyr_image2g, lapl_pyr_image1g, gauss_pyr_maskg)
 outpyrb = blend(lapl_pyr_image2b, lapl_pyr_image1b, gauss_pyr_maskb)

 outimgr = collapse(blend(lapl_pyr_image2r, lapl_pyr_image1r, gauss_pyr_maskr))
 outimgg = collapse(blend(lapl_pyr_image2g, lapl_pyr_image1g, gauss_pyr_maskg))
 outimgb = collapse(blend(lapl_pyr_image2b, lapl_pyr_image1b, gauss_pyr_maskb))
 # blending sometimes results in slightly out of bound numbers.
 outimgr[outimgr < 0] = 0
 outimgr[outimgr > 255] = 255
 outimgr = outimgr.astype(np.uint8)

 outimgg[outimgg < 0] = 0
 outimgg[outimgg > 255] = 255
 outimgg = outimgg.astype(np.uint8)

 outimgb[outimgb < 0] = 0
 outimgb[outimgb > 255] = 255
 outimgb = outimgb.astype(np.uint8)

 result = np.zeros(image1.shape,dtype=image1.dtype)
 tmp = []
 tmp.append(outimgb)
 tmp.append(outimgg)
 tmp.append(outimgr)
 result = cv2.merge(tmp,result)
 cv2.imwrite('img/blended.jpg', result)

if  __name__ =='__main__':
 main()


'''







import cv2
import numpy as np,sys


def init_img(filepath):
    return cv2.imread(filepath)


def gen_gaussian(orig):
    img = orig.copy()
    pyramid = [img]
    for i in range(6):
        img = cv2.pyrDown(img)
        pyramid.append(img)
    return pyramid


def gen_laplacian(gauss):
    pyramid = [gauss[5]]
    for i in range(5,0,-1):
        size = (gauss[i-1].shape[1],gauss[i-1].shape[0])
        GE = cv2.pyrUp(gauss[i],dstsize=size)
        laplace = cv2.subtract(gauss[i-1],GE)
        pyramid.append(laplace)
    return pyramid


def blend(laplace_a,laplace_b):
    # add mask here?
    laplace_sum = []
    for l_a,l_b in zip(laplace_a,laplace_b):
        rows,cols,dpt = l_a.shape
        l_s = np.hstack((l_a[:,0:int(cols/2)], l_b[:,int(cols/2):]))
        laplace_sum.append(l_s)

    laplace_pyramid = laplace_sum[0]
    for i in range(1,6):
        size = (laplace_sum[i].shape[1],laplace_sum[i].shape[0])
        laplace_pyramid = cv2.pyrUp(laplace_pyramid,dstsize=size)
        laplace_pyramid = cv2.add(laplace_pyramid,laplace_sum[i])
    return laplace_pyramid



def blend_mask(laplace_a,laplace_b,gauss_mask):
    # add mask here
    laplace_sum = []
    for l_a,l_b in zip(laplace_a,laplace_b):
        rows,cols,dpt = l_a.shape
        l_s = np.hstack((l_a[:,0:int(cols/2)], l_b[:,int(cols/2):]))
        laplace_sum.append(l_s)


    laplace_pyramid = laplace_sum[0]
    for i in range(1,6):
        size = (laplace_sum[i].shape[1],laplace_sum[i].shape[0])
        laplace_pyramid = cv2.pyrUp(laplace_pyramid,dstsize=size)
        laplace_pyramid = cv2.add(laplace_pyramid,laplace_sum[i])
    return laplace_pyramid


def driver():
    img_a = init_img('img/apple.jpg')
    img_b = init_img('img/orange.jpg')
    img_mask = init_img('img/mask512.jpg')
    gauss_a = gen_gaussian(img_a)
    gauss_b = gen_gaussian(img_b)
    gauss_mask = gen_gaussian(img_mask)
    gauss_mask = gauss_mask[-2::-1]
    laplace_a = gen_laplacian(gauss_a)
    laplace_b = gen_laplacian(gauss_b)

    #print([x.shape for x in gauss_a])
    #print([x.shape for x in laplace_a])
    #print([x.shape for x in gauss_mask])

    blended_img = blend_mask(laplace_a,laplace_b,gauss_mask)
    cv2.imwrite('img/apple_orange_blended.jpg',blended_img)


if __name__ == '__main__':
    driver()








# end of file

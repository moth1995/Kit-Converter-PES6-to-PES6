import os
import cv2
import glob
import itertools
import numpy as np
import argparse
import imutils
from datetime import datetime

#A ESTA FUNCION LE PASAS UNA IMAGEN Y EL ANGULO DE ROTACION Y LO ROTA 

def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)
    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


#abro la imagen y la muestro
#archivo ='all.png' #para debuggear
def convertir_kit(kit):
    #print(kit)
    stream = open(u'%s'% kit, "rb")
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
    #img = cv2.imread(kit, -1)
    #cv2.imshow('image', img)
    #print (img.shape)
    tamanio = img.shape
    if tamanio[0]==512 and tamanio[1]==512 and tamanio[2]==4:
        #print(kit)
        chunk_size = 4096
        with open(kit,'rb') as img_rf:
            with open(kit+'_pes6','wb') as wf_img:
                img_rf_chunk = img_rf.read(chunk_size)
                while len(img_rf_chunk) >0:
                    wf_img.write(img_rf_chunk)
                    img_rf_chunk = img_rf.read(chunk_size)
        shirt_short = img[0:323, 0:482]
        shirt_short = cv2.resize(shirt_short, (575,512))

        socks = img[323:512, 389:512]
        rotated_socks = rotate_bound(socks,270)
        rotated_socks = cv2.resize(rotated_socks, (240,162))

        sleeves = img[322:512 ,  0:390]
        sleeves = cv2.resize(sleeves, (450,350))

        captain = img[180:221, 482:512]
        captain = cv2.resize(captain, (51,60))

        collar = img[0:180, 482:512]
        collar = cv2.resize(collar, (58,164))

        u_short = img[208:251, 140:184]
        u_short = cv2.resize(u_short, (104,104))


        img1 = cv2.imread('template_1024x512.png', -1)
        img1[0 : 512 ,  0 : 575] = shirt_short
        img1[0 : 162 ,  733 : 973] = rotated_socks
        img1[162 : 512 ,  574 : 1024] = sleeves
        img1[0 : 60 ,  973 : 1024] = captain
        img1[0 : 164 ,  678 : 736] = collar
        img1[0 : 104 ,  574 : 678] = u_short
        #cv2.imshow('image', img1)#descomentar esto si queres ver un preview de las imagenes convertidas
        #cv2.imwrite(kit, img1)
        is_success, im_buf_arr = cv2.imencode(".png", img1)
        im_buf_arr.tofile(kit)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        with open("conversor_kits_pes6_a_pes5_log.txt", "a+") as myfile:
            log=("[logfile]"+str(datetime.now())+" Actualmente el tamaño del archivo "+"'"+ kit +"'"+ str(tamanio[1])+"x"+str(tamanio[0])+" no es soportado. O bien su imagen no esta indexada, si el siguiente valor es 4 entonces si esta indexada VALOR="+str(tamanio[2])+"\n")
            myfile.write(log)
            #print("Actualmente el tamaño del archivo ","'", kit ,"'", tamanio[1],"x",tamanio[0]," no es soportado\nO bien su imagen no esta indexada, si el siguiente valor es 4 entonces si esta indexada VALOR=",tamanio[2])

def getFilenames(exts):
    fnames = [glob.glob(ext) for ext in exts]
    fnames = list(itertools.chain.from_iterable(fnames))
    return fnames

exts = ["*.png","*/*.png","*/*/*.png","*/*/*/*.png","*/*/*/*/*.png"]
archivos = getFilenames(exts)
#print(archivos)
for archivo in archivos:
    #print("debugg "+ archivo)
    convertir_kit(archivo)
print("todos sus kits fueron convertidos, revise el archivo log.txt para mas informacion :)")

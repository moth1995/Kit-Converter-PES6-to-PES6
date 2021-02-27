import cv2
import glob
import itertools
import numpy as np
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pathlib import Path

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

def convertir_txt(configfile):
    model28=['model=28\n','model =28\n', 'model = 28\n', 'model= 28\n']
    with open(configfile, 'r') as file :
        filedata = file.readlines()
    for (i, line) in enumerate(filedata):
        if line in model28:
            filedata[i]='model = 0\n'
    with open(configfile, 'w') as file:
        file.writelines( filedata )


def convertir_kit_pes5(kit):
    if Path(kit).suffix=='.txt':
        convertir_txt(kit)
    else:
        stream = open(u'%s'% kit, "rb")
        bytes = bytearray(stream.read())
        numpyarray = np.asarray(bytes, dtype=np.uint8)
        img = cv2.imdecode(numpyarray, cv2.IMREAD_UNCHANGED)
        tamanio = img.shape
        if tamanio[0]==512 and tamanio[1]==512 and tamanio[2]==4:
            '''chunk_size = 4096
            with open(kit,'rb') as img_rf:
                with open(kit+'_pes6','wb') as wf_img:
                    img_rf_chunk = img_rf.read(chunk_size)
                    while len(img_rf_chunk) >0:
                        wf_img.write(img_rf_chunk)
                        img_rf_chunk = img_rf.read(chunk_size)'''
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


            img1 = cv2.imread(template, -1)
            img1[0 : 512 ,  0 : 575] = shirt_short
            img1[0 : 162 ,  733 : 973] = rotated_socks
            img1[162 : 512 ,  574 : 1024] = sleeves
            img1[0 : 60 ,  973 : 1024] = captain
            img1[0 : 164 ,  678 : 736] = collar
            img1[0 : 104 ,  574 : 678] = u_short
            is_success, im_buf_arr = cv2.imencode(".png", img1)
            if is_success:
                im_buf_arr.tofile(kit)
            else:
                with open(folder_selected+r"\log.txt", "a+") as myfile:
                    log=("[logfile "+str(datetime.now())+"] the file "+"'"+ kit +"' returned error "+ is_success+"\n")
                    myfile.write(log)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            with open(folder_selected+r"\log.txt", "a+") as myfile:
                log=("[logfile "+str(datetime.now())+"] the size of "+"'"+ kit +"' "+ str(tamanio[1])+"x"+str(tamanio[0])+" is not supported or your image is not indexed, if the next value is 4 then your image is indexed VALUE="+str(tamanio[2])+"\n")
                myfile.write(log)



def getFilenames(exts):
    fnames = [glob.glob(ext) for ext in exts]
    fnames = list(itertools.chain.from_iterable(fnames))
    return fnames

def startbtn():
    if folder_selected!=r'' and Path(template).is_file():
        exts = [folder_selected+"*.png",
                folder_selected+"*/*.png",
                folder_selected+"*/*/*.png",
                folder_selected+"*/*/*/*.png",
                folder_selected+"*/*/*/*/*.png",]
        if check.get():
            exts = [folder_selected+"*.png",folder_selected+"*.txt",
                    folder_selected+"*/*.png",folder_selected+"*/*.txt",
                    folder_selected+"*/*/*.png",folder_selected+"*/*/*.txt",
                    folder_selected+"*/*/*/*.png",folder_selected+"*/*/*/*.txt",
                    folder_selected+"*/*/*/*/*.png",folder_selected+"*/*/*/*/*.txt"]
        archivos = getFilenames(exts)
        for archivo in archivos:
            convertir_kit_pes5(archivo)
        messagebox.showinfo(title=app_name, message='All of your kits were converted please check log.txt for more info')
    elif folder_selected==r'':
        messagebox.showerror(title=app_name, message='Please select your uni folder!')
    elif not Path(template).is_file():
        messagebox.showerror(title=app_name, message='Template not found!')

def select_a_folder():
    global folder_selected
    global follbl
    follbl.destroy()
    folder_selected = filedialog.askdirectory(initialdir=r".",title='Please select your uni')
    if folder_selected:
        folder_selected=folder_selected.replace('/', '\\')
        follbl=Label(root,text=folder_selected)
        follbl.place(x=0,y=180)


def close():
    root.destroy()

def debug():
    debug=filedialog.askopenfilename(initialdir=r'.',title='Selecciona imagen para debug', filetypes=[('all files', '*')])
    img = cv2.imread(debug, -1)
    tamanio = img.shape
    print(img.shape)
    print(tamanio[0], tamanio[1])
    #Select ROI
    r = cv2.selectROI(img)
    print(r)
    #Crop image
    imCrop = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    cv2.imshow('image', imCrop)#descomentar esto si queres ver un preview de las imagenes convertidas
    print(int(r[1]) ,':' ,int(r[1]+r[3]), ', ', int(r[0]), ':', int(r[0]+r[2]))


app_name='PES5 kits converter from PES6 kits'
root = Tk()
root.title(app_name)

#con el codigo de abajo definimos el tamaño del formulario y tambien hacemos que se posicione en el centro de la pantalla

w = 400 # width for the Tk root
h = 200 # height for the Tk root
# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen
# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)
# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))
folder_selected=r''
template=r'.\template_pes5_1024x512.png'
#definimos variables para los elementos en el formulario
#debugbtn=Button(root, text='Debug', command=debug)
check=IntVar()
checkbox_model=Checkbutton(root, text="Set model = 0",variable=check)
selfolbtn=Button(root, text='Select an uni Folder',command=select_a_folder)
follbl=Label(root)
convkitbtn=Button(root, text='Convert Kits',command=startbtn)
exitbtn=Button(root, text='Exit',command=close)
#posicionamos todo lo definido arriba en el formulario
selfolbtn.place(x=140,y=50)
convkitbtn.place(x=160,y=110)
#debugbtn.place(x=180,y=360)
exitbtn.place(x=180,y=140)
checkbox_model.place(x=140,y=80)
#con esto seteamos para que el formulario sea fijo
root.resizable(False, False)
root.mainloop()
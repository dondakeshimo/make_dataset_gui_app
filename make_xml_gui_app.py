# -*- coding: utf-8 -*-

import sys
import os
from Tkinter import *
from tkMessageBox import *
from PIL import Image, ImageTk
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom


# pathの設定と画像拡張子の設定
my_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(my_dir)
img_extension = [".png", ".jpg"]


# 写真のサイズ調整
def getSize(tup):
    x, y = tup
    ratio_x = float(x / cvs_w)
    ratio_y = float(y / cvs_h)
    if (ratio_x <= 1 and ratio_y<= 1):
        return (1, x, y)
    elif ratio_x > ratio_y:
        return (ratio_x, int(cvs_w), int(y/ratio_x))
    else:
        return (ratio_y, int(x/ratio_y), int(cvs_h))


class MainWindow():
    def __init__(self,main):
        main.geometry("%dx%d+0+0" % (scr_w, scr_h))

        self.canvas = Canvas(main, width=cvs_w, height=cvs_h)
        self.canvas.grid(row=0, column=0, columnspan=6, rowspan=22)

        # 画像ファイルの情報を一気にself.my_imagesに格納,list内dictの入れ子構造
        self.my_images=[]
        self.file_num = 0
        for img in os.listdir("./images"):
            for ext in img_extension:
                if img.endswith(ext):
                    original = Image.open("./images/"+img)
                    img_org_w, img_org_h = original.size
                    ratio, img_w, img_h = getSize(original.size)
                    resized = original.resize((img_w, img_h), Image.ANTIALIAS)
                    self.my_images.append({
                        "image":    ImageTk.PhotoImage(resized),
                        "name":     img,
                        "size":     (img_w, img_h),
                        "org_size": (img_org_w, img_org_h),
                        "ratio":    ratio
                    })

        # 初期化群
        self.my_image_number = 0
        self.person_counter = 0
        self.person_name = "Person"
        self.person_coords = []

        # canvasにイベントのバインドと画像埋め込み
        self.canvas.bind("<Button-1>", self.pressButton)
        self.canvas.bind("<Button1-Motion>", self.draggingButton)
        self.canvas.bind("<ButtonRelease-1>", self.releaseButton)

        self.image_on_canvas = self.canvas.create_image(
            0, 0, anchor=NW, image=self.my_images[self.my_image_number]["image"])

        # 右側の各ボタンの作成
        self.button_next = Button(
            main, text="Next >>", command=self.onNextButton, width=5, height=1)
        self.button_next.grid(row=20, column=8)
        self.button_back = Button(
            main, text="<< Back", command=self.onBackButton, width=5, height=1)
        self.button_back.grid(row=20, column=6)
        self.button_save = Button(
            main, text="Save", command=self.onSaveButton, width=5, height=1)
        self.button_save.grid(row=20, column=7)
        self.button_clear = Button(
            main, text="Clear", command=self.onClearButton, width=5, height=1)
        self.button_clear.grid(row=19, column=7)

        self.message_num = Entry(width=40)
        self.message_num.insert(
            END, ("This image is " + self.my_images[self.my_image_number]["name"]))
        self.message_num.grid(row=1, column=6, columnspan=3)

        self.frame = Frame(main, width=scr_w-cvs_w-10, height=scr_h-20)
        self.frame.grid(row=4, column=6, rowspan=13, columnspan=3)

        self.checkbuttons = {"bool": [0, ], "chbutton": [0, ]}
        for num in range(1,20):
            b = BooleanVar()
            b.set(False)
            self.checkbuttons["bool"].append(b)
            c = Checkbutton(
                text="Person"+str(num), variable=self.checkbuttons["bool"][num])
            c.pack(in_=self.frame)
            c.lower()
            self.checkbuttons["chbutton"].append(c)


# 以降、callback関数

    # canvas内でクリックした時
    def pressButton(self, event):
        self.press_x = event.x
        self.press_y = event.y

        # 矩形描画
        self.temp_rectangle = self.canvas.create_rectangle(
            self.press_x, self.press_y, self.press_x+1,
            self.press_y+1,tags="temp")


    # canvas内でドラッグした時
    def draggingButton(self, event):
        self.now_x = event.x
        self.now_y = event.y

        if self.press_x < self.now_x:
            self.xmin = self.press_x
            self.xmax = self.now_x
        else:
            self.xmin = self.now_x
            self.xmax = self.press_x
        if self.press_y < self.now_y:
            self.ymin = self.press_y
            self.ymax = self.now_y
        else:
            self.ymin = self.now_y
            self.ymax = self.press_y

        self.canvas.coords(self.temp_rectangle,
            self.xmin, self.ymin, self.xmax, self.ymax)


    # canvas内でクリックを離した時
    def releaseButton(self, event):
        # temp_rectangleの消去
        self.canvas.delete(self.temp_rectangle)

        self.release_x = event.x
        self.release_y = event.y

        if self.press_x < self.release_x:
            self.xmin = self.press_x
            self.xmax = self.release_x
        else:
            self.xmin = self.release_x
            self.xmax = self.press_x
        if self.press_y < self.release_y:
            self.ymin = self.press_y
            self.ymax = self.release_y
        else:
            self.ymin = self.release_y
            self.ymax = self.press_y

        self.person_counter += 1

        # 矩形描画
        self.canvas.create_rectangle(
            self.xmin, self.ymin, self.xmax, self.ymax, tags="Person")
        self.canvas.create_text(
            self.xmin+5, self.ymin+5,
            text=str(self.person_counter), tags="Person")

        # 矩形の頂点座標の格納とチェックボタンの呼び出し
        r = self.my_images[self.my_image_number]["ratio"]
        self.person_coords.append(
            (int(self.xmin*r), int(self.ymin*r), int(self.xmax*r), int(self.ymax*r)))
        self.checkbuttons["chbutton"][self.person_counter].lift()


    # [<<Back]を押した時
    def onBackButton(self):
        if self.my_image_number == 0:
            showinfo(message="This is the first image")
            return
        else:
            self.my_image_number -= 1

        # canvas内情報の更新
        self.canvas.delete("Person")
        self.person_counter = 0
        self.person_coords = []
        self.canvas.itemconfig(
            self.image_on_canvas, image=self.my_images[self.my_image_number]["image"])

        # チェックボタンを隠す
        for num in range(1,11):
            self.checkbuttons["chbutton"][num].lower()

        # 画像の名前更新
        self.message_num.delete(0, END)
        self.message_num.insert(
            END, ("This image is " + self.my_images[self.my_image_number]["name"]))


    # [Next>>]を押した時
    def onNextButton(self):
        self.my_image_number += 1

        if self.my_image_number == len(self.my_images):
            showinfo(message="This is the last image")
            return

        # canvas内情報の更新
        self.canvas.delete("Person")
        self.person_counter = 0
        self.person_coords = []
        self.canvas.itemconfig(
            self.image_on_canvas, image=self.my_images[self.my_image_number]["image"])

        # チェックボタンを隠す
        for num in range(1,11):
            self.checkbuttons["chbutton"][num].lower()

        # 画像の名前更新
        self.message_num.delete(0, END)
        self.message_num.insert(
            END, ("This image is " + self.my_images[self.my_image_number]["name"]))


    # [Save]を押した時
    def onSaveButton(self):
    # 画像と同名のxmlファイルを作成
        self.fout = open(
            "./annotations/"+self.my_images[self.my_image_number]["name"][0:-4]+".xml", "wt")
        # xmlのテンプレを代入
        self.xml = xmlMaker(
                self.my_images[self.my_image_number]["name"],
                self.my_images[self.my_image_number]["org_size"])

        # チェックボタンで選択したPersonをxmlファイルに記入
        for (i, size) in enumerate(self.person_coords):
            if self.checkbuttons["bool"][i+1].get()==True:
                self.xml.object_name = SubElement(self.xml.object, "name")
                self.xml.object_name.text = "Person"
                self.xml.object_bndbox = SubElement(self.xml.object, "bndbox")
                self.xml.bndbox_xmin = SubElement(self.xml.object_bndbox, "xmin")
                self.xml.bndbox_xmin.text = str(size[0])
                self.xml.bndbox_ymin = SubElement(self.xml.object_bndbox, "ymin")
                self.xml.bndbox_ymin.text = str(size[1])
                self.xml.bndbox_xmax = SubElement(self.xml.object_bndbox, "xmax")
                self.xml.bndbox_xmax.text = str(size[2])
                self.xml.bndbox_ymax = SubElement(self.xml.object_bndbox, "ymax")
                self.xml.bndbox_ymax.text = str(size[3])

        self.fout.write(self.xml.prettify(self.xml.top))
        self.fout.close()

        # 保存されたことを伝える
        showinfo(message="Xml file is saved")


    # [Clear]を押した時
    def onClearButton(self):
        # canvas内情報の更新
        self.canvas.delete("Person")
        self.person_counter = 0
        self.person_coords = []
        self.canvas.itemconfig(
            self.image_on_canvas, image=self.my_images[self.my_image_number]["image"])

        # チェックボタンを隠す
        for num in range(1,11):
            self.checkbuttons["chbutton"][num].lower()


# xmlファイルのテンプレと記入用class
class xmlMaker():
    def __init__(self, image_name, size):
        self.top = Element("annotation")
        self.folder = SubElement(self.top, "folder")
        self.folder.text = my_dir
        self.filename = SubElement(self.top, "filename")
        self.filename.text = image_name
        self.source = SubElement(self.top, "source")
        self.source_annotation = SubElement(self.source, "annotation")
        self.source_annotation.text = "Annotated Person Datebase"
        self.size = SubElement(self.top, "size")
        self.width = SubElement(self.size, "width")
        self.width.text = str(size[0])
        self.height = SubElement(self.size, "height")
        self.height.text = str(size[1])
        self.depth = SubElement(self.size, "depth")
        self.depth.text = "3"
        self.object = SubElement(self.top, "object")


    def prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


if __name__=="__main__":
    root = Tk()
    root.title(u"機械がお勉強をするための教材を人間様が作ってやりましょう")
    scr_w, scr_h = root.winfo_screenwidth(), root.winfo_screenheight()
    cvs_w, cvs_h = scr_w*2/3, scr_h-10
    MainWindow(root)
    root.mainloop()

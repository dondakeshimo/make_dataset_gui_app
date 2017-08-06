# -*- coding: utf-8 -*-

import sys
import os

# pathの設定と画像拡張子の設定
my_dir = os.path.abspath(os.path.dirname(__file__))
img_dir = os.path.join(my_dir, "images")

for num, img in enumerate(os.listdir(img_dir), start=1):
    if img.endswith("png"):
        str_num = u"%06d" % num
        old_name = os.path.join(img_dir, img)
        new_name = os.path.join(img_dir, u"Person"+str_num+u".png")
        os.rename(old_name, new_name)
    else:
        print(img + u"はpngファイルではありません")
        print(u"ナンバリングに失敗したのでpngファイルのみにして再度実行してください")

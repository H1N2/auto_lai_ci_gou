# coding=utf-8


import os
import shutil

from PIL import Image
from PIL import ImageFile

from logger import log

ImageFile.LOAD_TRUNCATED_IMAGES = True

CHAR_IMG_WIDTH = 28
CHAR_IMG_HEIGHT = 60
REGIONS = [(38, 0, 38 + CHAR_IMG_WIDTH, CHAR_IMG_HEIGHT),
           (64, 0, 64 + CHAR_IMG_WIDTH, CHAR_IMG_HEIGHT),
           (86, 0, 86 + +CHAR_IMG_WIDTH, CHAR_IMG_HEIGHT),
           (116, 0, 116 + +CHAR_IMG_WIDTH, CHAR_IMG_HEIGHT)]

BOTTOM_BLANK_IMG = './base_pic/blank/blank_30_12.jpg'

file_index = 0


def corp(src, des, regions):
    """
    按定义的区域将文件夹下的图片裁剪为多个图片，存于指定目录
    :param src: 需要剪裁的图片所在路径
    :param des: 剪切后的图片保存路径
    :param regions: 剪裁区域
    :return:
    """
    global file_index
    for root, dirs, files in os.walk(src):
        for file in files:
            with Image.open(src + file) as image:
                for region in regions:
                    img = Image.new('RGB', (CHAR_IMG_WIDTH, CHAR_IMG_HEIGHT))
                    crop_img = image.crop(region)
                    img.paste(crop_img, (0, 0))
                    # 由于PIL未完全读取图片数据（OSError: image file is truncated (27 bytes not processed)）
                    # 导致剪切后的图片底部有12个像素高的黑色长条
                    # 强制性使用12像素高的空白图片（blank_30_12.jpg）来填充覆盖此黑色部分
                    bottom_img = Image.open(BOTTOM_BLANK_IMG)
                    img.paste(bottom_img, (0, 48))

                    img.save(des + str(file_index) + '.jpg')
                    file_index = file_index + 1


def move_sorted_pics(src, des):
    """
    将分类过的图片剪切到指定目标目录
    num 文件夹对应放置数字子文件夹
    la 文件夹对应放置小写字母子文件夹
    ua 文件夹对应放置大写字母子文件夹
    :param src: 分类过的图片原始路径
    :param des: 目标路径
    :return:
    """
    for r0, dirs, f0 in os.walk(src):
        for dir in dirs:
            for r1, d1, files in os.walk(src + '/' + dir):
                src_path = src + dir + '\\'
                if len(dir) == 2:
                    dir = dir[1:]

                dst_path = ''
                if dir.isdigit():
                    dst_path = des + '\\num\\' + dir + '\\'
                elif dir.islower():
                    dst_path = des + '\\la\\' + dir + '\\'
                elif dir.isupper():
                    dst_path = des + '\\ua\\' + dir + '\\'

                for file in files:
                    src = src_path + file

                    if not os.path.exists(dst_path):
                        os.makedirs(dst_path)
                        log('创建文件夹：' + dst_path)

                    dst = dst_path + file
                    log('移动文件：从{0}到{1}'.format(src, dst))
                    shutil.move(src, dst)


if __name__ == '__main__':
    src_path = r'E:\\BaiduNetdiskDownload\\1\\'
    des_path = r'E:\\BaiduNetdiskDownload\\2\\'
    base_pic_path = './base_pic/'
    corp(src_path, des_path, REGIONS)
    move_sorted_pics(des_path, base_pic_path)
    log('end')
    pass

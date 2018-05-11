# coding=utf-8
import os
import random
import numpy as np

from PIL import ImageFile
from PIL import Image

from logger import log
from ml.captcha_crack_baidu.image_corp import CHAR_IMG_WIDTH

ImageFile.LOAD_TRUNCATED_IMAGES = True

file_index = 0
CAPTCHA_CHAR_LEN = 4

CAPTCHA_IMG_WIDTH = 160
CAPTCHA_IMG_HEIGHT = 60

# 当前文件所在目录
ROOT_PATH = os.path.split(os.path.realpath(__file__))[0]

# 训练数据数字基本图片目录
BASIC_NUMBERS_PATH = ROOT_PATH + '/base_pic/num/'
# 训练数据小写字母基本图片目录
BASIC_LOWERCASE_ALPHABET_PATH = ROOT_PATH + '/base_pic/la/'
# 训练数据大写字母基本图片目录
BASIC_UPPERCASE_ALPHABET_PATH = ROOT_PATH + '/base_pic/ua/'
# 空白图片（间隙补充图）全路径
BLANK_PIC = ROOT_PATH + '/base_pic/blank/blank_2_60.jpg'
# 本地训练数据存放目录
TRAINING_DATA_PATH = ROOT_PATH + '/data/train_data/'


def get_dirs(path):
    for root, dirs, files in os.walk(path):
        return dirs


# 获取可用的数字集
NUMBERS = get_dirs(BASIC_NUMBERS_PATH)
log('数字字符集：{0}'.format(NUMBERS))
# 获取可用的小写字母集
LOWERCASE_ALPHABET = get_dirs(BASIC_LOWERCASE_ALPHABET_PATH)
log('小写字母集：{0}'.format(LOWERCASE_ALPHABET))
# 获取可用的大写字母集
UPPERCASE_ALPHABET = get_dirs(BASIC_UPPERCASE_ALPHABET_PATH)
log('大写字母集：{0}'.format(UPPERCASE_ALPHABET))
# 所有的验证码字符集
CHAR_SET = NUMBERS + LOWERCASE_ALPHABET + UPPERCASE_ALPHABET
log('所有字符集：{0}'.format(CHAR_SET))


def gen_random_list(li, length=CAPTCHA_CHAR_LEN):
    """
    从已知列表中随机抽取指定长度的元素（可重复）构成新的列表
    :param li: 原始列表
    :param length: 需要生成的随机列表长度
    :return: 新生成的随机列表
    """
    r = []
    for i in range(length):
        n = random.randint(0, len(li) - 1)
        r.append(li[n])

    return r


def gen_all_base_pic_name_list():
    """
    随机生成合成验证码图片所需的基本图片名列表
    :return: 构成验证码图片的基础图片列表
    """
    chars = gen_random_list(CHAR_SET)
    captcha_text = ''.join(chars)

    gap_num = int((160 - 4 * 28) / 2)
    gap_num_left = int(gap_num * 0.6)
    gap_num_right = gap_num - gap_num_left

    basic_pic = []
    for char in chars:
        if char.isupper():
            path = BASIC_UPPERCASE_ALPHABET_PATH + char
        elif char.islower():
            path = BASIC_LOWERCASE_ALPHABET_PATH + char
        elif char.isdigit():
            path = BASIC_NUMBERS_PATH + char

        # 随机获取基本元素图，将其路径存入basic_pic
        for root, dirs, files in os.walk(path):
            index = random.randint(0, len(files) - 1)
            basic_pic.append(path + '/' + files[index])

    # 将60%的间隙补充图补充到左边
    for i in range(gap_num_left):
        basic_pic.insert(0, BLANK_PIC)  # 头部插入

    # 将40%的间隙补充图补充到右边
    for i in range(gap_num_right):
        basic_pic.append(BLANK_PIC)  # 尾部插入

    return captcha_text, basic_pic


def gen_captcha(save=False):
    """
    生成验证码图片
    :param save: 是否保存到磁盘，缺省不保存
    :return: 验证码元组
             第一个元素为验证码字符标签
             第二个元素为验证码图像数组对象

    """
    captcha_text, base_pics = gen_all_base_pic_name_list()

    img = Image.new('RGB', (CAPTCHA_IMG_WIDTH, CAPTCHA_IMG_HEIGHT))
    x = 0
    for pic_file_path in base_pics:
        from_img = Image.open(pic_file_path)
        loc = (x, 0)
        img.paste(from_img, loc)
        if pic_file_path == BLANK_PIC:
            x = x + 2
        else:
            x = x + CHAR_IMG_WIDTH

    global file_index
    file_index = file_index + 1

    # 保存图片
    if save:
        if not os.path.exists(TRAINING_DATA_PATH):
            os.makedirs(TRAINING_DATA_PATH)
            log('创建文件夹：' + TRAINING_DATA_PATH)

        file_path = TRAINING_DATA_PATH + str(file_index) + '-' + captcha_text + '.jpg'
        img.save(file_path)

    captcha_image = np.array(img)
    return captcha_text, captcha_image


def gen_captchas(count):
    """
    批量生成验证码图片
    :param count: 要生成的验证码数量
    :return:
    """
    for i in range(count):
        gen_captcha(True)


if __name__ == '__main__':
    gen_captchas(10)
    log('end')
    pass

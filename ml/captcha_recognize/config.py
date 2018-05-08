# about captcha image
IMAGE_HEIGHT = 60
IMAGE_WIDTH = 160
CHAR_SETS = 'abcdefghijklmnpqrstuvwxyz0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ'
CLASSES_NUM = len(CHAR_SETS)
CHARS_NUM = 4
# for train
RECORD_DIR = './data'
TRAIN_FILE = 'train.tfrecords'
VALID_FILE = 'valid.tfrecords'

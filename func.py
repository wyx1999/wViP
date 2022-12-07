import matplotlib
import PyPDF2

matplotlib.use('Agg')

from nltk.stem import *
from nltk.corpus import wordnet


def read_pdf(filepath, text):
    pdfFileObj = open(filepath, 'rb')  # rw,r+都会出错
    # pdfFileObj = open(filename, 'r+',encoding="utf-8")
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

  #  print("pages cnt:", pdfReader.numPages)

    for i in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(i)
        dataStr = pageObj.extractText()

        #      print("current page index:", i)
        #       print("============text===============")
        text = text + dataStr


    pdfFileObj.close()
    return text


def transparence2white(img):
    sp = img.shape  # 获取图片维度
    width = sp[0]  # 宽度
    height = sp[1]  # 高度
    for yh in range(height):
        for xw in range(width):
            color_d = img[xw, yh]  # 遍历图像每一个点，获取到每个点4通道的颜色数据
            if color_d.size != 4:  # 如果图片只有三个通道，也是可以正常处理
                continue
            if color_d[3] == 0:  # 最后一个通道为透明度，如果其值为0，即图像是透明
                img[xw, yh] = [255, 255, 255, 255]  # 则将当前点的颜色设置为白色，且图像设置为不透明
    return img


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def binary_conversion(var: int):
    """
    二进制单位转换
    :param var: 需要计算的变量，bytes值
    :return: 单位转换后的变量，kb 或 mb
    """
    assert isinstance(var, int)
    if var <= 1024:
        return f'占用 {round(var / 1024, 2)} KB内存'
    else:
        return f'占用 {round(var / (1024 ** 2), 2)} MB内存'

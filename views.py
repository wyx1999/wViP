import os
import time
import json
from shutil import copyfile

from PIL import Image
import numpy as np
import docx
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
import base64
import io

import matplotlib

from wordcloud import WordCloud, ImageColorGenerator

from .enrichment import do_go, do_kegg, do_gesa, do_do
from .func import read_pdf, transparence2white, get_wordnet_pos

matplotlib.use('Agg')
from matplotlib import pyplot as plt

from nltk.tokenize import word_tokenize
from nltk.tokenize import MWETokenizer  # Multi-Word Expression
from nltk.stem import *
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag
import nltk


def set_cookie(request):
    x = request.POST.get('x')
    response = HttpResponse("OK")
    response.set_cookie("is_cookie", "True")
    if x == 'false':
        response.delete_cookie("is_cookie")

    return response


def index(request):
    """
     try:
        del request.session['mwe_text']
    except:
        print('没有字典session')
    try:
        del request.session['filetext']
    except:
        print('没有filetext session')

    """
    request.session.flush()
    stop_words = stopwords.words('english')
    punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%', '\'\'', '\'',
                    '`', '’', '‘', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                    '``', '-', '--', '|', '/', '/', '“', 'The', 'the', 'We', 'we']  # 自定义需要过滤的符号
    f = open('client/static/client/collection/example_stopwords.txt', 'r', encoding='utf-8')
    for l in f:
        l = l.rstrip()
        stop_words.append(l)
    stop_words.extend(punctuations)
    # print(stop_words)
    f.close()
    mwe = []
    f = open('client/static/client/collection/example_dictionary.txt', 'r', encoding='utf-8')
    for l in f:
        l = l.rstrip()
        mwe.append(l)
    f.close()

    request.session['stop_words'] = stop_words
    request.session['mwe_text'] = mwe
    # request.COOKIES("is_cookie", "false")

    is_cookie = request.COOKIES.get('is_cookie')
    if not is_cookie:
        is_cookie = 'false'
    return render(request, 'client/index.html', {'is_cookie': is_cookie})


def enrichment(request):
    is_cookie = request.COOKIES.get('is_cookie')
    if not is_cookie:
        is_cookie = 'false'
    return render(request, 'client/enrichment.html', {'is_cookie': is_cookie})


def documentation(request):
    is_cookie = request.COOKIES.get('is_cookie')
    if not is_cookie:
        is_cookie = 'false'
    return render(request, 'client/documentation.html', {'is_cookie': is_cookie})


def get_mwetokenizer(request):
    mwe_text = request.session.get('mwe_text', 'null')
    mwetokenizer = MWETokenizer([], separator=' ')
    if mwe_text == 'null':
        print(mwe_text)
    else:
        for i in mwe_text:
            sp = i.rstrip().split(' ')
            mwetokenizer.add_mwe(tuple(sp))
    return mwetokenizer


def nlp_1(request):
    text = request.POST.get('text')
    stamp = str(request.POST.get('stamp', '0'))
    if stamp != '0':
        file_path = os.path.join('client/media/' + stamp)
        filenames = os.listdir(file_path)
        for filename in filenames:
            text = text + '\n' + request.session.get(filename, '')
    is_stopwords = request.POST.get('is_stopwords')
    is_dictionary = request.POST.get('is_dictionary')
    word_case = request.POST.get('word_case')
    data = {}
    word_tokens = word_tokenize(text)

    if is_dictionary == 'true':
        mwetokenizer = get_mwetokenizer(request)
        word_tokens = mwetokenizer.tokenize(word_tokens)
    if is_stopwords == 'true':
        stop_words = request.session.get('stop_words', 'null')
        word_tokens = [w for w in word_tokens if not w in stop_words]

    word_tokens_lower = [item.lower() for item in word_tokens]

    if word_case == 'lowercase':
        word_tokens = word_tokens_lower

    lmtzr = WordNetLemmatizer()
    POS = pos_tag(word_tokens_lower)

    message = []
    for i in range(0, len(word_tokens)):
        a = [word_tokens[i]]
        tag = get_wordnet_pos(POS[i][1])
        a.append(tag)
        x = lmtzr.lemmatize(word_tokens[i], tag)
        a.append(x)

        message.append(a)
    request.session['message'] = message
    data['index'] = []
    print(len(message))
    data['index'] = list(range(1, int(len(message) / 10000) + 2, 1))
    data['message'] = message[0:10000]
    return JsonResponse(data)


def nlp1_goto(request):
    data = {}
    message = list(request.session.get('message', 'null'))
    x = int(request.POST.get('x'))
    l = int(len(message) / 10000) + 1

    if x < 1:
        x = 1
    elif x > l:
        x = l
    if x == l:
        data['message'] = message[(x - 1) * 10000:]
    else:
        data['message'] = message[(x - 1) * 10000:x * 10000]
    data['x'] = x
    return JsonResponse(data)


def nlp_2(request):
    message = list(request.session.get('message', 'null'))
    word_tokens = []
    for i in range(0, len(message)):
        word_tokens.append(message[i][2])

    data = {'message': []}

    if word_tokens != 'message':
        # word_tokens = word_tokens.split('/+/')

        stop_words = request.session.get('stop_words', 'null')
        word_tokens = [w for w in word_tokens if not w in stop_words]
        fdist = nltk.FreqDist(word_tokens)
        most_list = fdist.most_common(10000)
        wordcloud_list = []
        for w in most_list:
            dic = [w[0], w[1]]
            wordcloud_list.append(dic)
        data['message'] = wordcloud_list

    print(len(data['message']))
    return JsonResponse(data)


def tagging_change(request):
    data = {}
    x = int(request.POST.get('x'))
    trSeq = int(request.POST.get('trSeq'))
    tag = request.POST.get('tag')
    word = request.POST.get('word')

    lmtzr = WordNetLemmatizer()

    data['message'] = lmtzr.lemmatize(word, tag)
    message = request.session.get('message', 'null')
    l = int(len(message) / 10000) + 1
    if x < 1:
        x = 1
    elif x > l:
        x = l
    i = (x - 1) * 10000 + trSeq
    message[i][1] = tag
    message[i][2] = data['message']
    return JsonResponse(data)


def plot_wordcloud(request):
    timeticket = time.time()
    text = request.POST.get('text', '')
    #   stamp = str(request.POST.get('stamp', '0'))
    ##   if stamp != '0':
    #       file_path = os.path.join('client/media/' + stamp)
    #       filenames = os.listdir(file_path)
    #       for filename in filenames:
    #           text = text + '\n' + request.session.get(filename, '')
    frequency = request.POST.get('frequency', 'null')
    frequency = json.loads(frequency)

    if len(text.rstrip()) == 0:
        text = 'None'

    is_nlp = request.POST.get('is_nlp')
    is_mask = request.POST.get('is_mask')
    width = int(request.POST.get('width'))
    height = int(request.POST.get('height'))
    scale = float(request.POST.get('scale'))
    prefer_horizontal = float(request.POST.get('prefer_horizontal'))
    max_font_size = int(request.POST.get('max_font_size'))
    min_font_size = int(request.POST.get('min_font_size'))
    show_img = request.POST.get('show_img')
    font_type = request.POST.get('font_type')
    colormaps = request.POST.get('colormaps')
    ColorByMask = request.POST.get('ColorByMask')
    ColorBySize = request.POST.get('ColorBySize')
    ColorBySize_threshold = int(request.POST.get('ColorBySize_threshold'))

    data = {}
    color_mask = None
    relative_scaling = 0.5
    font_path = 'client/static/client/Fonts/' + font_type
    stop_words = request.session.get('stop_words', 'null')

    if is_mask == 'false':
        mask = None
    else:
        if show_img == 'custom':
            pic = request.session.get('custom', 'null')
            pic = np.array(pic)
        else:
            url = "client/static/client/img/" + show_img
            pic = np.array(Image.open(url))
        if ColorByMask == 'true':
            color_mask = ImageColorGenerator(pic)

        mask = transparence2white(pic)

    def test_color_func(word, font_size, position, orientation, font_path, random_state):
        r, g, b, alpha = plt.get_cmap(colormaps)(font_size / ColorBySize_threshold)
        return int(r * 255), int(g * 255), int(b * 255)

    wc = WordCloud(font_path=font_path, width=width, height=height, scale=scale,
                   prefer_horizontal=prefer_horizontal,
                   max_font_size=max_font_size, min_font_size=min_font_size, relative_scaling=relative_scaling,
                   mask=mask, mode='RGBA', background_color=None, stopwords=stop_words, colormap=colormaps, repeat=True)

    if is_nlp == 'true' and len(frequency) != 0:
        frequency = {k: int(v) for k, v in frequency.items()}
        wc.generate_from_frequencies(frequency)
    else:
        wc.generate(text)
    if ColorByMask == 'true' and ColorBySize == 'false':
        wc.recolor(color_func=color_mask)
    if ColorBySize == 'true':
        wc.recolor(color_func=test_color_func)
    plt.figure()  # 画图
    plt.imshow(wc)
    plt.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf)
    data['wordcloud_pic'] = base64.b64encode(buf.getvalue()).decode()
    url = "client/static/client/media/" + str(timeticket) + ".png"
    wc.to_file(url)
    plt.close()
    data['time'] = timeticket

    return JsonResponse(data)


def upload_maskImage(request):
    try:
        pic = request.FILES.get('files')

        image_byte = pic.read()
        image_base64 = str(base64.b64encode(image_byte))[2:-1]
        data = image_base64
        request.session['custom'] = np.array(Image.open(pic)).tolist()
    except:
        print('无文件')
        data = '无文件'

    return HttpResponse(data, 'image/png')


def upload_dictionary(request):
    data = {'mwe_text': []}
    try:
        file_object = request.FILES.get('files')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        file_name = file_object.name.split('.')[0]

        for chunk in file_object.chunks():
            l = chunk.decode().rstrip().split('\r\n')
            for i in l:
                data['mwe_text'].append(i)
    except:
        print('无文件')

    return JsonResponse(data)


def save_dictionary(request):
    mwe_text = request.POST.get('mwe_text')
    mwe_text = mwe_text.rstrip().split('\n')
    VALUE = request.session.get('mwe_text', 'null')
    if VALUE == 'null':
        request.session['mwe_text'] = mwe_text
    else:
        VALUE.extend(mwe_text)
        request.session['mwe_text'] = list(set(VALUE))

    data = {}
    return JsonResponse(data)


def search_dictionary(request):
    VALUE = request.session.get('mwe_text', 'null')
    data = {}

    if VALUE != 'null':
        data['record'] = list(set(VALUE))
    return JsonResponse(data)


def clear_dictionary(request):
    data = {}
    try:
        del request.session['mwe_text']
    except:
        print('没有字典session')
    return JsonResponse(data)


def upload_stopwords(request):
    data = {'stop_words': []}
    try:
        file_object = request.FILES.get('files')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        file_name = file_object.name.split('.')[0]

        for chunk in file_object.chunks():
            l = chunk.decode().rstrip().split('\r\n')
            for i in l:
                data['stop_words'].append(i)
    except:
        print('无文件')

    return JsonResponse(data)


def save_stopwords(request):
    stop_words = request.POST.get('stop_words')
    stop_words = stop_words.rstrip().split('\n')
    VALUE = request.session.get('stop_words', 'null')
    if VALUE == 'null':
        request.session['stop_words'] = stop_words
    else:
        VALUE.extend(stop_words)
        request.session['stop_words'] = list(set(VALUE))
    data = {}
    return JsonResponse(data)


def search_stopwords(request):
    VALUE = request.session.get('stop_words', 'null')

    data = {}
    if VALUE != 'null':
        data['record'] = list(set(VALUE))
    return JsonResponse(data)


def clear_stopwords(request):
    data = {}
    try:
        del request.session['stop_words']
    except:
        print('没有stopwords')
    return JsonResponse(data)


def single_upload(f, stamp):
    file_path = os.path.join('client/media/' + stamp + '/' + f.name)  # 拼装目录名称+文件名称

    with open(file_path, 'wb+') as destination:  # 写文件word
        for chunk in f.chunks():
            destination.write(chunk)
    destination.close()


def up_files(request):
    stamp = request.POST.get('stamp', '0')
    if stamp == '0':
        stamp = str(time.time())
        os.mkdir('client/media/' + stamp)
    data = {'stamp': stamp}
    files = request.FILES.getlist('filelist')  # 获得多个文件上传进来的文件列表。

    for f in files:
        single_upload(f, stamp)  # 处理上传来的文件
        filetext = ''
        suffix = f.name.split('.')[1]
        if suffix == 'docx':
            file = docx.Document('client/media/' + stamp + '/' + f.name)
            for para in file.paragraphs:
                if len(para.text) != 0:
                    filetext = filetext + para.text + '\n'

        elif suffix == 'txt':
            with open('client/media/' + stamp + '/' + f.name, encoding='utf-8') as file:
                content = file.read()
                filetext = content.rstrip()

        elif suffix == 'pdf':
            filepath = 'client/media/' + stamp + '/' + f.name
            filetext = read_pdf(filepath, filetext)

        request.session[f.name] = filetext
    return JsonResponse(data)


def example2(request):
    stamp = request.POST.get('stamp', '0')
    if stamp == '0':
        stamp = str(time.time())
        os.mkdir('client/media/' + stamp)

    filetext = ''
    data = {'stamp': stamp}
    filepath = 'client/static/client/collection/Example2.pdf'
    filetext = read_pdf(filepath, filetext)

    copyfile('client/static/client/collection/Example2.pdf',
             'client/media/' + stamp + '/Example2.pdf')

    request.session['Example2.pdf'] = filetext
    return JsonResponse(data)


def example3(request):
    stamp = request.POST.get('stamp', '0')
    if stamp == '0':
        stamp = str(time.time())
        os.mkdir('client/media/' + stamp)
    data = {'stamp': stamp}

    with open('client/static/client/collection/Example3.txt', encoding='utf-8') as file:
        content = file.read()
        filetext = content.rstrip()

    file_path = os.path.join('client/media/' + stamp + '/Example3.txt')  # 拼装目录名称+文件名称
    with open(file_path, 'w+', encoding='utf-8') as destination:  # 写文件word
        destination.write(filetext)
    destination.close()

    request.session['Example3.txt'] = filetext
    return JsonResponse(data)


def get_files_name(request):
    data = {}
    stamp = str(request.POST.get('stamp', '0'))
    file_path = os.path.join('client/media/' + stamp)
    filenames = os.listdir(file_path)
    data['filenames'] = filenames
    return JsonResponse(data)


def file_del(request):
    data = {}
    stamp = str(request.POST.get('stamp', '0'))
    filename = str(request.POST.get('filename', '0'))
    file_path = os.path.join('client/media/' + stamp + '/' + filename)
    os.remove(file_path)
    data['message'] = filename + ' has been deleted.'
    try:
        del request.session[filename]
        print('删除文件session成功：' + filename)
    except:
        print('删除文件session失败：' + filename)
    return JsonResponse(data)


def enrichment_analysis(request):
    data = {}
    species = request.POST.get('species')
    way = request.POST.get('way')
    gene_set = request.POST.get('text_gene')
    gene_set = gene_set.rstrip().split('\n')

    if way == 'go' or way == 'bp' or way == 'mf' or way == 'cc':
        ad = do_go(gene_set, species, way)
    elif way == 'kegg':
        ad = do_kegg(gene_set, species)
    elif way == 'do':
        ad = do_do(gene_set)
    else:
        ad = do_gesa(gene_set, way)

    data['result'] = ad
    return JsonResponse(data)


def upload_geneset(request):
    data = {'geneset': list()}
    try:
        file_object = request.FILES.get('files')
        file_name = file_object.name.split('.')[0]

        for chunk in file_object.chunks():
            l = chunk.decode().rstrip().split('\r\n')
            for i in l:
                data['geneset'].append(i)
    except:
        print('无文件')

    return JsonResponse(data)


def plot_word_cloud_EA(request):
    data = {}
    return JsonResponse(data)
    timeticket = time.time()

    word_e_p = request.POST.get('word_e_p', 'null')
    word_e_p = json.loads(word_e_p)

    width = int(request.POST.get('width'))
    height = int(request.POST.get('height'))
    scale = float(request.POST.get('scale'))
    prefer_horizontal = float(request.POST.get('prefer_horizontal'))
    max_font_size = int(request.POST.get('max_font_size'))
    min_font_size = int(request.POST.get('min_font_size'))
    show_img = request.POST.get('show_img')
    font_type = request.POST.get('font_type')
    colormaps = request.POST.get('colormaps')

    relative_scaling = 0.5
    font_path = 'client/static/client/Fonts/' + font_type

    if show_img == 'none':
        mask = None
    else:
        if show_img == 'custom':
            pic = request.session.get('custom', 'null')
            pic = np.array(pic)
        else:
            url = "client/static/client/img/" + show_img
            pic = np.array(Image.open(url))
        # colormaps = ImageColorGenerator(pic)
        # print(colormaps)
        mask = transparence2white(pic)

    wc = WordCloud(font_path=font_path, width=width, height=height, scale=scale,
                   prefer_horizontal=prefer_horizontal,
                   max_font_size=max_font_size, min_font_size=min_font_size, relative_scaling=relative_scaling,
                   mask=mask, mode='RGBA', background_color=None, colormap=colormaps)
    word_e_p = {k: float(v[0]) for k, v in word_e_p.items()}
    wc.generate_from_frequencies(word_e_p)

    plt.figure()  # 画图
    plt.imshow(wc)
    plt.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf)
    data['wordcloud_pic'] = base64.b64encode(buf.getvalue()).decode()
    url = "client/static/client/media/" + str(timeticket) + ".png"
    wc.to_file(url)
    plt.close()
    data['time'] = timeticket

    return JsonResponse(data)

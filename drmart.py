# -*- coding: utf-8 -*-
u"""Webスクレイピング用のコード
対象サイト: drmart
"""
import os
# import os.path
import re
# My library
from logmessage import logprint
import scraping
import imagefile
import textfile
import csvfile

BASE_URL = 'http://store.shopping.yahoo.co.jp/'
START_URL = BASE_URL + 'drmart/'
LINK_PATTERN = re.compile(
    r'http://store.shopping.yahoo.co.jp/drmart/[a-z\d]+.html')
GROUP_PATTERN = re.compile(
    r'http://store.shopping.yahoo.co.jp/drmart/[a-z\d]+.html')
PRODUCT_PATTERN = re.compile(
    r'http://store.shopping.yahoo.co.jp/drmart/[a-z\d-]+.html')


def make_url_list():
    u"""http://store.shopping.yahoo.co.jp/drmart-1/cm-200000.htmlを
    作成してリストで返す。
    """
    return_list = []
    # for i in range(200000, 400000):
    for i in range(200000, 200200):
        return_list.append(
            BASE_URL + 'drmart-1/cm-' + str(i) + '.html')

    return return_list


def make_header_name(name, number):
    u"""リストnameを受け取り要素数numberのリストを返す
    iが10の場合はlist1からlist10までを返す
    """
    name_list = []
    for i in range(0, number):
        name_list.append(name + 'list' + str(i + 1))

    return name_list


def make_header_list_old():
    u"""csvファイル用のヘッダーを作成する。
    """
    header_list = [
        'name', 'jan', 'abstract', 'price', 'explanation',
        'code', 'caption', 'image1', 'image2', 'image3',
        'image4', 'image5', 'Gimage1', 'path']

    header_name_40 = ['color-']

    header_name_30 = [
        'model-number-',
        'size-',
        'fragrance-',
        'type-'
        ]

    header_name_10 = [
        'seat-color-', 'seat-width-', 'seat-type-',
        'seat-height-', 'seat-color-type-', 'sitting-height-',
        'sitting-width-', 'pattern-', 'frame-color-',
        'left-and-right-', 'head-cap-color-', 'head-supprot-type-',
        'size-color-', 'firmness-', 'type-color-',
        'arm-support-', 'mount-position-', 'color2-',
        'color-type-', 'choice2-', 'taste-',
        'size-cm-', 'top-board-color-', 'lever-position-',
        'cloth-color-', 'thickness-', 'tire-size-',
        'cover-color-', 'cover-type-', 'caster-size-',
        'bag-color-', 'tipping-pipe-', 'wood-color-',
        'operating-side-', 'back-support-color-', 'body-color-',
        '']

    header_list_half = []
    for name in header_name_40:
        header_list_half.extend(make_header_name(name, 40))

    for name in header_name_30:
        header_list_half.extend(make_header_name(name, 30))

    for name in header_name_10:
        header_list_half.extend(make_header_name(name, 10))

    header_list.extend(header_list_half)

    return header_list


def make_header_list():
    u"""csvファイル用のヘッダーを作成する。
    """
    header_list = [
        'name', 'jan', 'abstract', 'price', 'explanation',
        'code', 'caption', 'image1', 'image2', 'image3',
        'image4', 'image5', 'Gimage1', 'path']

    header_name_40 = [
        'color-',
        'type-',
        'size-',
        'other-'
    ]

    header_list_half = []
    for name in header_name_40:
        header_list_half.extend(make_header_name(name, 40))

    header_list.extend(header_list_half)

    return header_list


if __name__ == '__main__':
    # baseURL               BASE_URL
    # スタートURL           BASE_URL + 'drmart/'
    # リンク追跡パターン    LINK_PATTERN

    TOP_LINKS = []        # 最初の走査で取得したリンク
    LAST_LINKS = set()       # 2回目の走査で取得したリンク
    PRODUCT_LINKS = set()    # 次のページ

    SCRAPING = scraping.Scraping(BASE_URL)
    TEXTFILE = textfile.TextFile('drmart-result', 'top_category.txt')
    COMPLETE = textfile.TextFile('drmart-result', 'complete_product.txt')
    NOT_FIND = textfile.TextFile('drmart-result', 'not_find_product.txt')
    HEADER_LIST = make_header_list()
    CSVFILE = csvfile.Csvfile('./drmart/', HEADER_LIST)
    COMPLETE_PRODUCT = ''
    NOT_FIND_PRODUCT = ''
    XPATH = ("//div[@id='NaviStrCategory1']" +
             "/div/ul/li/a[2]")

    # NOT FINDのファイルを読み込む
    NOT_FIND_FILE = NOT_FIND.open_read_mode()
    if NOT_FIND_FILE is not None:
        NOT_FIND_PRODUCT = NOT_FIND_FILE.read()
        NOT_FIND_FILE.close()

    # 処理済のファイルを読み込む
    COMPLETE_FILE = COMPLETE.open_read_mode()
    if COMPLETE_FILE is not None:
        COMPLETE_PRODUCT = COMPLETE_FILE.read()
        COMPLETE_FILE.close()

    # トップカテゴリを取得してTOP_LINKSに格納する。
    if os.path.isfile('drmart-result/top_category.txt'):
        # ファイルからトップカテゴリを読み込みTOP_LINKSにaddする
        logprint('トップカテゴリをファイルから読み込みます。')
        TOP_CATEGORY_FILE = TEXTFILE.open_read_mode()
        for line in TOP_CATEGORY_FILE:
            if not line.startswith('#'):
                if line != '\n':
                    TOP_LINKS.append(line.strip())

        TEXTFILE.close()

    else:
        logprint('カテゴリ(トップ)の走査を開始します。')

        TOP_CATEGORY_FILE = TEXTFILE.open_write_mode()

        # リンクをゲットする。
        TOP_LINKS = SCRAPING.get_links(
            START_URL,
            LINK_PATTERN,
            XPATH
            )
        if TOP_LINKS is None:
            logprint('リンク情報が見つかりません')
        else:
            # トップカテゴリをファイルに保存する。
            print(len(TOP_LINKS))
            for category in TOP_LINKS:
                TOP_CATEGORY_FILE.write(category + '\n')
                TOP_CATEGORY_FILE.flush()
            logprint(str(len(TOP_LINKS)) + '個のカテゴリが見つかりました')

        TEXTFILE.close()

    logprint('カテゴリの走査を開始します。')

    # # ラストカテゴリを渡して
    # # 商品情報とイメージファイルを保存する。
    # for link in TOP_LINKS:
    #     # last_links = SCRAPING.get_last_links(
    #     products = SCRAPING.find_item_list(
    #         link,
    #         PRODUCT_PATTERN
    #         )

    logprint(
        str(imagefile.get_image_count()) + '個のイメージファイルを保存しました。')

    logprint('商品情報の取得を終了します。')

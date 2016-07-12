# -*- coding: utf-8 -*-
u"""Webスクレイピング用のコード
対象サイト: アズワン
"""
# import os
# import os.path
import re
# My library
import logmessage
import scraping
import imagefile
import textfile
import csvfile

BASE_URL = 'http://store.shopping.yahoo.co.jp/'
START_URL = BASE_URL + 'drmart-1/'
LINK_PATTERN = re.compile(
    r'http://store.shopping.yahoo.co.jp/drmart-1/[a-z\d]+.html')
GROUP_PATTERN = re.compile(
    r'http://store.shopping.yahoo.co.jp/drmart-1/[a-z\d]+.html')
PRODUCT_PATTERN = re.compile(
    r'http://store.shopping.yahoo.co.jp/drmart-1/[a-z\d-]+.html')


def make_url_list():
    u"""http://store.shopping.yahoo.co.jp/drmart-1/cm-200000.htmlを
    作成してリストで返す。
    """
    return_list = []
    for i in range(200000, 400000):
        return_list.append(
            BASE_URL + 'drmart-1/cm-' + str(i) + '.html')

    return return_list


if __name__ == '__main__':
    # baseURL               BASE_URL
    # スタートURL           BASE_URL + 'drmart/'
    # リンク追跡パターン    LINK_PATTERN

    TOP_LINKS = []        # 最初の走査で取得したリンク
    LAST_LINKS = set()       # 2回目の走査で取得したリンク
    PRODUCT_LINKS = set()    # 次のページ

    SCRAPING = scraping.Scraping(BASE_URL)
    TEXTFILE = textfile.TextFile('result', 'top_category.txt')
    COMPLETE = textfile.TextFile('result', 'complete_product.txt')
    NOT_FIND = textfile.TextFile('result', 'not_find_product.txt')
    # NOT_FIND = textfile.TextFile('result', 'notfind_product.txt')
    CSVFILE = csvfile.Csvfile('./drmart-1/')
    COMPLETE_PRODUCT = ''
    NOT_FIND_PRODUCT = ''

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

    # 処理するurlのリストを作成する。
    URL_LIST = make_url_list()

    # テスト用
    URL_LIST = [
        # 'http://store.shopping.yahoo.co.jp/drmart-1/cm-234176.html',
        # 'http://store.shopping.yahoo.co.jp/drmart-1/cm-234177.html',
        # 'http://store.shopping.yahoo.co.jp/drmart-1/cm-257405.html',
        # 'http://store.shopping.yahoo.co.jp/drmart-1/cm-257486.html',
        # 'http://store.shopping.yahoo.co.jp/drmart-1/cm-257404.html',
        # 'http://store.shopping.yahoo.co.jp/drmart-1/cm-252447.html',
        'http://store.shopping.yahoo.co.jp/drmart-1/cm-218372.html',
        'http://store.shopping.yahoo.co.jp/drmart-1/cm-216054.html'
    ]
    # 処理済みのファイルに書き込む
    COMPLETE_FILE = COMPLETE.open_append_mode()
    for url in URL_LIST:
        if url in COMPLETE_PRODUCT:
            pass
        elif url in NOT_FIND_PRODUCT:
            pass
        else:
            # 商品情報を取得する。
            product = SCRAPING.get_product_info(url)
            if product is not None:
                CSVFILE.writerow(product)
                COMPLETE_FILE.write(url + '\n')

    COMPLETE_FILE.close()

    """
    # トップカテゴリを取得してTOP_LINKSに格納する。
    if os.path.isfile('result/top_category.txt'):
        # ファイルからトップカテゴリを読み込みTOP_LINKSにaddする
        logmessage.logprint('トップカテゴリをファイルから読み込みます。')
        TOP_CATEGORY_FILE = TEXTFILE.open_read_mode()
        for line in TOP_CATEGORY_FILE:
            if not line.startswith('#'):
                if line != '\n':
                    # TOP_LINKS.add(line.strip())
                    TOP_LINKS.append(line.strip())
        TEXTFILE.close()

    else:
        logmessage.logprint('カテゴリ(トップ)の走査を開始します。')

        TOP_CATEGORY_FILE = TEXTFILE.open_write_mode()

        # リンクをゲットする。
        TOP_LINKS = SCRAPING.get_links(
            [START_URL],
            LINK_PATTERN
            )

        # トップカテゴリをファイルに保存する。
        print(len(TOP_LINKS))
        for category in TOP_LINKS:
            TOP_CATEGORY_FILE.write(category + '\n')
            TOP_CATEGORY_FILE.flush()

        TEXTFILE.close()

    logmessage.logprint(str(len(TOP_LINKS)) + '個のカテゴリが見つかりました')

    logmessage.logprint('カテゴリの走査を開始します。')

    # ラストカテゴリを渡して
    # 商品情報とイメージファイルを保存する。
    for link in TOP_LINKS:
        # last_links = SCRAPING.get_last_links(
        products = SCRAPING.find_item_list(
            link,
            PRODUCT_PATTERN
            )
    """

    logmessage.logprint(
        str(imagefile.get_image_count()) + '個のイメージファイルを保存しました。')

    logmessage.logprint('商品情報の取得を終了します。')

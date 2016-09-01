# -*- coding: utf-8 -*-
u"""Webスクレイピング用のコード
対象サイト: サンワチャンネル
"""
import os
# import re
import time
# My library
from logmessage import logprint
import sanwachannel
# import imagefile
import textfile
import csvfile
import imagefile

URL = 'https://cust.sanwa.co.jp'

LOGIN_DICT = {
    'login_id': 'health-welfare@ghjapan.jp',
    'login_id_name': 'MailAddress',
    'password': 'ghjapan006',
    'password_name': 'PassWord',
    'submit_path': '//div[@class="login_inaccount"]/p/a'
}

SEARCH_LIST = [
    ["sProductCode", "-"],
    ["sProductName", ""],
    ["sJanCode", ""],
    ["sInventory", ""],
    ["sRegularPrice_Under", ""],
    ["sRegularPrice_TOP", ""],
    ["InAbolish", ""],
    ["DispImg", ""]
]

SUBMIT_PATH = "//img[@alt='この条件で検索']"

# 検索結果へのxpath
SERACH_RESULT_XPATH = "//p[@class='result_amount']"

# 商品リストのxpath
TABLE_TR_XPATH = "//table/tbody/tr"

# 商品個別ページのリンクテキスト
PRODUCT_LINK_TEXT = "詳細を見る"

# 在庫照会へのリンク
SEARCH_LINK_TEXT = "//li/p/a/img[@alt='在庫照会']"

# 次のページのリンクテキスト
NEXT_PAGE_LINK_TEXT = "次のページへ"


GET_ITEMS_LIST = [
    [
        1,
        "品名",
        "//div[@class='product_data_main']/p[@class='pname']"
    ],
    [
        2,
        "製品品番",
        "//div[@class='p_line1 clfx']/p[@class='p_line_right pcode']"
    ],
    [
        3,
        "JANコード",
        "//div[@class='p_line2 clfx']/p[@class='p_line_right']"
    ],
    [
        4,
        "標準価格",
        "//div[@class='p_line3 clfx']" +
        "/p[@class='p_line_right']"
    ],
    [
        5,
        "仕切価格",
        "//div[@class='p_line2 tp_4 clfx']" +
        "/p[@class='p_line_right pprice']/span"
    ]
]

FETR_AREA_XPATH = "//div[@class='fetr_area']"

PRODUCT_IMAGE_XPATH = "//p[@class='product_img']/img"

# 絵文字エリア
PRODUCT_SPEC_IMAGE_XPATH = "//div[@class='emoji_area clfx']/p/img"

# サンワサプライホームページへのリンク
LINK_XPATH = "//p[@class='sanwaweb_btn']/a"


def make_header_list():
    u"""csvファイル用のヘッダーを作成する。
    """
    header_list = [
        "品名1",
        "型番",
        "JAN",
        "標準価格",
        "仕切価格",
        "商品画像",
        "商品仕様画像1",
        "商品仕様画像2",
        "商品仕様画像3",
        "商品仕様画像4",
        "商品仕様画像5",
        "商品仕様画像6",
        "商品仕様画像7",
        "商品仕様画像8",
        "商品仕様画像9",
        "商品仕様画像10",
        "特長",
        "特長画像1",
        "特長画像2",
        "特長画像3",
        "特長画像4",
        "特長画像5",
        "特長画像6",
        "特長画像7",
        "特長画像8",
        "特長画像9",
        "特長画像10",
        "仕様",
        "仕様画像1",
        "仕様画像2",
        "仕様画像3",
        "仕様画像4",
        "仕様画像5",
        "仕様画像6",
        "仕様画像7",
        "仕様画像8",
        "仕様画像9",
        "仕様画像10",
        "対応機種",
        "対応機種画像1",
        "対応機種画像2",
        "対応機種画像3",
        "対応機種画像4",
        "対応機種画像5",
        "対応機種画像6",
        "対応機種画像7",
        "対応機種画像8",
        "対応機種画像9",
        "対応機種画像10",
        "カテゴリ1",
        "カテゴリ2",
        "カテゴリ3",
        "キャッチ"
        ]

    return header_list


if __name__ == '__main__':
    # CSVファイルのヘッダー作成
    HEADER_LIST = make_header_list()
    CSVFILE = csvfile.Csvfile('./sanwa/', HEADER_LIST)

    # プロダクトURL保存用ファイル
    PRODUCT_URL = []
    PRODUCT_URL_OBJ = textfile.TextFile('sanwa-result', 'product_url.txt')
    # 処理済みプロダクト格納用ファイル
    COMPLETE_PRODUCT = []
    COMPLETE_OBJ = textfile.TextFile('sanwa-result', 'complete_product.txt')

    # Sanwachannelクラスの初期化
    SANWACHANNEL = sanwachannel.Sanwachannel(URL)

    # 処理済みのファイルを読み込む
    COMPLETE_FILE = COMPLETE_OBJ.open_read_mode()
    if COMPLETE_FILE is not None:
        for line in COMPLETE_FILE:
            if line != "\n":
                COMPLETE_PRODUCT.append(line.strip())
        COMPLETE_FILE.close()

    if os.path.isfile('sanwa-result/product_url.txt'):
        # ファイルからURLを読み込む
        logprint('URLをファイルから読み込みます。')
        PRODUCT_URL_FILE = PRODUCT_URL_OBJ.open_read_mode()
        for line in PRODUCT_URL_FILE:
            if not line.startswith("#"):
                if line != '\n':
                    PRODUCT_URL.append(line.strip())
        PRODUCT_URL_FILE.close()
    else:
        # URL格納ファイルを書き込み用にオープンする。
        PRODUCT_URL_FILE = PRODUCT_URL_OBJ.open_append_mode()

        # ログイン処理 - driver
        SANWACHANNEL.get_page(SANWACHANNEL.driver, URL)
        SANWACHANNEL.execute_login(SANWACHANNEL.driver, LOGIN_DICT)

        time.sleep(5)
        # 在庫照会をクリック
        SANWACHANNEL.execute_link_click(
            SANWACHANNEL.driver, SEARCH_LINK_TEXT)

        # 検索の実行
        SANWACHANNEL.execute_search(SEARCH_LIST, SUBMIT_PATH)

        while True:
            # 結果表示
            SANWACHANNEL.get_page_information(SERACH_RESULT_XPATH)

            # 商品リストを取得する。
            PRODUCT_ROWS = SANWACHANNEL.get_table_row(TABLE_TR_XPATH)

            # 商品個別ページの処理。
            for row in PRODUCT_ROWS:
                url = SANWACHANNEL.get_product_url(row, PRODUCT_LINK_TEXT)

                if url is not None:
                    PRODUCT_URL_FILE.write(url + '\n')

            if SANWACHANNEL.is_link_enable(NEXT_PAGE_LINK_TEXT):
                SANWACHANNEL.get_next_page(NEXT_PAGE_LINK_TEXT)
            else:
                break

        PRODUCT_URL_FILE.close()

    # ログイン処理 - product_driver
    SANWACHANNEL.get_page(SANWACHANNEL.product_driver, URL)
    SANWACHANNEL.execute_login(
        SANWACHANNEL.product_driver, LOGIN_DICT)

    time.sleep(5)
    # プロダクトのURLが格納されているファイルを読み込む
    PRODUCT_URL_FILE = PRODUCT_URL_OBJ.open_read_mode()
    if PRODUCT_URL_FILE is not None:
        for line in PRODUCT_URL_FILE:
            if line != '\n':
                if line.strip() in PRODUCT_URL:
                    pass
                else:
                    PRODUCT_URL.append(line.strip())
        PRODUCT_URL_FILE.close()
    else:
        logprint("URL格納ファイル処理で予期せぬエラーが発生しました。")

    COMPLETE_FILE = COMPLETE_OBJ.open_append_mode()
    for url in PRODUCT_URL:
        # 処理済であれば何もしない
        if url in COMPLETE_PRODUCT:
            pass
        else:
            product_page = SANWACHANNEL.get_product_driver(url)
            # 品名、製品品番、JANコード、標準価格、仕切価格を取得する。
            product_text = SANWACHANNEL.get_product_text(
                product_page, GET_ITEMS_LIST)

            model_number = product_text[1]

            # 「￥」と「,」を削除する。
            if product_text[3].startswith('￥'):
                product_text[3] = SANWACHANNEL.get_only_number(
                    product_text[3])
            if product_text[4].startswith('￥'):
                product_text[4] = SANWACHANNEL.get_only_number(
                    product_text[4])

            # 商品画像を取得する。
            image_list = SANWACHANNEL.make_image_row(
                product_page, PRODUCT_IMAGE_XPATH)

            if len(image_list) != 0:
                # '_ma'を削除する。
                # image_name = image_list[0][0].replace('_MA', '')
                # print(image_name)
                extension_list = image_list[0][0].split('.')
                extension = extension_list[1]
                image_name = model_number
                image_name = image_name.lower() + '.' + extension

                # イメージをダウンロードして保存する。
                imagefile.download_and_save_dir_direct(
                    image_list[0][1], 'sanwaimage', image_name)
                product_text.extend([image_name])

            # 商品仕様画像を取得する。
            spec_image_list = SANWACHANNEL.make_image_row(
                product_page, PRODUCT_SPEC_IMAGE_XPATH)

            # イメージをダウンロードして保存する。
            for image_list in spec_image_list:
                if len(image_list) != 0:
                    image_name = image_list[0].lower()
                    imagefile.download_and_save_dir_direct(
                        image_list[1],
                        'sanwaimage/icon',
                        image_name)
                    product_text.extend([image_name])
                else:
                    product_text.extend([''])

            # 特長、仕様、対応機種を取得する。
            product_fetr = SANWACHANNEL.get_product_fetr(
                product_page, FETR_AREA_XPATH, model_number)
            product_text.extend(product_fetr)
            # リンク先の情報を取得する。
            link_dist_info = SANWACHANNEL.get_link_dist_info(
                product_page, LINK_XPATH)
            product_text.extend(link_dist_info)
            # 商品名が取得できていなければCSVファイルに書き込まない
            if len(product_text[0]) != 0:
                CSVFILE.writerow(product_text)
                COMPLETE_FILE.write(url + '\n')
    COMPLETE_FILE.close()

    logprint('商品情報の取得を終了します。')

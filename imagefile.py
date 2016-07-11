# -*- coding: utf-8 -*-
u"""イメージファイルをダウンロードしてファイルに保存する。
"""
import os
import unittest
import shutil
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import urlretrieve
# My library
import logmessage

IMAGE_SERIAL_NUMBER = 0
IMAGE_DIR_NAME = '000'

# イメージファイル名に重複ないように
IMAGE_FILE_SET = set()


def make_image_directory_name():
    u"""
    目的    : イメージファイルを格納するディレクトリ名を作成するために'001'から始まる連番を返す
    引数    : なし
    戻り値  : '001'から始まり、呼ばれる度に１つずつ増加する。
    """
    global IMAGE_DIR_NAME

    IMAGE_DIR_NAME = int(IMAGE_DIR_NAME) + 1
    IMAGE_DIR_NAME = str(IMAGE_DIR_NAME)

    if len(IMAGE_DIR_NAME) == 1:
        IMAGE_DIR_NAME = '00' + IMAGE_DIR_NAME
    elif len(IMAGE_DIR_NAME) == 2:
        IMAGE_DIR_NAME = '0' + IMAGE_DIR_NAME
    else:
        pass

    return IMAGE_DIR_NAME


def download_and_save(url, image_dir, image_file_name):
    u"""
    目的 : urlを受け取りページにアクセスしてイメージファイルを
           ダウンロードする。
    引数 :   * url
                * image_file_name
    戻り値 : なし
    処理概要 :
        * イメージファイルを格納するディレクトリ名を作成するために
          '001'から始まる連番を返す
        * 呼ばれるたびにIMAGE_SERIAL_NUMBERをインクリメントする
        * IMAGE_DIR_NAMEを1000回呼ばれるごとにインクリメントする
    """
    global IMAGE_SERIAL_NUMBER  # imageの通し番号　1000ファイルごとに001からの連番を取得する
    global IMAGE_DIR_NAME       # imageの通し番号のディレクトリ名

    # ./imageディレクトリを作成する。
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # 1000個ごとに新たにディレクトリを作成する。
    if IMAGE_SERIAL_NUMBER % 1000 == 0:
        IMAGE_DIR_NAME = make_image_directory_name()
        # ./image/001ディレクトリを作成する。
        if not os.path.exists(
                os.path.join(image_dir, IMAGE_DIR_NAME)):
            os.mkdir(os.path.join(image_dir, IMAGE_DIR_NAME))
        if IMAGE_SERIAL_NUMBER != 0:
            logmessage.logprint(str(IMAGE_SERIAL_NUMBER) + '個のイメージを保存しました。')

    image_file_path = (
        os.path.join(image_dir, IMAGE_DIR_NAME, image_file_name)
        )

    # イメージファイルを取得する
    try:
        local_filename = urlretrieve(url, image_file_path)
    except HTTPError as error_code:
        logmessage.logprint('HTTPError')
        logmessage.logprint(url)
        logmessage.logprint(str(error_code))
    except URLError as error_code:
        logmessage.logprint('URLError')
        logmessage.logprint(url)
        logmessage.logprint(str(error_code))
    except UnicodeEncodeError as error_code:
        logmessage.logprint('UnicodeEncodeError')
        logmessage.logprint(url)
        logmessage.logprint(str(error_code))
    else:
        if local_filename is not None:
            if local_filename not in IMAGE_FILE_SET:
                IMAGE_FILE_SET.add(local_filename)
                # IMAGE_SERIAL_NUMBERのインクリメント
                IMAGE_SERIAL_NUMBER = IMAGE_SERIAL_NUMBER + 1


def download_and_save_dir_direct(url, image_dir, image_file_name):
    u"""
    目的 : urlを受け取りページにアクセスしてイメージファイルを
           ダウンロードする。
    引数 :
        * url
        * image_file_name
    戻り値 : なし
    処理概要 :
        * イメージファイルを格納するディレクトリはimage直下
        * 呼ばれるたびにIMAGE_SERIAL_NUMBERをインクリメントする
    """
    global IMAGE_SERIAL_NUMBER  # imageの通し番号　1000ファイルごとに001からの連番を取得する

    # ./imageディレクトリを作成する。
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # 1000個ごとに新たにディレクトリを作成する。
    if IMAGE_SERIAL_NUMBER % 10 == 0:
        if IMAGE_SERIAL_NUMBER != 0:
            logmessage.logprint(str(IMAGE_SERIAL_NUMBER) + '個のイメージを保存しました。')

    image_file_path = (
        os.path.join(image_dir, image_file_name)
        )

    # イメージファイルを取得する
    try:
        local_filename = urlretrieve(url, image_file_path)
    except HTTPError as error_code:
        logmessage.logprint('HTTPError')
        logmessage.logprint(url)
        logmessage.logprint(str(error_code))
    except URLError as error_code:
        logmessage.logprint('URLError')
        logmessage.logprint(url)
        logmessage.logprint(str(error_code))
    except UnicodeEncodeError as error_code:
        logmessage.logprint('UnicodeEncodeError')
        logmessage.logprint(url)
        logmessage.logprint(str(error_code))
    else:
        if local_filename is not None:
            if local_filename not in IMAGE_FILE_SET:
                IMAGE_FILE_SET.add(local_filename)
                # IMAGE_SERIAL_NUMBERのインクリメント
                IMAGE_SERIAL_NUMBER = IMAGE_SERIAL_NUMBER + 1


def get_image_count():
    u"""イメージのカウントを返す
    """

    return IMAGE_SERIAL_NUMBER


class FatorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        pass

    def test_make_image_directory_name(self):
        u"""イメージファイルをダウンロードして保存する。
        """
        image_directory_name = make_image_directory_name()
        self.assertEqual(image_directory_name, '002')

    def test_download_and_save(self):
        u"""イメージファイルを保存するディレクトリを作成する。
        """
        url = 'http://item.shopping.c.yimg.jp/i/l/drmart-1_cm-298752_1'
        download_and_save(url, 'image', 'cm-298752_1.jpg')
        self.assertTrue(
            os.path.exists('image/001/cm-298752_1.jpg'))

    def test_download_and_save_direct(self):
        u"""イメージファイルを保存するディレクトリを作成する。
        """
        url = 'http://item.shopping.c.yimg.jp/i/l/drmart-1_cm-298752_1'
        download_and_save_dir_direct(url, 'image', 'cm-298752_1.jpg')
        self.assertTrue(
            os.path.exists('image/cm-298752_1.jpg'))

    def tearDown(self):
        u"""ファイルをクローズする。
        """
        if os.path.exists('image'):
            shutil.rmtree('image')

if __name__ == '__main__':
    unittest.main()

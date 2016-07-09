# -*- coding: utf-8 -*-
u"""ログを処理するモジュール
機能:
    *
    *
"""
import os
import unittest
from datetime import datetime

YYYY = str(datetime.now().year)
MM = str(datetime.now().month)
DD = str(datetime.now().day)

if not os.path.exists('log'):
    os.makedirs('log')

OUTPUT_FILE = open('log/' + YYYY + '-' + MM + '-' + DD + '.log',
                   mode='w',
                   encoding='utf-8')


def logprint(message):
    u"""messageを受け取り端末に表示しログに出力する。
    """
    global MM
    global DD

    message = str(message)

    # MM
    if len(MM) == 1:
        MM = '0' + MM

    # DD
    if len(DD) == 1:
        DD = '0' + DD

    # hour_str
    hour_str = str(datetime.now().hour)
    if len(hour_str) == 1:
        hour_str = '0' + hour_str

    # MM
    MM = str(datetime.now().minute)
    if len(MM) == 1:
        MM = '0' + MM

    # second_str
    second_str = str(datetime.now().second)
    if len(second_str) == 1:
        second_str = '0' + second_str

    print_message = (
        YYYY + '-' +
        MM + '-' +
        DD + 'T' +
        hour_str + ':' +
        MM + ':' +
        second_str + ' ' +
        message
        )

    print(print_message)
    # ファイルに書き出す
    # flushで強制的に書き込む
    OUTPUT_FILE.write(print_message + '\n')
    OUTPUT_FILE.flush()


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """
    def setUp(self):
        u"""セットアップ
        """
        pass

    def test_print_message(self):
        u"""端末に'test'を表示しlogに書き込むテスト
        """
        logprint('test')
        self.assertTrue(os.path.exists('log/2016-7-9.log'))

    def test_encoding(self):
        u"""ファイルのエンコーディングをテスト
        """
        logprint('test')
        file_handler = open('log/2016-7-9.log', 'r')
        self.assertTrue(file_handler.encoding, 'utf-8')
        file_handler.close()

    def tearDown(self):
        u"""終了時の処理
        """
        pass

if __name__ == '__main__':
    unittest.main()

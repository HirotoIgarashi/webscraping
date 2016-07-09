# -*- coding: utf-8 -*-
u"""ファイルの読み書きを行うクラス
"""
import unittest
import os


class TextFile(object):
    u"""テキストファイルのクラス
    引数:
        * directory
        * file_name
    変数:
        * file_object
        * contents
    処理:
        * directoryを受け取りそのディレクトリが存在しなかったら作成する。
    """
    def __init__(self, directory, file_name):
        self.directory = directory
        self.text_file_name = file_name

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # 変数は__init__で定義しておく
        self.file_object = None
        self.contents = None

    def open_write_mode(self):
        u"""書き込みモードでオープンしてfile objectを返す
        既にファイルがある場合は削除する。
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.file_object = open(
            os.path.join(self.directory, self.text_file_name),
            mode='w',
            encoding='utf-8')

        return self.file_object

    def open_append_mode(self):
        u"""追記モードでオープンしてfile objectを返す
        ファイルがない場合は新規に作成する。
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.file_object = open(
            os.path.join(self.directory, self.text_file_name),
            mode='a',
            encoding='utf-8')

        return self.file_object

    def open_read_mode(self):
        u"""読み込みモードでオープンしてfile objectを返す
        ファイルが見つからなかったらNoneを返す
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        try:
            self.file_object = open(
                os.path.join(self.directory, self.text_file_name),
                mode='r',
                encoding='utf-8')
        except FileNotFoundError:
            return None

        return self.file_object

    def write(self, text):
        u"""ファイルにtextを書き込む
        """
        self.file_object.write(text)
        self.file_object.flush()

        return self.file_object

    def read(self):
        u"""ファイルからtextを読み込む
        """
        self.contents = self.file_object.read()

        return self.contents

    def close(self):
        u"""ファイルをクローズする
        """
        self.file_object.close()


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        self.text_file = TextFile('testpath', 'test.txt')

        self.text_file_hundler = None

    def test_open_write_mode(self):
        u"""書き込み用にファイルをオープンするテスト
        """
        self.text_file_hundler = self.text_file.open_write_mode()
        self.assertTrue(os.path.exists('testpath/test.txt'))

    def test_open_append_mode(self):
        u"""書き込み用にファイルをオープンするテスト
        """
        self.text_file_hundler = self.text_file.open_append_mode()
        self.assertTrue(os.path.exists('testpath/test.txt'))

    def test_file_name(self):
        u"""ファイルの名前をテスト
        """
        self.text_file_hundler = self.text_file.open_write_mode()
        self.assertEqual(self.text_file_hundler.name, 'testpath/test.txt')

    def test_encoding(self):
        u"""ファイルのencodingをテスト
        """
        self.text_file_hundler = self.text_file.open_write_mode()
        self.assertEqual(self.text_file_hundler.encoding, 'utf-8')

    def test_mode(self):
        u"""ファイルのmodeをテスト
        """
        self.text_file_hundler = self.text_file.open_write_mode()
        self.assertEqual(self.text_file_hundler.mode, 'w')

    def test_write_text(self):
        u"""ファイルに書き込むテスト
        """
        self.text_file_hundler = self.text_file.open_write_mode()
        self.text_file_hundler.write('test test test')
        self.text_file_hundler.close()
        self.text_file_hundler = self.text_file.open_read_mode()
        self.assertEqual(self.text_file_hundler.read(), 'test test test')

    def test_write_texts(self):
        u"""ファイルに複数行、書き込みするテスト
        """
        self.text_file_hundler = self.text_file.open_write_mode()
        self.text_file_hundler.write('test test test\n')
        self.text_file_hundler.write('test2 test2 test2')
        self.text_file_hundler.close()
        self.text_file_hundler = self.text_file.open_read_mode()
        self.assertEqual(
            self.text_file_hundler.read(),
            'test test test\ntest2 test2 test2')

    def test_read_error(self):
        u"""存在しないファイルをオープンしたときにNoneが返るテスト
        """
        self.text_file = TextFile('testpath', 'error.txt')
        self.text_file_hundler = self.text_file.open_read_mode()
        self.assertEqual(
            self.text_file_hundler, None
        )

    def tearDown(self):
        u"""ファイルをクローズする。
        """
        if self.text_file_hundler is not None:
            self.text_file_hundler.close()

if __name__ == '__main__':
    unittest.main()

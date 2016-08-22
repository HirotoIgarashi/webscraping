# -*- coding: utf-8 -*-
u"""csvファイルの処理を行う
"""
import os
import unittest
from datetime import datetime
import csv
# My library
from logmessage import logprint


class Csvfile():
    u"""Csvfileクラス
    """
    def __init__(self, directory, header_list):
        # csvファイルに書き込んだヘッダを除くレコード数
        self.row_serial_number = 0
        # 今オープンしているcsvファイル
        self.csv_file = None
        self.directory = directory
        self.file_name = ''

        # csvファイル名のdata_160712_01.csvの160712部分
        self.part_file_name = self.get_yymmdd()
        # csvファイル名のdata_160712_01.csvの01部分
        self.csv_file_serial_number = 1

        self.file_path = None

        self.header_list = header_list

        # 既存ファイルの読み込み
        self.open_read_mode()

    @staticmethod
    def get_yymmdd():
        u"""本日のyymmddの値を返す。
        """
        # 起動時の時刻を取得してself.part_file_nameに値を代入'''
        # 2桁の年を追記
        yymmdd = ''
        year_str = str(datetime.now().year)[2:]

        # 2桁の月を追記
        month_str = str(datetime.now().month)
        if len(month_str) == 1:
            month_str = '0' + month_str

        # 2桁の日を追記
        day_str = str(datetime.now().day)
        if len(day_str) == 1:
            day_str = '0' + day_str

        yymmdd = year_str + month_str + day_str

        return yymmdd

    def make_csv_file_name(self):
        u"""csvファイルの名前を返す
        data_YYMMDD_01.csvという形式のファイル名になる。
        """
        file_name = 'data_'

        # self.part_file_nameを追記
        file_name += self.part_file_name

        # '_'アンダーバーを追記
        file_name = file_name + '_'

        # 文字列に変換
        serial_number = str(self.csv_file_serial_number)
        if len(serial_number) == 1:
            serial_number = '0' + serial_number
        file_name = file_name + serial_number

        return file_name

    def open_read_mode(self):
        u"""読み込みモードでオープンしてself.row_serial_numberに
        行数を設定して返す。
        * dirctoryが存在しない場合はself.directoryを作成する。
        * directoryにファイルがない場合は何もしない
        * directoryにファイルが１つ以上ある場合は一覧を取得して
          レコード数を求める。
        * ファイル名からYYMMDDを求める。self.part_file_nameを更新する。
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # ファイルの一覧を取得する。
        backup_cwd = os.getcwd()
        os.chdir(self.directory)
        files = [f for f in os.listdir('.')]
        if len(files) is 0:
            os.chdir(backup_cwd)
            # self.csv_file_serial_number = 1
            return
        else:
            # files.sort(key=os.path.getmtime)
            files.sort()
        os.chdir(backup_cwd)

        for file_name in files:
            # 読み込んだファイル名からyymmddを求める。
            if file_name.startswith('data_'):
                self.part_file_name = file_name.split('.')[0].split('_')[1]
                file_path = os.path.join(self.directory, file_name)

                # 行数を取得する。
                try:
                    file_handler = open(file_path, encoding='utf-8')
                except IOError:
                    logprint('CSVファイルのオープンでエラーが発生しました。')
                line_num = len(file_handler.readlines())

                if line_num == 0:
                    pass
                elif line_num == 1:
                    pass
                else:
                    self.row_serial_number += (line_num - 1)

                self.csv_file_serial_number = int(
                    file_name.split('.')[0].split('_')[2])

                file_handler.close()

        return self.row_serial_number

    def open_append_mode(self):
        u"""追記モードでオープンしてfile objectを返す
        """
        self.file_name = self.make_csv_file_name()
        self.file_path = os.path.join(
            self.directory, self.file_name + '.csv')

        try:
            self.csv_file = open(
                self.file_path,
                newline='',
                mode='a+',
                encoding='utf-8')
        except IOError:
            logprint('CSVファイルのオープンでエラーが発生しました。')

        return self.csv_file

    def writerow(self, row_list):
        u"""row_listを受け取りcsvファイルに保存する。
        """
        # 10個のレコードを保存するたびにログを表示する。
        # if self.row_serial_number % 10 == 0:
        #     # 初回はパスする。
        #     if self.row_serial_number != 0:
        #         logprint(
        #             str(self.row_serial_number) + '個のレコードを保存しました。')

        if self.row_serial_number % 19999 == 0:
            # 19,999行、39,998行...書き込んだ時の処理
            # 通し番号をインクリメント
            if self.row_serial_number is not 0:
                self.csv_file_serial_number += 1

        # ファイルがNoneかどうか判定してオープンする。
        if self.csv_file is None:
            self.csv_file = self.open_append_mode()

        # ファイルがオープンしてるかどうか判定してオープンする。
        if self.csv_file.closed is True:
            self.csv_file = self.open_append_mode()

        writer = csv.writer(self.csv_file, lineterminator='\n')

        if self.row_serial_number == 0:
            # 初回の処理
            try:
                writer.writerow(self.header_list)
            except csv.Error:
                logprint('CSVファイルへの書き込みに失敗しました。')

        elif self.row_serial_number % 19999 == 0:
            # 19,999行、39,998行...書き込んだ時のヘッダの書き込み処理
            try:
                writer.writerow(self.header_list)
            except csv.Error:
                logprint('CSVファイルへの書き込みに失敗しました。')

        else:
            pass

        # CSVファイルへの書き込み
        try:
            writer.writerow(row_list)
        except csv.Error:
            logprint('CSVファイルへの書き込みに失敗しました。')
        else:
            self.row_serial_number += 1

        # 19999レコード書き終わったらファイルをクローズする
        if self.row_serial_number % 19999 == 0:
            self.csv_file.close()

        return self.row_serial_number

    def get_record_count(self):
        u"""レコードの件数を返す
        """

        return self.row_serial_number

    def close(self):
        u"""ファイルをクローズする。
        """
        if self.csv_file is not None:
            self.csv_file.close()


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
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
            header_list_half.extend(self.make_header_name(name, 40))

        for name in header_name_30:
            header_list_half.extend(self.make_header_name(name, 30))

        for name in header_name_10:
            header_list_half.extend(self.make_header_name(name, 10))

        header_list.extend(header_list_half)

        self.csv_file = Csvfile('./testdir/', header_list)

    @staticmethod
    def make_header_name(name, number):
        u"""リストnameを受け取り要素数numberのリストを返す
        iが10の場合はlist1からlist10までを返す
        """
        name_list = []
        for i in range(0, number):
            name_list.append(name + 'list' + str(i + 1))

        return name_list

    def test_open_append_mode(self):
        u"""追記用にファイルをオープンして書き込むテスト
        """
        self.csv_file.writerow(['test1', 'test2'])
        self.csv_file.writerow(['test3', 'test4'])

        csv_file_name = self.csv_file.make_csv_file_name() + '.csv'
        self.assertTrue(os.path.exists(
            'testdir/' + csv_file_name))

    # def test_write_row(self):
    #     u"""ファイルに書き込むテスト
    #     """
    #     self.csv_file.writerow(['test1', 'test2'])
    #     self.csv_file.writerow(['test3', 'test4'])
    #     self.csv_file.writerow(['test5', 'test6'])
    #     self.assertTrue(os.path.exists('testdir/data_160711_01.csv'))

    # def test_append_row(self):
    #     u"""追記用にファイルをオープンして書き込むテスト
    #     """
    #     self.csv_file.writerow(['test7', 'test8'])
    #     self.csv_file.writerow(['test9', 'test10'])
    #     self.csv_file.writerow(['test11', 'test12'])
    #     self.csv_file.writerow(['test13', 'test14'])
    #     self.assertTrue(os.path.exists('testdir/data_160711_02.csv'))

    def test_write_30000(self):
        u"""追記用にファイルをオープンして書き込むテスト
        """
        for i in range(10000):
            self.csv_file.writerow([i])

        csv_file_name = self.csv_file.make_csv_file_name() + '.csv'

        self.assertTrue(os.path.exists(
            'testdir/' + csv_file_name))

    # def test_encoding(self):
    #     u"""ファイルのmodeをテスト
    #     """
    #     self.csv_file = self.csv_file.open_append_mode()
    #     self.assertEqual(self.csv_file.encoding, 'utf-8')

    # def test_append_mode(self):
    #     u"""ファイルのmodeをテスト
    #     """
    #     self.csv_file = self.csv_file.open_append_mode()
    #     self.assertEqual(self.csv_file.mode, 'a+')

    # def test_read(self):
    #     u"""ファイルの内容を読み込む
    #     """
    #     # self.csv_file = self.csv_file.open_append_mode()
    #     self.csv_file.writerow(('test1', 'test2'))
    #     self.csv_file.writerow(('test3', 'test4'))
    #     self.csv_file.writerow(('test5', 'test6'))
    #     self.csv_file.writerow(('test7', 'test8'))

    #     self.assertEqual(self.csv_file, 4)

    def tearDown(self):
        u"""ファイルをクローズする。
        """
        self.csv_file.close()

if __name__ == '__main__':
    unittest.main()

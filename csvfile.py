# -*- coding: utf-8 -*-
u"""csvファイルの処理を行う
"""
import os
import unittest
from datetime import datetime
import csv
# My library
import logmessage


class Csvfile():
    u"""Csvfileクラス
    """
    def __init__(self, directory):
        self.csv_file_serial_number = 0
        self.row_serial_number = 0
        self.csv_file = None
        self.directory = directory
        self.file_name = ''

        yymmdd_string = self.get_yymmdd()

        self.part_file_name = yymmdd_string

        self.file_path = None

        self.header_list = [
            'name', 'jan', 'abstract', 'price', 'explanation',
            'code', 'caption', 'image1', 'image2', 'image3',
            'image4', 'image5', 'Gimage1', 'path']

        self.header_name_40 = ['color-']

        self.header_name_30 = [
            'model-number-',
            'size-',
            'fragrance-',
            'type-'
            ]

        self.header_name_10 = [
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

        # 既存のファイル読み込む
        self.open_read_mode()

        header_list_half = []
        for name in self.header_name_40:
            header_list_half.extend(self.make_header_name(name, 40))

        for name in self.header_name_30:
            header_list_half.extend(self.make_header_name(name, 30))

        for name in self.header_name_10:
            header_list_half.extend(self.make_header_name(name, 10))

        self.header_list.extend(header_list_half)

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
        * dirctoryが存在しない場合はself.directoryで作成する。
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
            return
        else:
            files.sort(key=os.path.getmtime)
        os.chdir(backup_cwd)

        print(files)

        for file_name in files:
            # 読み込んだファイル名からyymmddを求める。
            if file_name.startswith('data_'):
                print(file_name)
                self.part_file_name = file_name.split('.')[0].split('_')[1]
                file_path = os.path.join(self.directory, file_name)
                with open(file_path, 'r', encoding='utf-8') as file_contents:
                    reader = csv.reader(file_contents)
                    # ヘッダーを読み飛ばす
                    next(reader)
                    i = 0
                    for row in reader:
                        i += 1
                    print(i)
                    self.row_serial_number += i

                self.csv_file_serial_number += 1

        return self.row_serial_number

    def open_append_mode(self):
        u"""追記モードでオープンしてfile objectを返す
        既にファイルがある場合は削除される。
        """
        # print('open_append_mode start')
        self.file_name = self.make_csv_file_name()
        self.file_path = os.path.join(
            self.directory, self.file_name) + '.csv'
        # print(self.file_path)

        self.csv_file = open(
            self.file_path,
            newline='',
            mode='a+',
            encoding='utf-8')

        return self.csv_file

    @staticmethod
    def make_header_name(name, number):
        u"""リストnameを受け取り要素数numberのリストを返す
        iが10の場合はlist1からlist10までを返す
        """
        name_list = []
        for i in range(0, number):
            name_list.append(name + 'list' + str(i + 1))

        return name_list

    def writerow(self, row_list):
        u"""row_listを受け取りcsvファイルに保存する。
        """
        # 10個のレコードを保存するたびにログを表示する。
        if self.row_serial_number % 10 == 0:
            if self.row_serial_number != 0:
                logmessage.logprint(
                    str(self.row_serial_number) + '個のレコードを保存しました。')

        if self.row_serial_number % 19999 == 0:
            # 通し番号をインクリメント
            self.csv_file_serial_number += 1

            self.csv_file = self.open_append_mode()
            writer = csv.writer(self.csv_file, lineterminator='\n')
            writer.writerow(self.header_list)

        if self.csv_file is None:
            self.csv_file = self.open_append_mode()

        # CSVファイルへの書き込み
        try:
            writer = csv.writer(self.csv_file, lineterminator='\n')
            writer.writerow(row_list)
        except csv.Error:
            logmessage.logprint('CSVファイルへの書き込みに失敗しました。')
        else:
            self.row_serial_number += 1

        # 19999レコード書き終わったらファイルをクローズする
        if self.row_serial_number % 19999 == 0:
            self.csv_file.close()

        # print(self.row_serial_number)

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
        self.csv_file = Csvfile('./testdir/')

    # def test_open_write_mode(self):
    #     u"""書き込み用にファイルをオープンするテスト
    #     """
    #     self.csv_file = self.csv_file.open_write_mode()
    #     self.assertTrue(os.path.exists('testdir/data_160706_01.csv'))

    # def test_open_append_mode(self):
    #     u"""追記用にファイルをオープンするテスト
    #     """
    #     self.csv_file = self.csv_file.open_append_mode()
    #     self.assertTrue(os.path.exists('testdir/data_160706_01.csv'))

    # def test_write_row(self):
    #     u"""ファイルに書き込むテスト
    #     """
    #     self.csv_file.writerow(['test1', 'test2'])
    #     self.csv_file.writerow(['test3', 'test4'])
    #     self.csv_file.writerow(['test5', 'test6'])
    #     self.assertTrue(os.path.exists('testdir/data_160706_01.csv'))

    # def test_append_row(self):
    #     u"""追記用にファイルをオープンして書き込むテスト
    #     """
    #     self.csv_file.writerow(['test7', 'test8'])
    #     self.csv_file.writerow(['test9', 'test10'])
    #     self.csv_file.writerow(['test11', 'test12'])
    #     self.csv_file.writerow(['test13', 'test14'])
    #     self.assertTrue(os.path.exists('testdir/data_160706_01.csv'))

    def test_write_30000(self):
        u"""追記用にファイルをオープンして書き込むテスト
        """
        # for i in range(19999):
        for i in range(50000):
            self.csv_file.writerow([i])
        self.assertTrue(os.path.exists('testdir/data_160709_01.csv'))

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

    # def test_write_mode(self):
    #     u"""ファイルのmodeをテスト
    #     """
    #     self.csv_file = self.csv_file.open_write_mode()
    #     self.assertEqual(self.csv_file.mode, 'w+')

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

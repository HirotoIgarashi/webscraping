# -*- conding: utf-8 -*-
u"""スクレイピング用のライブラリ
"""
import re
import random
import time
from urllib.error import HTTPError
from urllib.error import URLError
from http.client import RemoteDisconnected
import unittest
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# My library
import imagefile
from logmessage import logprint
import textfile
from scraping import Scraping


def make_header_name(name, number):
    u"""リストnameを受け取り要素数numberのリストを返す
    iが10の場合はlist1からlist10までを返す
    """
    name_list = []
    for i in range(0, number):
        name_list.append(name + 'list' + str(i + 1))

    return name_list


def write_not_find_page_url(url):
    u"""見つからなかったページのurlを書き込む
    """
    not_find = textfile.TextFile('result', 'not_find_product.txt')
    not_find_file = not_find.open_append_mode()
    not_find_file.write(url + '\n')
    not_find_file.close()


def make_header_list():
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


def decide_start_column(data, color_list, type_list, size_list, other_list):
    u"""column数を決定する。
    """
    title = data[0]
    if title in color_list[1]:
        # start_colum = color_count
        start_colum = color_list[0]
    elif title in type_list[1]:
        # start_colum = type_count
        start_colum = type_list[0]
    elif title in size_list[1]:
        # start_colum = size_count
        start_colum = size_list[0]
    else:
        # start_colum = other_count
        start_colum = other_list[0]

    return start_colum


def set_start_column(
        title, start_colum, color_list, type_list, size_list, other_list):
    u"""それぞれのリストの開始数をアップデートする。
    """
    if title in color_list[1]:
        # color_count = start_colum
        color_list[0] = start_colum
    elif title in type_list[1]:
        # type_count = start_colum
        type_list[0] = start_colum
    elif title in size_list[1]:
        # size_count = start_colum
        size_list[0] = start_colum
    else:
        # other_count = start_colum
        other_list[0] = start_colum


class Drmartone(Scraping):
    u"""Scrapingクラス
    """

    def get_only_number(data):
        u"""
        * データから数値のみを抜き出す。(1,280件) -> ['1','280']
        * 結果のリストをつなげる。['1','280'] -> 1280
        * intに変換する。
        戻り値 : int
        """
        # 数字のみを抜き出す。(1,280件) -> ['1','280']
        match_list = re.findall(r"\d+", data)
        str_data = ''
        int_data = 0
        for count in match_list:
            str_data += str(count)
        int_data = int(str_data)

        return int_data

    def get_page(self, url):
        u"""urlを受け取りページを取得する。
        """
        try:
            # old_page = driver.find_element_by_tag_name('html')
            self.driver.get(url)
        except HTTPError as error_code:
            logprint(url)
            logprint(error_code)
            return None
        except URLError as error_code:
            logprint("The server could not be found!")
            logprint(error_code)
            return None
        except RemoteDisconnected as error_code:
            logprint("Error! RemoteDisconnected")
            logprint(error_code)
            return None
        except WebDriverException as error_code:
            logprint("Error! WebDriverException")
            logprint(error_code)
            return None

        return self.driver

    def execute_login(self, login_dict):
        u"""ログインを実行する。
        """
        try:
            self.driver.find_element_by_name(
                login_dict['login_id_name']).send_keys(login_dict['login_id'])
            self.driver.find_element_by_name(
                login_dict['password_name']).send_keys(login_dict['password'])
            self.driver.find_element_by_xpath(
                login_dict['submit_path']).click()
        except NoSuchElementException:
            return None

        return self.driver

    def execute_link_click(self, xpath):
        u"""リンクをクリックする。
        """
        try:
            self.driver.find_element_by_xpath(xpath).click()
        except NoSuchElementException:
            return None

        return self.driver

    def execute_search(self, input_list, submit_path):
        u"""リンクをクリックする。
        引数:
            * input_list: [xpath, 値]となっている。
        """
        for value in input_list:
            # element = self.driver.find_element_by_xpath(value[0])
            element = self.driver.find_element_by_name(value[0])
            if element.get_attribute('type') == 'checkbox':
                if element.is_selected():
                    element.click()
            else:
                element.send_keys(value[1])

        try:
            self.driver.find_element_by_xpath(submit_path).click()
            time.sleep(20)
        except NoSuchElementException:
            logprint('xpathの指定が間違っています。')
            logprint(submit_path)
            return None

        return self.driver

    def get_page_information(self, xpath):
        u"""ページの情報を出力する。
        """
        page_number = self.driver.find_element_by_xpath(
            # xpath).get_attribute('outerHTML')
            xpath).text
        logprint(page_number)

    def is_link_enable(self, link_text):
        u"""
        目的: 引数で与えられたリンクが存在するか
        戻り値:
            * True - 存在する。
            * False - 存在しない。
        """
        try:
            link_exists = self.driver.find_element_by_link_text(
                link_text).is_enabled()
        except NoSuchElementException:
            logprint(link_text + 'は見つかりません。')
            return False
        else:
            return link_exists

    def get_next_page(self, link_text):
        u"""
        目的: 引数で与えられたリンクをクリックする
        引数:
            * link_text - リンクのテキスト
        戻り値:
            * TrueかFalseを返す
        """
        try:
            # next button '次のページ'をクリックする
            old_page = (self.driver.find_element_by_tag_name('html'))
            self.driver.find_element_by_link_text(link_text).click()
            WebDriverWait(self.driver, 30).until(
                EC.staleness_of(old_page))
        except NoSuchElementException as error_code:
            logprint('NoSuchElementException')
            logprint(error_code)
            return False
        except StaleElementReferenceException as error_code:
            logprint('StaleElementReferenceException')
            logprint(error_code)
            return False
        except TimeoutException as error_code:
            logprint('TimeoutException')
            logprint(error_code)
            return False
        except WebDriverException as error_code:
            logprint('WebDriverException')
            logprint(error_code)
            return False
        else:
            return True

    @staticmethod
    def get_phantom_page(url, driver):
        u"""urlを受け取りページを取得する。
        """

        try:
            # 0.2秒から2秒の間でランダムにスリープする
            time.sleep(2/random.randint(1, 10))
            old_page = driver.find_element_by_tag_name('html')
            driver.get(url)
        except HTTPError as error_code:
            logprint(url)
            logprint(error_code)
            return None
        except URLError as error_code:
            logprint("The server could not be found!")
            logprint(error_code)
            return None
        except RemoteDisconnected as error_code:
            logprint("Error! RemoteDisconnected")
            logprint(error_code)
            return None
        except WebDriverException as error_code:
            logprint("Error! WebDriverException")
            logprint(error_code)
            return None

        try:
            WebDriverWait(driver, 30).until(
                EC.staleness_of(old_page)
                )
        except TimeoutException as error_code:
            logprint("Error! TimeoutException")
            logprint(error_code)
            return None

        return driver

    def get_product_link(self, product_pattern):
        u"""
        目的 : 商品個別のページを返す。
        引数 :
                * product_pattern -- 正規表現
        設定 :
                *
        戻り値 : link_list -- リンクのリスト
        例外発行 : なし
        処理方式:
            * <div class="mdItemList">以下のaタグでループする。
            * aタグのhref属性の値をlink_listに格納する。
        """

        link_list = []

        try:
            links = (self.product_page_driver.find_elements_by_xpath
                     ("//div[@class='mdItemList']/div/div/ul/li/dl/dd/a"))
        except StaleElementReferenceException as error_code:
            logprint('StaleElementReferenceException')
            logprint(error_code)
        except WebDriverException as error_code:
            logprint('WebDriverException')
            logprint(error_code)
        else:
            for link in links:
                try:
                    new_page = link.get_attribute('href')
                except StaleElementReferenceException as error_code:
                    logprint('StaleElementReferenceException')
                    logprint(error_code)
                else:
                    # 商品パターンの処理
                    if product_pattern.search(new_page):
                        link_list.append(new_page)

        return link_list

    def get_path_list(self, driver, xpath):
        u"""driverとxpathを受け取りpathを返す。
        * 先頭の「ドクターマート介護用品」は不要なので省く。
        * 「...」を「MRI」に変換する。
        """
        bound_path = ''

        path_list = self.get_list_by_xpath(
            driver,
            xpath)

        for path in path_list[1:]:
            # 末尾の'>'を取り除く
            path = path.text.replace('>', '').strip()
            path = path.replace('爪きり・ハサミ・ルー...', '爪きり・ハサミ・ルーペ')
            path = path.replace('エアロバイク・ルーム...', 'エアロバイク・ルームランナー')
            path = path.replace('補助いす・いす・座い...', '補助いす・いす・座いす')
            path = path.replace('...', '・MRI')
            if len(bound_path) == 0:
                bound_path = path
            else:
                bound_path = bound_path + ':' + path

        return bound_path

    def follow_item_list(self, url, product_pattern):
        u"""
        目的 : 商品のリストが表示されるページのurlを受け取りリンクを返す。
        引数 :
                * url - URL
                * product_pattern -- 商品のページを表す正規表現
        設定 :
                *
        戻り値 : url_list -- urlのリスト
        例外発行 : なし
        処理方式:
            * <div class="elHeader"><h2><span>を探す。何件かの情報
            * ,(カンマ)を除く処理
            * 「何件が該当する」を取得してログで表示する。
            * (1)このページにある商品情報を取得する。
            * (2)次のページというリンクテキストがあればクリックする。
            * (1)、(2)でループする。
        """

        link_list = set()

        self.get_phantom_page(url, self.product_page_driver)

        product_count_text = self.get_text_by_xpath(
            self.product_page_driver,
            "//div[@class='elHeader']/h2/span",
            '該当する件数が見つかりませんでした。')
        if product_count_text == '':
            return link_list

        # 例えば1,230件のように','カンマが含まれる場合にも対応する。
        int_data = self.get_only_number(product_count_text)

        logprint(str(int_data) + '件が該当します。')
        logprint(str(int(int_data / 20 + 1)) + 'ページあります')

        # path(カテゴリ)を取得
        bound_path = self.get_path_list(
            self.product_page_driver,
            "//div[@id='TopSPathList1']/ol/li")

        # クリックする処理。
        # クリック回数 = 商品リストの数 ÷ 20(1ページの表示数) - 1
        i = 0
        while True:
            # このページにある商品リストを調べる
            product_url_list = self.get_product_link(product_pattern)

            for product_url in product_url_list:
                link_list.add(product_url)

                if product_url not in self.product_page_list:
                    # 商品ごとの処理
                    self.product_page_list.append(product_url)
                    product_list = self.get_product_info(
                        product_url, bound_path)
                    self.csv_file.writerow(product_list)

            logprint(str(i+1) + 'ページを処理しました。')

            # 2秒から4秒の間でランダムにスリープする
            time.sleep(4/random.randint(1, 2))

            try:
                # next button '次のページ'をクリックする
                if self.product_page_driver.find_elements_by_link_text(
                        '次のページ'):
                    self.product_page_driver.find_element_by_link_text(
                        '次のページ').click()
                    old_page = (self.product_page_driver
                                .find_element_by_tag_name('html'))
                    WebDriverWait(self.product_page_driver, 30).until(
                        EC.staleness_of(old_page)
                        )
                else:
                    break
            except NoSuchElementException as error_code:
                logprint('NoSuchElementException')
                logprint(error_code)
                break
            except StaleElementReferenceException as error_code:
                logprint('StaleElementReferenceException')
                logprint(error_code)
                break
            except TimeoutException as error_code:
                logprint('TimeoutException')
                logprint(error_code)
                break
            except WebDriverException as error_code:
                logprint('WebDriverException')
                logprint(error_code)
                break

            i += 1

    def find_item_list(self, url, product_pattern):
        u"""
        目的 : 商品のリストが表示されるページのurlを受け取りリンクを返す。
        引数 :
            * url - URL
            * product_pattern -- 商品のページを表す正規表現
        設定 :
                *
        戻り値 : なし
        例外発行 : なし
        処理方式:
            * 与えられたurlでページをgetする。
            * カテゴリリストがあった場合はカテゴリリストに含まれるリンクで
            　再帰
        """

        logprint(url + ' を処理します。')

        # 引数のurlでページをget
        self.get_phantom_page(url, self.category_driver)

        if self.category_driver is None:
            logprint('ページの取得に失敗しました。')
            return None

        # カテゴリリストに含まれるリンクのリストを取得
        cent_cat = ("//div[@id='CentCategoryList1']" +
                    "/div/div/div/div[2]/ul/li/dl/dd[1]/a")

        category_links = self.get_list_by_xpath(
            self.category_driver,
            cent_cat)

        url_list = []
        for link_object in category_links:
            url_list.append(link_object.get_attribute('href'))

        for category_url in url_list:
            # 引数のurlでページをget
            self.get_phantom_page(category_url, self.category_driver)

            if self.category_driver is None:
                logprint('ページの取得に失敗しました。')
                return None

            # カテゴリリストに含まれるリンクのリストを取得
            cent_cat = ("//div[@id='CentCategoryList1']" +
                        "/div/div/div/div[2]/ul/li/dl/dd[1]/a")

            category_links = self.get_list_by_xpath(
                self.category_driver,
                cent_cat)

            self.find_item_list(category_url, product_pattern)

        # 商品リストの処理
        self.follow_item_list(url, product_pattern)

        logprint(str(len(self.product_page_list)) + '個の商品を処理しました。')

        return

    def get_absolute_url(self, source):
        u"""起点になるurlとhrefの値を受け取り
        相対パスだったら絶対パスに変換して返す
        """

        absolute_url = ''
        # 相対パスを絶対パスに加工
        if source.startswith('/'):
            source = source[1:]
            absolute_url = self.base_url + source

        # 相対パスを絶対パスに加工
        # ページのリンクが'./page=2&cfrom=A00000'という形式になっている
        if source.startswith('./'):
            source = source[2:]
            absolute_url = self.base_url + source

        return absolute_url

    @staticmethod
    def get_text_by_xpath(phantom_page, xpath, error_message=''):
        u"""driverと検索するclassの名前を受け取り結果を返す。
        目的:
            * xpathに一致するテキストを返す
            * 一致しなかったらエラーメッセージを出力する
            * 一致しなかったら空文字列を返す。
        引数:
            * phantom_page: driver
            * xpath: 検索するxpath
            * error_message: 目的のデータがなかった時のエラーメッセージ
        戻り値 :
            * data : xpathに一致したテキスト
            * '' : データが一致しなかった時
        """
        try:
            data = phantom_page.find_element_by_xpath(xpath).text
        except NoSuchElementException:
            if error_message is '':
                pass
            else:
                logprint(error_message)
            return ''
        except WebDriverException:
            return ''

        data = bytes(data, 'utf-8').decode('utf-8')

        return data

    @staticmethod
    def get_attribute_by_xpath(phantom_page, xpath, attribute):
        u"""driverと検索するclassの名前を受け取り結果を返す。
        """
        try:
            data = (phantom_page
                    .find_element_by_xpath(xpath).get_attribute(attribute))
        except NoSuchElementException:
            return None
        except WebDriverException:
            return None

        return data

    @staticmethod
    def get_attribute_list_by_xpath(phantom_page, xpath, attribute):
        u"""driverと検索するclassの名前を受け取り結果のリストを返す。
        """
        return_list = []
        try:
            data_list = (phantom_page
                         .find_elements_by_xpath(xpath))
        except NoSuchElementException:
            return None
        except WebDriverException:
            return None

        for data in data_list:
            return_list.append(data.get_attribute(attribute))

        return return_list

    @staticmethod
    def get_list_by_xpath(driver, xpath):
        u"""driverとxpathを受け取り結果をリストで返す。
        戻り値:
            * 見つかった時: リンクのリスト
            * 見つからなかった時: None
        """

        try:
            return_list = driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            return None
        except WebDriverException:
            return None

        return return_list

    @staticmethod
    def get_select_list_by_xpath(driver, xpath):
        u"""driverとxpathを受け取り結果をリストで返す。
        """

        return_list = []
        try:
            selections = driver.find_elements_by_xpath(xpath)
        except NoSuchElementException:
            return None
        except WebDriverException:
            return None

        i = 0
        # select -> <p><span><select><option>
        for select in selections:
            try:
                select_name = select.find_element_by_xpath(
                    xpath +
                    "[" +
                    str(i + 1) +
                    "]/select").get_attribute("name")
                return_list.append([select_name])

                option_list = select.find_elements_by_xpath(
                    xpath +
                    "[" +
                    str(i + 1) +
                    "]/select/option")

                for option in option_list:
                    if option.text == '選択してください':
                        pass
                    else:
                        return_list[i].append(option.text)
            except NoSuchElementException:
                pass
            except WebDriverException:
                pass

            i += 1

        return return_list

    @staticmethod
    def get_selection_list(data_list):
        u"""選択肢の処理
        """
        return_list = [''] * (160)

        color_list = [0, [
            'カラー', '色', 'カラー（タイプ）', 'カラー・タイプ',
            'カラー（音）', 'タイプ／カラー', 'タイプ(カラー)', 'タイプ（カラー）',
            '本体カラー', '塗色', 'カラータイプ／袋', 'タイヤカラー',
            '張地カラー', 'ユニットカラー', 'グリップカラー', '棚・手すりカラー',
            '棚カラー', '天板カラー', '布張り地カラー', 'カバーカラー',
            'バッグカラー', 'シートカラー', 'シートカラー（タイプ）', 'フレームカラー',
            '頭キャップカラー', '木部カラー', 'バックサポートカラー', 'ボディカラー',
            'カラー（材質）'
        ]]
        type_list = [40, [
            'キャスター', 'ハンガー部', 'ハンドリム外径', '右用／左用',
            '強さ', '犬種', '材質', '取付金具タイプ',
            '種類', '周波数（ch）', '度数', '猫の種類',
            '肘掛け', '負荷', '風味', '名称',
            '毛の硬さ', '名称／型番', '香り', 'タイプ',
            'シートタイプ', '柄', '左右', 'ヘッドサポートタイプ',
            '固さ', 'アームサポート', '取付位置', '選択枝2',
            '味', 'レバー位置', 'カバータイプ', '操作側'
        ]]
        size_list = [80, [
            '駆動輪サイズ', '高さ', '座幅サイズ', '座面',
            '座面高', '座面幅', '床下', '長さ',
            '幅', 'サイズ', '座幅', '座面高さ',
            '前座高', '前座幅', 'サイズ（カラー）', 'サイズ（cm）',
            'サイズ（cm)', '厚さ', 'タイヤサイズ', 'キャスタサイズ',
            'ティッピングパイプ径', '幅サイズ', '最うz'
        ]]
        other_list = [120]

        for data in data_list:
            title = data[0]
            start_colum = decide_start_column(
                data, color_list, type_list, size_list, other_list)

            for option in data[1:]:
                try:
                    return_list[start_colum] = (
                        bytes(str(title) + ':' + option, 'utf-8')
                        .decode('utf-8'))
                except IndexError:
                    logprint('Error! IndexError')
                else:
                    start_colum += 1

            set_start_column(
                title,
                start_colum,
                color_list,
                type_list,
                size_list,
                other_list)

        return return_list

    def set_productlist_one_to_seven(self, product_list, url):
        u"""product_listの1から7までのデータを取得してsetして返す。
        """
        # name
        product_list[0] = self.get_text_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoTitle']",
            '商品はありません。')
        if product_list[0] is '':
            not_file = self.get_text_by_xpath(
                self.driver,
                "//div[@id='CentPageErr1']/table",)
            if not_file.startswith('商品情報を表示できません。'):
                write_not_find_page_url(url)

            return None

        # jan
        jan = self.get_text_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoCode']/p")

        if jan is not '':
            # ：(コロン)は全角
            jan = jan.split('：')[1]
            product_list[1] = jan

        # abstract
        product_list[2] = self.get_text_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoComment']",
            'abstractはありません。')

        # price
        product_list[3] = self.get_text_by_xpath(
            self.driver,
            "//span[@class='elNum']",
            '価格はありません。')

        # explanation
        explanation = self.get_attribute_by_xpath(
            self.driver, "//p[@class='pt2']", 'outerHTML')

        if explanation is not None:
            product_list[4] = bytes(explanation, 'utf-8').decode('utf-8')

        p_list = self.get_list_by_xpath(
            self.driver,
            "//div[@id='abuserpt']/p")

        for inner in p_list:
            if inner.text.startswith('商品コード：'):
                code = inner.text.split('：')[1]
                product_list[5] = code

        # caption
        product_list[6] = self.get_text_by_xpath(
            self.driver,
            "//div[@id='CentItemCaption1']/p",
            '商品説明がありません。')

        return product_list

    def set_productlist_eight_to_twelve(self, product_list):
        u"""product_listの8列目から12列目までのデータを取得してsetして返す。
        """
        # image
        image_attrs_list = (self.get_attribute_list_by_xpath(
            self.driver,
            "//ul[@class='elThumbnail elW300 cf']/li/a/img",
            "src"))
        for image_count, image_attrs in enumerate(image_attrs_list):
            image_name = re.search(r"drmart-1_[\da-z-_]+", image_attrs)
            if image_name is None:
                pass
            else:
                image_name = image_name.group() + '.jpg'
                # imageをダウンロードして保存する。
                imagefile.download_and_save_dir_direct(
                    image_attrs,
                    'image',
                    image_name)
                product_list[7 + image_count] = bytes(
                    image_name, 'utf-8').decode('utf-8')

        return product_list

    def set_productlist_thirteen(self, product_list):
        u"""product_listの13列目のデータを取得してsetして返す。
        """
        # Gimage1
        image_attrs = (self.get_attribute_by_xpath
                       (self.driver,
                        "//div[@id='CentItemAdditional1']/a", "href"))
        if image_attrs is None:
            image_attrs = (self.get_attribute_by_xpath
                           (self.driver,
                            "//div[@id='CentItemAdditional2']/a",
                            "href"))
        else:
            image_name = re.search(r"[\da-zA-Z-_]+.jpg", image_attrs)
            if image_name is None:
                pass
            else:
                # imageをダウンロードして保存する。
                image_name = image_name.group()
                imagefile.download_and_save_dir_direct(
                    image_attrs,
                    'image',
                    image_name)
                product_list[12] = bytes(image_name, 'utf-8').decode('utf-8')

        return product_list

    def set_productlist_fourteen(self, product_list, path):
        u"""product_listの14列目のデータを取得してsetして返す。
        """
        # path
        if path is '':
            # path(カテゴリ)を取得
            path = self.get_path_list(
                self.driver,
                "//div[@id='TopSPathList1']/ol/li")
            path = path.split(':')[0]

        product_list[13] = bytes(path, 'utf-8').decode('utf-8')

        return product_list

    def set_productlist_fifteen(self, product_list):
        u"""product_listの14列目のデータを取得してsetして返す。
        """
        # list
        data_list = self.get_select_list_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoOption']/p")

        if data_list is not None:
            selection_list = self.get_selection_list(data_list)

            for select_count, selection in enumerate(selection_list):
                try:
                    product_list[14 + select_count] = selection
                except IndexError:
                    logprint('Error! IndexError')
                else:
                    pass

        return product_list

    def get_product_info(self, url, path=''):
        u"""商品個別のurlを受け取り、商品情報をリストにして返す
        引数:
            * url
            * path: 上位のページから遷移した場合にpathを引数として引き継ぐ。
                直接遷移した場合はpathを渡されない。
        """
        if self.driver is None:
            logprint('driverの取得に失敗しています。')
            return None

        logprint(url)

        self.get_phantom_page(url, self.driver)

        # 要素数が34のリストを作成する。
        product_list = [''] * 174

        product_list = self.set_productlist_one_to_seven(product_list, url)
        if product_list is None:
            return None

        product_list = self.set_productlist_eight_to_twelve(product_list)
        product_list = self.set_productlist_thirteen(product_list)
        product_list = self.set_productlist_fourteen(product_list, path)
        product_list = self.set_productlist_fifteen(product_list)

        return product_list

    def get_links(self, url, link_pattern, xpath):
        u"""
        目的 : トップページを引数として受け取りページ内の商品カテゴリの
               リストを返す。
        引数 :
            * url -- URL
            * link_pattern -- リンクの正規表現
            * xpath -- linkへのxpath
        設定 :
                * self.page_list -- ページのURLのリスト
        戻り値 : self.page_list -- ページのURLのリスト
        例外発行 : なし
        処理方式:
            * 20回ごとにメッセージを出力する。
            * ページをgetする。
            * <div id="NaviStrCategory1">を探す。
            * <a ...>タグを探してループする。
            * href属性の値を取得する。
        """

        logprint(url)

        link_serial_number = 0

        if link_serial_number % 20 == 0:
            if link_serial_number != 0:
                logprint(
                    str(link_serial_number) + '個目のカテゴリを処理しています。')

        self.get_phantom_page(url, self.driver)

        links = self.get_list_by_xpath(
            self.driver,
            xpath)

        if links is None:
            self.page_list = None
        else:
            for link in links:
                new_page = link.get_attribute('href')

                # リンク追跡パターン
                if link_pattern.search(new_page):
                    if new_page not in self.page_list:
                        self.page_list.append(new_page)

        link_serial_number += 1

        return self.page_list


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        self.drmartone = Drmartone('http://store.shopping.yahoo.co.jp')

    def test_get_product_info(self):
        u"""商品情報を取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart-1/cm-234176.html'
        product_list = self.drmartone.get_product_info(url)

        if product_list is None:
            self.assertEqual(product_list, None)
        else:
            self.assertEqual(len(product_list), 174)

    def test_not_find_product(self):
        u"""商品情報を取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart-1/cm-200000.html'
        product_list = self.drmartone.get_product_info(url)

        self.assertEqual(product_list, None)

    def test_get_product_info_cm(self):
        u"""商品情報を取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart-1/cm-218372.html'
        product_list = self.drmartone.get_product_info(url)

        if product_list is None:
            self.assertEqual(product_list, None)
        else:
            self.assertEqual(len(product_list), 174)
            self.assertEqual(product_list[5], 'cm-218372')

    def test_get_product_info_color(self):
        u"""商品情報を取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart-1/cm-207520.html'
        product_list = self.drmartone.get_product_info(url)

        if product_list is None:
            self.assertEqual(product_list, None)
        else:
            self.assertEqual(len(product_list), 174)
            self.assertEqual(product_list[5], 'cm-207520')
            self.assertEqual(product_list[14], 'シートカラー:A3（紺チェック）')
            self.assertEqual(product_list[23], 'フレームカラー:シルバー')

    def test_get_links(self):
        u"""linkを取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart/'
        link_pattern = re.compile(
            r'http://store.shopping.yahoo.co.jp/drmart/[a-z\d]+.html')
        xpath = "//div[@id='NaviStrCategory1']/div/ul/li/a[2]"
        links = self.drmartone.get_links(
            url,
            link_pattern,
            xpath)

        self.assertEqual(len(links), 40)

    def test_get_links_not_find(self):
        u"""linkを取得するテスト見つからないケース
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart/'
        link_pattern = re.compile(
            r'http://store.shopping.yahoo.co.jp/drmart/[a-z\d]+.html')
        xpath = "//div[@id='NaviStrCategory1']/div?/ul/li/a[2]"
        links = self.drmartone.get_links(
            url,
            link_pattern,
            xpath)

        self.assertEqual(links, None)

    def tearDown(self):
        u"""クローズ処理など
        """
        pass

if __name__ == '__main__':
    unittest.main()

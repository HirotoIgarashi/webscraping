# -*- conding: utf-8 -*-
u"""スクレイピング用のライブラリ
"""
import os
import re
import random
import time
from urllib.error import HTTPError
from urllib.error import URLError
from http.client import RemoteDisconnected
import unittest
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# My library
import imagefile
import logmessage
import csvfile
import textfile


class Scraping():
    u"""Scrapingクラス
    """
    def __init__(self, base_url):
        headers = (
            {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)"
                           "AppleWebKit 537.36 (KHTML, like Gecko) Chrome",
             "Accept": "text/html,application/xhtml+xml,application/xml;"
                       "q=0.9,image/webp,*/*;q=0.8"})

        self.page_list = []
        self.product_page_list = []

        self.base_url = base_url

        # Csvfileクラス
        self.csv_file = csvfile.Csvfile('./drmart-1/')

        for key, value in enumerate(headers):
            (webdriver
             .DesiredCapabilities
             .PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)]) = value

        def get_phantom_driver():
            u"""phantomJSのドライバーを取得する。
            """
            try:
                if os.name == 'posix':
                    driver = webdriver.PhantomJS(
                        executable_path='lib/phantomjs')
                elif os.name == 'nt':
                    driver = webdriver.PhantomJS(
                        executable_path='lib/phantomjs.exe')
                else:
                    logmessage.logprint('Unsupported OS')
            except URLError as error_code:
                logmessage.logprint('ドライバーの取得に失敗しました。')
                logmessage.logprint(error_code)
                return None
            except WebDriverException as error_code:
                logmessage.logprint('PhantomJSのサービスとの接続に失敗しました。')
                logmessage.logprint('libディレクトリにPhantomJSの実行ファイルが必要です。')
                # logmessage.logprint(error_code)
                return None

            return driver

        self.driver = get_phantom_driver()
        if self.driver is not None:
            self.category_driver = get_phantom_driver()
            self.product_page_driver = get_phantom_driver()

    @staticmethod
    def get_phantom_page(url, driver):
        u"""urlを受け取りページを取得する。
        """

        try:
            # 0.2秒から2秒の間でランダムにスリープする
            # time.sleep(2/random.randint(1, 10))
            old_page = driver.find_element_by_tag_name('html')
            driver.get(url)
            # print(driver.current_url)
        except HTTPError as error_code:
            logmessage.logprint(url)
            logmessage.logprint(error_code)
            return None
        except URLError as error_code:
            logmessage.logprint("The server could not be found!")
            logmessage.logprint(error_code)
            return None
        except RemoteDisconnected as error_code:
            logmessage.logprint("Error! RemoteDisconnected")
            logmessage.logprint(error_code)
            return None
        except WebDriverException as error_code:
            logmessage.logprint("Error! WebDriverException")
            logmessage.logprint(error_code)
            return None

        try:
            WebDriverWait(driver, 30).until(
                EC.staleness_of(old_page)
                )
        except TimeoutException as error_code:
            logmessage.logprint("Error! TimeoutException")
            logmessage.logprint(error_code)
            return None

        # print(driver.current_url)

        return driver

    def get_page(self, url):
        u"""urlを受け取りページを取得する。
        """

        try:
            # 0.2秒から2秒の間でランダムにスリープする
            time.sleep(2/random.randint(1, 10))
            self.driver.get(url)
        except HTTPError as error_code:
            logmessage.logprint(url)
            logmessage.logprint(error_code)
        except URLError as error_code:
            logmessage.logprint("The server could not be found!")
            logmessage.logprint(error_code)
        else:
            page_source = self.driver.page_source
            bs_obj = BeautifulSoup(page_source, "lxml")

        return bs_obj

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
            logmessage.logprint('StaleElementReferenceException')
            logmessage.logprint(error_code)
        except WebDriverException as error_code:
            logmessage.logprint('WebDriverException')
            logmessage.logprint(error_code)
        else:
            for link in links:
                try:
                    new_page = link.get_attribute('href')
                except StaleElementReferenceException as error_code:
                    logmessage.logprint('StaleElementReferenceException')
                    logmessage.logprint(error_code)
                else:
                    # 商品パターンの処理
                    if product_pattern.search(new_page):
                        link_list.append(new_page)

        return link_list

    @staticmethod
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

        logmessage.logprint(str(int_data) + '件が該当します。')
        logmessage.logprint(str(int(int_data / 20 + 1)) + 'ページあります')

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

            logmessage.logprint(str(i+1) + 'ページを処理しました。')

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
                logmessage.logprint('NoSuchElementException')
                logmessage.logprint(error_code)
                break
            except StaleElementReferenceException as error_code:
                logmessage.logprint('StaleElementReferenceException')
                logmessage.logprint(error_code)
                break
            except TimeoutException as error_code:
                logmessage.logprint('TimeoutException')
                logmessage.logprint(error_code)
                break
            except WebDriverException as error_code:
                logmessage.logprint('WebDriverException')
                logmessage.logprint(error_code)
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

        logmessage.logprint(url + ' を処理します。')

        # 引数のurlでページをget
        self.get_phantom_page(url, self.category_driver)

        if self.category_driver is None:
            logmessage.logprint('ページの取得に失敗しました。')
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
                logmessage.logprint('ページの取得に失敗しました。')
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

        logmessage.logprint(str(len(self.product_page_list)) + '個の商品を処理しました。')

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
    def get_by_tag_name(phantom_page, tag_name):
        u"""driverと検索するtagを受け取り結果を返す。
        """
        try:
            data = phantom_page.find_element_by_tag_name(tag_name).text
        except NoSuchElementException as error_code:
            logmessage.logprint('NoSuchElementException')
            logmessage.logprint(error_code)
            return None
        except WebDriverException as error_code:
            logmessage.logprint('WebDriverException')
            logmessage.logprint(error_code)
            return None
        else:
            return data

    @staticmethod
    def get_by_class_name(phantom_page, class_name):
        u"""driverと検索するclassの名前を受け取り結果を返す。
        """
        try:
            data = phantom_page.find_element_by_class_name(class_name).text
        except NoSuchElementException:
            logmessage.logprint('NoSuchElementException')
            return None
        except WebDriverException:
            logmessage.logprint('WebDriverException')
            return None

        return data

    @staticmethod
    def get_text_by_xpath(phantom_page, xpath, error_message=''):
        u"""driverと検索するclassの名前を受け取り結果を返す。
        戻り値 :
            * data : 一致したデータ
            * '' : データが一致しなかった時
        """
        try:
            data = phantom_page.find_element_by_xpath(xpath).text
        except NoSuchElementException:
            if error_message is '':
                pass
            else:
                logmessage.logprint(error_message)
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
    def get_category_data(bs_obj):
        u"""BeautifulSoup Objectを受け取りカテゴリデータを返す。
        """
        data_list = []

        try:
            for ul_tag in bs_obj.findAll(
                    "nav", {"class": "breadcrumbs"})[0].findAll("ul"):
                category_list = ul_tag.findAll("a", {"href": True})
                contents = ''
                for category in category_list:
                    if category.get_text() == 'ホーム':
                        pass
                    else:
                        if len(contents) == 0:
                            contents = category.get_text()
                        else:
                            contents = contents + ';' + category.get_text()
                data_list.append(contents)

        except NoSuchElementException as error_code:
            logmessage.logprint('NoSuchElementException')
            logmessage.logprint(error_code)
            return ''
        except IndexError as error_code:
            logmessage.logprint('IndexError')
            logmessage.logprint(error_code)
            return ''

        category_data = ''

        for data in data_list:
            if len(category_data) == 0:
                category_data = data
            else:
                category_data = category_data + '\n' + data

        return category_data

    @staticmethod
    def get_description_list(desc_list):
        u"""description 説明の処理
        """
        description_list = []

        for item in desc_list:
            desc = str(item.h2) + str(item.ul)

            description_list.append(desc)

        return description_list

    @staticmethod
    def get_selection_list(data_list):
        u"""選択肢の処理
        """
        return_list = [''] * (530)

        count_dict = {
            'カラー': 0,
            '名称／型番': 40,
            'サイズ': 70,
            '香り': 100,
            'タイプ': 130,
            'シートカラー': 160,
            '座幅': 170,
            'シートタイプ': 180,
            '座面高さ': 190,
            'シートカラー（タイプ）': 200,
            '前座高': 210,
            '前座幅': 220,
            '柄': 230,
            'フレームカラー': 240,
            '左右': 250,
            '頭キャップカラー': 260,
            'ヘッドサポートタイプ': 270,
            'サイズ（カラー）': 280,
            '固さ': 290,
            'タイプ(カラー)': 300,
            'アームサポート': 310,
            '取付位置': 320,
            '色': 330,
            'カラー（タイプ）': 340,
            '選択枝2': 350,
            '味': 360,
            'サイズ（cm）': 370,
            '天板カラー': 380,
            'レバー位置': 390,
            '布張り地カラー': 400,
            '厚さ': 410,
            'タイヤサイズ': 420,
            'カバーカラー': 430,
            'カバータイプ': 440,
            'キャスタサイズ': 450,
            'バッグカラー': 460,
            'ティッピングパイプ径': 470,
            '木部カラー': 480,
            '操作側': 490,
            'バックサポートカラー': 500,
            'ボディカラー': 510,
            '': 520
        }

        # for data in enumerate(data_list):
        for data in data_list:
            print(data)
            # 初期値として510を設定。count_dictのキーにない場合は520に。
            start_colum = 520
            # 例えば、key: カラー, value: color
            # 半角の')'を全角の'）'に変換
            trans_data = data[0].replace('cm)', 'cm）')
            for key, value in count_dict.items():
                if trans_data == key:
                    start_colum = value
                    break

            for option_count, option in enumerate(data[1:]):
                try:
                    return_list[start_colum + option_count] = (
                        bytes(data[0] + ':' + option, 'utf-8')
                        .decode('utf-8'))
                except IndexError:
                    logmessage.logprint(start_colum + option_count)
                    logmessage.logprint('Error! IndexError')
                else:
                    pass

        return return_list

    def get_product_info(self, url, path=''):
        u"""商品個別のurlを受け取り、商品情報をリストにして返す
        """
        print(self)
        if self.driver is None:
            logmessage.logprint('driverの取得に失敗しています。')
            return None

        not_find = textfile.TextFile('result', 'not_find_product.txt')
        not_find_file = not_find.open_append_mode()

        logmessage.logprint(url)

        self.get_phantom_page(url, self.driver)

        # 要素数が34のリストを作成する。
        product_list = [''] * 544

        # name
        product_list[0] = self.get_text_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoTitle']",
            '商品はありません。')
        if product_list[0] is '':
            not_file = self.get_text_by_xpath(
                self.driver,
                "//div[@id='CentPageErr1']/table",
            )
            if not_file.startswith('商品情報を表示できません。'):
                not_find_file.write(url + '\n')
            return None

        # jan
        jan = self.get_text_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoCode']/p"
            )

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

        # code
        code = self.get_text_by_xpath(
            self.driver,
            "//div[@id='abuserpt']/p[2]",
            '商品コードはありません。')

        if code is not '':
            # ：(コロン)は全角
            code = code.split('：')[1]
            product_list[5] = code

        # caption
        product_list[6] = self.get_text_by_xpath(
            self.driver,
            "//div[@id='CentItemCaption1']/p",
            '商品説明がありません。')

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
                imagefile.download_and_save_dir_direct(image_attrs, image_name)
                product_list[7 + image_count] = bytes(
                    image_name, 'utf-8').decode('utf-8')

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
                imagefile.download_and_save_dir_direct(image_attrs, image_name)
                product_list[12] = bytes(image_name, 'utf-8').decode('utf-8')

        # path
        if path is '':
            # path(カテゴリ)を取得
            path = self.get_path_list(
                self.driver,
                "//div[@id='TopSPathList1']/ol/li")
            path = path.split(':')[0]

        product_list[13] = bytes(path, 'utf-8').decode('utf-8')

        # list
        data_list = self.get_select_list_by_xpath(
            self.driver,
            "//div[@class='mdItemInfoOption']/p")

        # print(data_list)
        if data_list is not None:
            selection_list = self.get_selection_list(data_list)

            for select_count, selection in enumerate(selection_list):
                try:
                    product_list[14 + select_count] = selection
                except IndexError:
                    logmessage.logprint('Error! IndexError')
                else:
                    pass

        not_find_file.close()

        return product_list

    def get_links(self, url_list, link_pattern):
        u"""
        目的 : トップページを引数として受け取りページ内の商品カテゴリの
               リストを返す。
        引数 :
            * url_list -- URLのリスト
            * link_pattern -- リンクの正規表現
        設定 :
                * self.page_list -- ページのURLのリスト
        戻り値 : self.page_list -- ページのURLのリスト
        例外発行 : なし
        処理方式:
            * URLのリストでループする。
            * 20回ごとにメッセージを出力する。
            * ページをgetする。
            * <div id="NaviStrCategory1">を探す。
            * <a ...>タグを探してループする。
            * href属性の値を取得する。
        """

        link_serial_number = 0

        for url in url_list:
            if link_serial_number % 20 == 0:
                if link_serial_number != 0:
                    logmessage.logprint(
                        str(link_serial_number) + '個目のカテゴリを処理しています。')

            bs_obj = self.get_page(url)

            category_tag = bs_obj.find("div", {"id": "NaviStrCategory1"})

            # aタグでループする
            for link in category_tag.findAll("a"):
                if 'href' in link.attrs:

                    new_page = link.attrs['href']

                    new_page = self.get_absolute_url(new_page)

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
        self.scraping = Scraping('http://store.shopping.yahoo.co.jp')

    def test_get_product_info(self):
        u"""商品情報を取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart-1/cm-234176.html'
        product_list = self.scraping.get_product_info(url)

        if product_list is None:
            self.assertEqual(product_list, None)
        else:
            self.assertEqual(len(product_list), 544)

    def test_get_product_info_cm(self):
        u"""商品情報を取得するテスト
        """
        url = 'http://store.shopping.yahoo.co.jp/drmart-1/cm-218372.html'
        product_list = self.scraping.get_product_info(url)

        if product_list is None:
            self.assertEqual(product_list, None)
        else:
            self.assertEqual(len(product_list), 544)

    def tearDown(self):
        u"""クローズ処理など
        """
        pass
if __name__ == '__main__':
    unittest.main()

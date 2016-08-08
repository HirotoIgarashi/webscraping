# -*- conding: utf-8 -*-
u"""スクレイピング用のライブラリ
"""
import time
import unittest
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# My library
from logmessage import logprint
from scraping import Scraping


class Sanwachannel(Scraping):
    u"""サンワチャンネル用クラス
    """

    def execute_search(self, input_list, submit_path):
        u"""検索を実行する。
        引数:
            * input_list: [xpath, 値]となっている。
        """
        for value in input_list:
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
        try:
            page_number = self.driver.find_element_by_xpath(
                xpath).text
        except NoSuchElementException:
            logprint('xpathが見つかりません。')
            logprint(xpath)
        else:
            logprint(page_number)

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
            links = (self.product_driver.find_elements_by_xpath
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

    def get_product_page(self, row, link_text):
        u"""
        目的 :
            * 商品が表示されるリンクを受け取りクリックする。
        引数 :
            * row - 商品リストの行データ
            * link_text - リンクテキスト
        設定 :
                *
        戻り値 : なし
        例外発行 : なし
        """
        try:
            link_text = row.find_element_by_link_text('詳細を見る')
        except NoSuchElementException:
            return False
        else:
            url = link_text.get_attribute('href')
            self.get_product_info(url)

        return True

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

    def get_product_info(self, url):
        u"""商品個別のurlを受け取り、商品情報をリストにして返す
        引数:
            * url
            * path: 上位のページから遷移した場合にpathを引数として引き継ぐ。
                直接遷移した場合はpathを渡されない。
        """
        logprint(url)

        product_page = self.get_product_driver(url)

        xpath = "//div[@class='product_data_main']/p[@class='pname']"
        try:
            print(product_page.find_element_by_xpath(xpath).text)
        except NoSuchElementException:
            logprint(product_page.find_element_by_xpath(
                "//body").get_attribute('outerHTML'))
            logprint('商品名がありません')

        xpath = "//div[@class='p_line1 clfx']/p[@class='p_line_right pcode']"
        try:
            print(product_page.find_element_by_xpath(xpath).text)
        except NoSuchElementException:
            logprint('製品品番がありません')

        xpath = "//div[@class='p_line2 clfx']/p[@class='p_line_right']"
        try:
            print(product_page.find_element_by_xpath(xpath).text)
        except NoSuchElementException:
            logprint('JANコードがありません')

        xpath = "//div[@class='p_line3 clfx']/p[@class='p_line_right']"
        try:
            print(product_page.find_element_by_xpath(xpath).text)
        except NoSuchElementException:
            logprint('標準価格がありません')

        partition_price = ("//div[@class='p_line2 tp_4 clfx']" +
                           "/p[@class='p_line_right pprice']" +
                           "/span")
        try:
            print(product_page.find_element_by_xpath(
                partition_price).text)
        except NoSuchElementException:
            logprint('仕切価格がありません')

        explanation = ("//p[@class='fetr_img_right']")
        try:
            print(product_page.find_element_by_xpath(
                explanation).get_attribute('innerHTML'))
        except NoSuchElementException:
            logprint('商品説明がありません')

        image = ("//p[@class='product_img']/img")
        try:
            print(product_page.find_element_by_xpath(
                image).get_attribute('outerHTML'))
        except NoSuchElementException:
            logprint('画像がありません')

        # 要素数が1のリストを作成する。
        product_list = ['']

        return product_list


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """

    def setUp(self):
        u"""セットアップ
        """
        self.sanwachannel = Sanwachannel('https://cust.sanwa.co.jp/')

    # def test_get_page(self):
    #     u"""pageを取得するテスト
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     page = self.sanwachannel.get_page(url)
    #     data = page.find_element_by_xpath(
    #         '//body').get_attribute('outerHTML')
    #     self.assertTrue(data.startswith('<body'))

    # def test_execute_login(self):
    #     u"""loginするテスト
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     page = self.sanwachannel.get_page(url)

    #     login_div = "//div[@class='login_inaccount']"
    #     login_dict = {
    #         'login_id': "health-welfare@ghjapan.jp",
    #         'login_id_name': 'MailAddress',
    #         'password': "ghjapan006",
    #         'password_name': 'PassWord',
    #         'submit_path': login_div + "/p/a"
    #     }

    #     page = self.sanwachannel.execute_login(login_dict)
    #     data = page.find_element_by_xpath(
    #         '//body').get_attribute('outerHTML')
    #     company_name = page.find_element_by_xpath(
    #         "//p[@class='head_customer_name_top']").text
    #     self.assertTrue(data.startswith('<body'))
    #     self.assertEqual(company_name, 'GH株式会社')

    # def test_execute_link_click(self):
    #     u"""在庫照会をクリックして検索画面に遷移するテスト
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     page = self.sanwachannel.get_page(url)

    #     login_div = "//div[@class='login_inaccount']"
    #     login_dict = {
    #         'login_id': "health-welfare@ghjapan.jp",
    #         'login_id_name': 'MailAddress',
    #         'password': "ghjapan006",
    #         'password_name': 'PassWord',
    #         'submit_path': login_div + "/p/a"
    #     }

    #     self.sanwachannel.execute_login(login_dict)
    #     data = page.find_element_by_xpath(
    #     '//body').get_attribute('outerHTML')

    #     page = self.sanwachannel.execute_link_click(
    #         "//li/p/a/img[@alt='在庫照会']")
    #     data = page.find_element_by_xpath(
    #     '//body').get_attribute('outerHTML')

    #     self.assertTrue(data.startswith('<body'))

    # def test_execute_search(self):
    #     u"""検索画面に値をセットして検索を実行するテスト
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     page = self.sanwachannel.get_page(url)

    #     login_div = "//div[@class='login_inaccount']"
    #     login_dict = {
    #         'login_id': "health-welfare@ghjapan.jp",
    #         'login_id_name': 'MailAddress',
    #         'password': "ghjapan006",
    #         'password_name': 'PassWord',
    #         'submit_path': login_div + "/p/a"
    #     }

    #     self.sanwachannel.execute_login(login_dict)
    #     data = page.find_element_by_xpath(
    #         '//body').get_attribute('outerHTML')

    #     page = self.sanwachannel.execute_link_click(
    #         "//li/p/a/img[@alt='在庫照会']")

    #     input_list = [
    #         ["sProductCode", '-'], ["sProductName", ''],
    #         ["sJanCode", ''], ["sInventory", ''],
    #         ["sRegularPrice_Under", ''], ["sRegularPrice_TOP", ''],
    #         ["InAbolish", ''], ["DispImg", '']
    #     ]

    #     submit_path = "//img[@alt='この条件で検索']"

    #     page = self.sanwachannel.execute_search(input_list, submit_path)

    #     self.sanwachannel.get_page_information("//p[@class='result_amount']")

    #     self.assertTrue(data.startswith('<body'))

    # def test_is_link_enable(self):
    #     u"""「次のページへ」というリンクがあるかチェックする。
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     self.sanwachannel.get_page(url)

    #     login_div = "//div[@class='login_inaccount']"
    #     login_dict = {
    #         'login_id': "health-welfare@ghjapan.jp",
    #         'login_id_name': 'MailAddress',
    #         'password': "ghjapan006",
    #         'password_name': 'PassWord',
    #         'submit_path': login_div + "/p/a"
    #     }

    #     self.sanwachannel.execute_login(login_dict)
    #     # data = page.find_element_by_xpath(
    #     #     '//body').get_attribute('outerHTML')

    #     self.sanwachannel.execute_link_click(
    #         "//li/p/a/img[@alt='在庫照会']")

    #     input_list = [
    #         ["sProductCode", '-'], ["sProductName", ''],
    #         ["sJanCode", ''], ["sInventory", ''],
    #         ["sRegularPrice_Under", ''], ["sRegularPrice_TOP", ''],
    #         ["InAbolish", ''], ["DispImg", '']
    #     ]

    #     submit_path = "//img[@alt='この条件で検索']"

    #     self.sanwachannel.execute_search(input_list, submit_path)

    #     # if page is not None:
    #     #     data = page.find_element_by_xpath(
    #     #         '//body').get_attribute('outerHTML')
    #     #     print(data)
    #     # else:
    #     #     print('見つからなかった')

    #     self.sanwachannel.get_page_information("//p[@class='result_amount']")

    #     self.assertTrue(self.sanwachannel.is_link_enable("次のページへ"))
    #     self.assertFalse(self.sanwachannel.is_link_enable("Next Page"))

    def test_get_next_link(self):
        u"""「次のページへ」というリンクをクリックする。
        """
        url = 'https://cust.sanwa.co.jp/'
        self.sanwachannel.get_page(self.sanwachannel.driver, url)

        login_div = "//div[@class='login_inaccount']"
        login_dict = {
            'login_id': "health-welfare@ghjapan.jp",
            'login_id_name': 'MailAddress',
            'password': "ghjapan006",
            'password_name': 'PassWord',
            'submit_path': login_div + "/p/a"
        }

        self.sanwachannel.execute_login(self.sanwachannel.driver, login_dict)

        self.sanwachannel.execute_link_click(
            self.sanwachannel.driver, "//li/p/a/img[@alt='在庫照会']")

        input_list = [
            ["sProductCode", '-'], ["sProductName", ''],
            ["sJanCode", ''], ["sInventory", ''],
            ["sRegularPrice_Under", ''], ["sRegularPrice_TOP", ''],
            ["InAbolish", ''], ["DispImg", '']
        ]

        submit_path = "//img[@alt='この条件で検索']"

        self.sanwachannel.execute_search(input_list, submit_path)

        self.sanwachannel.get_page_information("//p[@class='result_amount']")

        i = 0
        while self.sanwachannel.is_link_enable("次のページへ"):
            if i > 1:
                break
            self.sanwachannel.get_next_page("次のページへ")
            self.sanwachannel.get_page_information(
                "//p[@class='result_amount']")
            i += 1

    def test_get_table(self):
        u"""「次のページへ」というリンクをクリックする。
        """
        url = 'https://cust.sanwa.co.jp/'
        self.sanwachannel.get_page(self.sanwachannel.driver, url)
        self.sanwachannel.get_page(self.sanwachannel.product_driver, url)

        login_div = "//div[@class='login_inaccount']"
        login_dict = {
            'login_id': "health-welfare@ghjapan.jp",
            'login_id_name': 'MailAddress',
            'password': "ghjapan006",
            'password_name': 'PassWord',
            'submit_path': login_div + "/p/a"
        }

        self.sanwachannel.execute_login(
            self.sanwachannel.driver, login_dict)
        self.sanwachannel.execute_login(
            self.sanwachannel.product_driver, login_dict)

        self.sanwachannel.execute_link_click(
            self.sanwachannel.driver, "//li/p/a/img[@alt='在庫照会']")

        input_list = [
            ["sProductCode", '-'], ["sProductName", ''],
            ["sJanCode", ''], ["sInventory", ''],
            ["sRegularPrice_Under", ''], ["sRegularPrice_TOP", ''],
            ["InAbolish", ''], ["DispImg", '']
        ]

        submit_path = "//img[@alt='この条件で検索']"

        self.sanwachannel.execute_search(input_list, submit_path)

        self.sanwachannel.get_page_information("//p[@class='result_amount']")
        rows = self.sanwachannel.get_table_row(
            "//table/tbody/tr")
        for row in rows:
            self.sanwachannel.get_product_page(row, '詳細を見る')

        i = 0
        while self.sanwachannel.is_link_enable("次のページへ"):
            if i > 1:
                break
            self.sanwachannel.get_next_page("次のページへ")

            self.sanwachannel.get_page_information(
                "//p[@class='result_amount']")
            rows = self.sanwachannel.get_table_row(
                "//table/tbody/tr")
            for row in rows:
                self.sanwachannel.get_product_page(row, '詳細を見る')

            i += 1

    def test_get_product_info(self):
        u"""「次のページへ」というリンクをクリックする。
        """
        url = 'https://cust.sanwa.co.jp/'
        self.sanwachannel.get_page(self.sanwachannel.driver, url)
        self.sanwachannel.get_page(self.sanwachannel.product_driver, url)

        login_div = "//div[@class='login_inaccount']"
        login_dict = {
            'login_id': "health-welfare@ghjapan.jp",
            'login_id_name': 'MailAddress',
            'password': "ghjapan006",
            'password_name': 'PassWord',
            'submit_path': login_div + "/p/a"
        }

        self.sanwachannel.execute_login(
            self.sanwachannel.driver, login_dict)
        self.sanwachannel.execute_login(
            self.sanwachannel.product_driver, login_dict)

        url = 'https://cust.sanwa.co.jp/products/detail.asp?code=MR-ERGST1'
        self.sanwachannel.get_product_info(url)

    def tearDown(self):
        u"""クローズ処理など
        """
        pass

if __name__ == '__main__':
    unittest.main()

# -*- conding: utf-8 -*-
u"""スクレイピング用のライブラリ
"""
# import time
import unittest
import re
# from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
# from selenium.common.exceptions import StaleElementReferenceException
# from selenium.common.exceptions import WebDriverException
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC


# My library
from logmessage import logprint
from scraping import Scraping
import imagefile


class Sanwachannel(Scraping):
    u"""サンワチャンネル用クラス
    """
    def get_page_information(self, xpath):
        u"""ページの情報を出力する。
        目的: 全xxxx件中xxx〜xxx件目を端末に表示する。
        """
        try:
            page_number = self.driver.find_element_by_xpath(
                xpath).text
        except NoSuchElementException:
            logprint(self.driver.find_element_by_xpath(
                "//body").get_attribute('outerHTML'))
            logprint('xpathが見つかりません。')
            logprint(xpath + ' が見つかりません。')
        else:
            logprint(page_number)

    def get_product_text(self, product_page, item_list):
        u"""商品個別のurlを受け取り、商品情報をリストにして返す
        引数:
            * url
            * path: 上位のページから遷移した場合にpathを引数として引き継ぐ。
                直接遷移した場合はpathを渡されない。
        """
        product_list = [''] * len(item_list)

        for item in item_list:
            try:
                product_list[item[0] - 1] = self.get_text_by_xpath(
                    product_page, item[2], item[1] + "はありません")
            except IndexError as error_code:
                print(error_code)
                print(item[0])

        return product_list

    @staticmethod
    def combine_text_by_br(dist_list):
        u"""<br>を区切り文字としてリストの内容を結合する。
        """
        # リストへの書き込み
        return_text = ''
        for content in dist_list:
            if not content.startswith("<a href"):
                if len(return_text) == 0:
                    return_text = bytes(content, "utf-8").decode("utf-8")
                else:
                    return_text += bytes(
                        ("<br>" + content), "utf-8").decode("utf-8")

        return return_text

    def make_fetr_row(self, fetr_object):
        """特長、仕様、適応機種のリストを返す
        """
        fetr_list = [''] * 33

        for fetr_index, fetr in enumerate(fetr_object):
            fetr_ttl = ''

            # //div[@class='fetr_area'][1]
            fetr_index_xpath = ("//div[@class='fetr_area']["
                                + str(fetr_index + 1) + "]")
            # //div[@class='fetr_area'][1]/p[1]
            fetr_ttl_xpath = fetr_index_xpath + "/p[1]"

            # //div[@class='fetr_area'][1]/p/a/img
            fetr_img_xpath1 = fetr_index_xpath + "/div/p/a/img"

            # //div[@class='fetr_area'][1]/p/a/img
            fetr_img_xpath2 = fetr_index_xpath + "/p/a/img"

            # 特長、仕様、対応機種を抜き出す。
            fetr_ttl = self.get_text_by_xpath(
                fetr,
                fetr_ttl_xpath)

            # //div[@class='fetr_area'][1]/p[@class='fetr_line']
            fetr_line_list = self.get_attribute_list_by_xpath(
                fetr,
                fetr_index_xpath + "/p[@class='fetr_line']",
                "innerHTML")

            # //div[@class='fetr_area'][1]/p[@class='fetr_img_right']
            fetr_img_right_list = self.get_attribute_list_by_xpath(
                fetr,
                fetr_index_xpath + "/div/p[@class='fetr_img_right']",
                "innerHTML")

            i = 0
            # 特長の処理
            if fetr_ttl == "特長":
                i = 0
            # 仕様の処理
            elif fetr_ttl == "仕様":
                i = 11
            # 対応機種の処理
            elif fetr_ttl == "対応機種":
                i = 22
            else:
                logprint('予期せぬエラーが発生しました。')
                logprint(fetr_ttl)

            # リストへの書き込み
            fetr_list[i] = self.combine_text_by_br(
                fetr_line_list + fetr_img_right_list)

            # イメージ名の書き込み
            image_attrs_list1 = self.get_attribute_list_by_xpath(
                fetr, fetr_img_xpath1, "src")
            image_attrs_list2 = self.get_attribute_list_by_xpath(
                fetr, fetr_img_xpath2, "src")

            i += 1
            for image_count, image_attrs in enumerate(
                    image_attrs_list1 + image_attrs_list2):
                image_name = re.search(r"[\da-zA-Z_-]+.(jpg|gif)", image_attrs)
                if image_name is not None:
                    image_name = image_name.group()
                    # 小文字に変換する。
                    image_name = image_name.lower()
                    image_name_list = image_name.split('_')
                    if len(image_name_list) != 0:
                        image_name_last = image_name_list[1]
                        image_name_last = image_name_last.replace('ft', '')
                        image_name_last = image_name_last.replace('sp', '2')
                        image_name = image_name_list[0] + '_' + image_name_last

                    fetr_list[i + image_count] = image_name
                    # imageをダウンロードして保存する。
                    imagefile.download_and_save_dir_direct(
                        image_attrs, 'sanwaimage', image_name)

        return fetr_list

    def make_image_row(self, driver, image_xpath):
        """イメージのリストを返す
        """
        image_list = [''] * 10

        image_attrs_list = self.get_attribute_list_by_xpath(
            driver, image_xpath, "src")

        for image_count, image_attrs in enumerate(image_attrs_list[:10]):
            image_name = re.search(r"[\da-zA-Z_-]+.(jpg|gif)", image_attrs)
            if image_name is not None:
                image_name = image_name.group()
                # 小文字に変換する。
                image_list[image_count] = [image_name, image_attrs]

        return image_list

    def get_product_fetr(self, product_page, fetr_xpath):
        u"""商品個別のurlを受け取り、商品情報をリストにして返す
        引数:
            * url
            * path: 上位のページから遷移した場合にpathを引数として引き継ぐ。
                直接遷移した場合はpathを渡されない。
        """
        try:
            fetr_object = self.get_list_by_xpath(product_page, fetr_xpath)

        except IndexError as error_code:
            print(error_code)
        else:
            if fetr_object is not None:
                fetr_list = self.make_fetr_row(fetr_object)

        return fetr_list

    def get_link_dist_info(self, driver, link_xpath):
        """カテゴリのリストを返す
        """
        return_list = [''] * 4

        url = self.get_attribute_by_xpath(driver, link_xpath, 'href')
        self.get_page(self.link_driver, url)

        return_list[0] = bytes("サンワチャンネル", "utf-8").decode("utf-8")

        path = self.get_text_by_xpath(
            self.link_driver, "//div[@id='topic-path']/p")
        path_list = path.split('>')
        for index, item in enumerate(path_list):
            path_list[index] = item.strip()

        if len(path_list) > 2:
            return_list[1] = bytes(path_list[2], "utf-8").decode("utf-8")

        if len(path_list) > 3:
            return_list[2] = bytes(
                (":").join(path_list[3:-1]), "utf-8").decode("utf-8")

        return_list[3] = self.get_text_by_xpath(
            self.link_driver, "//h1[@class='clfx_b']")

        return return_list


class FactorialTest(unittest.TestCase):
    u"""テスト用のクラス
    """
    def setUp(self):
        u"""セットアップ
        """
        self.get_items_list = [
            [1, "品名", "//div[@class='product_data_main']/p[@class='pname']"],
            [2, "製品品番",
             "//div[@class='p_line1 clfx']/p[@class='p_line_right pcode']"],
            [3, "JANコード",
             "//div[@class='p_line2 clfx']/p[@class='p_line_right']"],
            [4, "標準価格",
             "//div[@class='p_line3 clfx']/p[@class='p_line_right']"],
            [5, "仕切価格",
             "//div[@class='p_line2 tp_4 clfx']" +
             "/p[@class='p_line_right pprice']/span"]
        ]

        self.sanwachannel = Sanwachannel('https://cust.sanwa.co.jp/')

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

    # def test_get_next_link(self):
    #     u"""「次のページへ」というリンクをクリックする。
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     self.sanwachannel.get_page(self.sanwachannel.driver, url)

    #     login_div = "//div[@class='login_inaccount']"
    #     login_dict = {
    #         'login_id': "health-welfare@ghjapan.jp",
    #         'login_id_name': 'MailAddress',
    #         'password': "ghjapan006",
    #         'password_name': 'PassWord',
    #         'submit_path': login_div + "/p/a"
    #     }

    #     self.sanwachannel.execute_login(self.sanwachannel.driver, login_dict)

    #     self.sanwachannel.execute_link_click(
    #         self.sanwachannel.driver, "//li/p/a/img[@alt='在庫照会']")

    #     input_list = [
    #         ["sProductCode", '-'], ["sProductName", ''],
    #         ["sJanCode", ''], ["sInventory", ''],
    #         ["sRegularPrice_Under", ''], ["sRegularPrice_TOP", ''],
    #         ["InAbolish", ''], ["DispImg", '']
    #     ]

    #     submit_path = "//img[@alt='この条件で検索']"

    #     self.sanwachannel.execute_search(input_list, submit_path)

    #     self.sanwachannel.get_page_information("//p[@class='result_amount']")

    #     i = 0
    #     while self.sanwachannel.is_link_enable("次のページへ"):
    #         if i > 1:
    #             break
    #         self.sanwachannel.get_next_page("次のページへ")
    #         self.sanwachannel.get_page_information(
    #             "//p[@class='result_amount']")
    #         i += 1

    # def test_get_table(self):
    #     u"""「次のページへ」というリンクをクリックする。
    #     """
    #     url = 'https://cust.sanwa.co.jp/'
    #     self.sanwachannel.get_page(self.sanwachannel.driver, url)
    #     self.sanwachannel.get_page(self.sanwachannel.product_driver, url)

    #     login_div = "//div[@class='login_inaccount']"
    #     login_dict = {
    #         'login_id': "health-welfare@ghjapan.jp",
    #         'login_id_name': 'MailAddress',
    #         'password': "ghjapan006",
    #         'password_name': 'PassWord',
    #         'submit_path': login_div + "/p/a"
    #     }

    #     self.sanwachannel.execute_login(
    #         self.sanwachannel.driver, login_dict)
    #     self.sanwachannel.execute_login(
    #         self.sanwachannel.product_driver, login_dict)

    #     self.sanwachannel.execute_link_click(
    #         self.sanwachannel.driver, "//li/p/a/img[@alt='在庫照会']")

    #     input_list = [
    #         ["sProductCode", '-'], ["sProductName", ''],
    #         ["sJanCode", ''], ["sInventory", ''],
    #         ["sRegularPrice_Under", ''], ["sRegularPrice_TOP", ''],
    #         ["InAbolish", ''], ["DispImg", '']
    #     ]

    #     submit_path = "//img[@alt='この条件で検索']"

    #     self.sanwachannel.execute_search(input_list, submit_path)

    #     self.sanwachannel.get_page_information("//p[@class='result_amount']")
    #     rows = self.sanwachannel.get_table_row(
    #         "//table/tbody/tr")
    #     for row in rows:
    #         self.sanwachannel.get_product_url(row, '詳細を見る')

    #     i = 0
    #     while self.sanwachannel.is_link_enable("次のページへ"):
    #         if i > 1:
    #             break
    #         self.sanwachannel.get_next_page("次のページへ")

    #         self.sanwachannel.get_page_information(
    #             "//p[@class='result_amount']")
    #         rows = self.sanwachannel.get_table_row(
    #             "//table/tbody/tr")
    #         for row in rows:
    #             self.sanwachannel.get_product_url(row, '詳細を見る')

    #         i += 1

    # def test_get_product_info(self):
    #     u"""商品単体の取得のテスト エルゴノミクスリフトアップデスク
    #     """
    #     url = 'https://cust.sanwa.co.jp/products/detail.asp?code=MR-ERGST1'
    #     product_page = self.sanwachannel.get_product_driver(url)
    #     data = self.sanwachannel.get_product_text(
    #         product_page, self.get_items_list)
    #     self.assertEqual(data[0], "エルゴノミクスリフトアップデスク")
    #     self.assertEqual(data[1], "MR-ERGST1")
    #     self.assertEqual(data[2], "4969887158838")
    #     self.assertEqual(data[3], "￥43,800")
    #     self.assertEqual(data[4], "￥28,470")
    #     fetr_data = self.sanwachannel.get_product_fetr(
    #         product_page, "//div[@class='fetr_area']")
    #     self.assertTrue(fetr_data)

    #     link_dist_info = self.sanwachannel.get_link_dist_info(
    #         product_page, "//p[@class='sanwaweb_btn']/a")

    #     self.assertEqual(link_dist_info[0], 'サンワチャンネル')
    #     self.assertEqual(link_dist_info[1], 'デスク・ラック')
    #     self.assertEqual(link_dist_info[2], 'デスク:上下昇降デスク（スタンディングデスク）')
    #     self.assertEqual(link_dist_info[3], '座り作業、立ち作業の切り替えを容易に行い、疲労軽減。')

    # def test_get_product_info_4_M(self):
    #     u"""商品単体の取得のテスト 4-M
    #     """
    #     url = 'https://cust.sanwa.co.jp/products/detail.asp?code=4-M'
    #     product_page = self.sanwachannel.get_product_driver(url)
    #     data = self.sanwachannel.get_product_text(
    #         product_page, self.get_items_list)
    #     self.assertEqual(data[0], "EフィルターIV")
    #     self.assertEqual(data[1], "4-M")
    #     self.assertEqual(data[2], "")
    #     self.assertEqual(data[3], "￥0")
    #     self.assertEqual(data[4], "￥0")
    #     fetr_data = self.sanwachannel.get_product_fetr(
    #         product_page, "//div[@class='fetr_area']")
    #     print(fetr_data[0])
    #     print(fetr_data[1])

    # def test_get_product_info_blueyooth(self):
    #     u"""商品単体の取得のテスト
    #     """
    #     url = 'https://cust.sanwa.co.jp/products/detail.asp?code=1660KIT'
    #     product_page = self.sanwachannel.get_product_driver(url)
    #     data = self.sanwachannel.get_product_text(
    #         product_page, self.get_items_list)
    #     self.assertEqual(data[0], "Bluetoothバーコードスキャナ1660キット")
    #     self.assertEqual(data[1], "1660KIT")
    #     self.assertEqual(data[2], "")
    #     self.assertEqual(data[3], "オープン価格")
    #     self.assertEqual(data[4], "￥58,000")
    #     fetr_data = self.sanwachannel.get_product_fetr(
    #         product_page, "//div[@class='fetr_area']")

    #     self.assertEqual(len(fetr_data[22]), 106)
    #     self.assertEqual(len(fetr_data[23]), 0)
    #     link_dist_info = self.sanwachannel.get_link_dist_info(
    #         product_page, "//p[@class='sanwaweb_btn']/a")

    #     self.assertEqual(link_dist_info[0], 'サンワチャンネル')
    #     self.assertEqual(link_dist_info[1], '周辺機器')
    #     self.assertEqual(link_dist_info[2], 'その他:バーコードスキャナ')
    #     self.assertEqual(
    #         link_dist_info[3], '最も便利で、最も多才な、小型・軽量Bluetoothスキャナ。')

    def test_get_product_info_cai_cab(self):
        u"""商品単体の取得のテスト
        """
        url = 'https://cust.sanwa.co.jp/products/detail.asp?code=CAI-CAB32'
        product_page = self.sanwachannel.get_product_driver(url)
        data = self.sanwachannel.get_product_text(
            product_page, self.get_items_list)
        self.assertEqual(data[0], "iPad・タブレットトロリー（32台収納）")
        self.assertEqual(data[1], "CAI-CAB32")
        self.assertEqual(data[2], "4969887130490")
        self.assertEqual(data[3], "￥680,000")
        self.assertEqual(data[4], "￥408,000")
        fetr_data = self.sanwachannel.get_product_fetr(
            product_page, "//div[@class='fetr_area']")
        print(fetr_data)

        link_dist_info = self.sanwachannel.get_link_dist_info(
            product_page, "//p[@class='sanwaweb_btn']/a")

        self.assertEqual(link_dist_info[0], 'サンワチャンネル')
        self.assertEqual(link_dist_info[1], 'デスク・ラック')
        self.assertEqual(link_dist_info[2], '機器収納キャビネット:タブレット')
        self.assertEqual(
            link_dist_info[3],
            '複数台のiPad・タブレットを同時に保管、充電、同期できる。32台収納。iPad Pro収納可能、2.4A充電可能。')

    def tearDown(self):
        u"""クローズ処理など
        """
        pass

if __name__ == '__main__':
    unittest.main()

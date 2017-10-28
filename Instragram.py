import sqlite3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import sys

class Instagram:

    driver = webdriver.Chrome()
    conn = sqlite3.connect('following.db')

    login = None


    following = 0

    @staticmethod
    def delete_tys_word(word):
        if "тыс." in word:
                word = word.replace('тыс.', '00')
                if "," in word:
                    word = word.replace(',', '')

        elif "млн" in word:
            if "," in word:
                word = word.replace('млн', '00000')
                word = word.replace(',', '')
        else:
            word = word.replace("тыс.", "000")

        return word

    @classmethod
    def add_following_login_to_data_base(cls, login):

        cursor = cls.conn.cursor()
        cursor.execute("INSERT INTO logins VALUES(?)", [login])
        cls.conn.commit()

    @classmethod
    def get_logins_from_data_base(cls):

        all_logins = []
        cur = cls.conn.cursor()
        cur.execute("SELECT * FROM logins")

        rows = cur.fetchall()

        for row in rows:
            login = row[0].rstrip()
            all_logins.append(login)
        return all_logins

    @staticmethod
    def get_html(url):

        driver = webdriver.Chrome()
        driver.get(url)

        return driver.page_source

    @classmethod
    def get_user_followers_following_difference(cls):

        time.sleep(2)
        elements = cls.driver.find_elements_by_class_name("_t98z6")
        login = cls.driver.find_element_by_class_name("_ienqf").text.split("Подписаться")[0].replace(' ', '')

        followers = int(cls.delete_tys_word(elements[1].text.split("подписчиков")[0]).replace(' ', ''))
        following = int(cls.delete_tys_word(elements[2].text.split("Подписки:")[1]).replace(' ', ''))

        return cls.process_account_data(login, following, followers)

    @staticmethod
    def process_account_data(login, following, followers):
        if following > followers:
            Instagram.add_following_login_to_data_base(login)
            return True
        return False

    @classmethod
    def start_login_process(cls, login, password):

        cls.driver.get("https://www.instagram.com/accounts/login/")

        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._qv64e._gexxb._4tgw8._njrw0"))
        cls.wait(element_present)

        cls.login = login
        cls.password = password

        username_input = cls.driver.find_element_by_xpath('//*[@name="username"]')
        password_input = cls.driver.find_element_by_xpath('//*[@name="password"]')
        enter_button = cls.driver.find_element_by_xpath('//*[@class="_qv64e _gexxb _4tgw8 _njrw0"]')

        username_input.send_keys(login)
        password_input.send_keys(password)

        enter_button.click()

        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._avvq0._o716c"))
        cls.wait(element_present)

    @classmethod
    def delete_following(cls):

        accounts_to_delete = cls.get_logins_from_data_base()
        time.sleep(3)
        cls.driver.get("https://www.instagram.com/" + cls.login + "/following/")
        element_present = EC.presence_of_element_located((By.CLASS_NAME, "_t98z6"))
        cls.wait(element_present)
        cls.driver.find_elements_by_class_name("_t98z6")[2].click()

        time.sleep(2)
        for i in range(10):
            all_followings = cls.driver.find_elements_by_css_selector("._pg23k._9irns._gvoze")
            all_followings[i].click()
            time.sleep(1)
            login = cls.driver.find_element_by_class_name("_ienqf").text.split("Подписки")[0].replace(' ', '').rstrip()

            if login in accounts_to_delete:
                cls.follow_unfollow_user(follow=False)
                # accounts_to_delete.remove(login)


            cls.driver.back()

        cls.driver.get("https://www.instagram.com/")





    @classmethod
    def search_hashtag(cls, driver, word):

        driver.get("https://www.instagram.com/")
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._avvq0._o716c"))
        cls.wait(element_present)

        search = driver.find_element_by_xpath('//*[@class="_avvq0 _o716c"]')
        search.clear()
        search.send_keys(word)

        time.sleep(1.5)

        search.send_keys(Keys.ENTER)
        search.send_keys(Keys.ENTER)

        return driver

    @staticmethod
    def wait(element_present):
        try:
            WebDriverWait(Instagram.driver, 10).until(element_present)
        except TimeoutException:
            pass

    @classmethod
    def get_first_page(cls, driver):

        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._mck9w._gvoze._f2mse"))
        cls.wait(element_present)

        driver.find_element_by_xpath('//*[@class="_mck9w _gvoze _f2mse"]').click()
        return driver

    @classmethod
    def set_up_amount_following(cls):
        cls.following = 0


    @classmethod
    def follow_unfollow_user(cls, follow=True):

            element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._lyv4q._ov9ai"))
            cls.wait(element_present)

            button_follow = cls.driver.find_element_by_css_selector("._lyv4q._ov9ai")

            if follow:
                if button_follow.text == "Подписаться":
                    button_follow.click()
                    time.sleep(1)
                    return True

            if not follow:
                button_follow.click()
                time.sleep(1)
                return True
            return False




    @classmethod
    def start_searching_by_hashtag(cls, hash_tag):

        cls.driver.get("https://www.instagram.com/")
        while cls.following < 55:
            driver = cls.search_hashtag(cls.driver, hash_tag)
            driver = cls.get_first_page(driver)
            cls.skip_first_pages()
            cls.start_following(driver)


    @classmethod
    def skip_first_pages(cls):

        for i in range(8):
            try:
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._pfyik._lz8g1"))
                cls.wait(element_present)

                next_button = cls.driver.find_element_by_link_text('Далее')
                time.sleep(1)
                next_button.click()

            except:
                print("no found")
                cls.driver.back()

    @classmethod
    def start_following_accounts_of_another_account(cls):

        cls.driver.get("https://www.instagram.com/xvoodookittenx/")
        time.sleep(3)

        cls.driver.find_elements_by_class_name("_t98z6")[1].click()

        time.sleep(3)


        for i in range(1,10):

            all_followings = cls.driver.find_elements_by_css_selector("._pg23k._9irns._gvoze")
            time.sleep(2)
            all_followings[i].click()
            time.sleep(2)
            cls.follow_unfollow_user()
            cls.driver.back()

    @classmethod
    def start_following(cls, driver):

        while cls.following < 55:

            try:
                element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "._pfyik._lz8g1"))
                cls.wait(element_present)

                next_button = driver.find_element_by_link_text('Далее')
                next_button.click()

                element_present = EC.presence_of_element_located((By.CLASS_NAME, "_o0j5z"))
                cls.wait(element_present)

                button_to_open_account = driver.find_element_by_class_name("_rewi8")
                button_to_open_account.click()

                if cls.get_user_followers_following_difference():
                    cls.follow_unfollow_user()
                    print("\a")
                    cls.following += 1

                time.sleep(2)
                print("followed " + str(cls.following))

                driver.back()
                print("returned")

            except:

                print("error")
                time.sleep(3)

                break












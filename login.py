# F:\chromedriver-win64\chromedriver.exe
import csv
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from configparser import ConfigParser


def login_qq():
    config = ConfigParser()
    config.read("config.ini")

    username = config.get("QQ", "username")
    password = config.get("QQ", "password")

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome("F:\chromedriver-win64\chromedriver.exe", options=options)

    driver.get("https://qzone.qq.com/")

    driver.switch_to.frame("login_frame")

    username_input = driver.find_element_by_id("u")
    username_input.clear()
    username_input.send_keys(username)

    password_input = driver.find_element_by_id("p")
    password_input.clear()
    password_input.send_keys(password)

    login_button = driver.find_element_by_id("login_button")
    login_button.click()

    time.sleep(2)

    if driver.current_url == "https://user.qzone.qq.com/{}?g_f=".format(username):
        print("登录成功")
    else:
        print("登录失败")

    return driver


def get_friend_list(driver):
    driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@id, 'app_canvas_frame')]"))
    time.sleep(2)

    friend_list = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    friends = soup.find_all('li', class_='user-info')
    for friend in friends:
        friend_name = friend.find('span', class_='nickname').text
        friend_list.append(friend_name)

    return friend_list


def get_friends_friends(driver, query_friend):
    driver.switch_to.default_content()
    driver.find_element_by_name('w').send_keys(query_friend)
    driver.find_element_by_name('searchbutton').click()
    time.sleep(3)

    friends_friends_list = []
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    friends = soup.find_all('li', class_='user-info')
    for friend in friends:
        friend_name = friend.find('span', class_='nick').text
        friends_friends_list.append(friend_name)

    return friends_friends_list


def crawl_qq_friends(qq):
    driver = login_qq()
    friend_list = get_friend_list(driver)

    csv_rows = [['Level 1', 'Level 2']]

    for friend in friend_list:
        friends_friends_list = get_friends_friends(driver, friend)
        for friends_friend in friends_friends_list:
            csv_rows.append([friend, friends_friend])

    driver.quit()

    with open('qq_friends.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(csv_rows)


crawl_qq_friends('3575197386')

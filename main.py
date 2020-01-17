import time
import base64
import os
import requests
from threading import Thread
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.firefox.options import Options
from seleniumwire import webdriver
import traceback


def get_driver(proxy_list):
    options1 = Options()
    options1.headless = True
    # port must be str
    options = {
        'proxy': {
            'http': 'http://' + proxy_list[2] + ':' + proxy_list[3] + '@' + proxy_list[0] + ':' + proxy_list[1],
            'https': 'https://' + proxy_list[2] + ':' + proxy_list[3] + '@' + proxy_list[0] + ':' + proxy_list[1]
        }
    }
    driver = webdriver.Firefox(seleniumwire_options=options, options=options1)
    return driver


def start_bot(proxy_list):
    driver = None
    try:
        driver = get_driver(proxy_list)
        driver.get("http://dwl.by/php/pl/h_captcha.html")
        iframes = driver.find_elements_by_tag_name("iframe")
        driver.switch_to.frame(iframes[0])
        wait(driver, 20).until(EC.presence_of_element_located((By.ID, "checkbox")))
        time.sleep(2)
        elem = driver.find_element_by_xpath("//*[@id='checkbox']")
        elem.click()
        elem.click()
        driver.switch_to.default_content()
        driver.switch_to.frame(iframes[1])
        wait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
        coor = None
        for i in range(0, 5):
            time.sleep(2)
            elem = driver.find_element_by_tag_name("canvas")
            size = get_size(driver)
            coor = get_coor(size)
            if coor is None:
                elem = driver.find_element_by_class_name("submit-background")
                elem.click()
            else:
                break

        if coor is None:
            raise Exception("Не найдены нужные координаты")
        solve_captch(driver, elem, coor)
        elem = driver.find_element_by_class_name("submit-background")
        elem.click()
        time.sleep(1)
        elem = driver.find_element_by_name("g-recaptcha-response")
        key = elem.get_attribute("value")
        answer(key)
    except:
        traceback.print_exc()
    finally:
        if driver is not None:
            driver.close()


def get_size(driver):
    canvas = driver.execute_script("return document.getElementsByTagName('canvas')[0]")
    img_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
    canvas_png = base64.b64decode(img_base64)
    with open(r"temp/temp.png", 'wb') as f:
        f.write(canvas_png)
    size_of_img = os.path.getsize("temp/{0}.png".format(Thread.name))
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp/temp.png')
    os.remove(path)
    return size_of_img


def get_coor(size):
    global main_coordinates
    size = str(size)
    coors = None
    for item in main_coordinates:
        if item[0] == size:
            coors = item
            break
    return coors[1]


def solve_captch(driver, elem, coor):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element_with_offset(elem, coor[0], coor[1]).perform()
    time.sleep(1)
    actions.click().perform()

    actions = webdriver.ActionChains(driver)
    actions.move_to_element_with_offset(elem, coor[2], coor[3]).perform()
    time.sleep(1)
    actions.click().perform()

    actions = webdriver.ActionChains(driver)
    actions.move_to_element_with_offset(elem, coor[4], coor[5]).perform()
    time.sleep(1)
    actions.click().perform()

    actions = webdriver.ActionChains(driver)
    actions.move_to_element_with_offset(elem, coor[6], coor[7]).perform()
    time.sleep(1)
    actions.click().perform()


def pars_str(str):
    list = str.split("|")
    size = list[0]
    coor = []
    for i in list[1:]:
        temp = i.split(",")
        coor.append(int(temp[0]))
        coor.append(int(temp[1]))
    return size, coor


def prepare(*proxy_list):
    i = 0
    while True:
        if i == len(proxy_list):
            i = 0
        start_bot(proxy_list[i])
        i += 1


def pars_file_coors():
    with open("coors.txt", 'r') as f:
        lines = f.readlines()
    new_lines = []
    for line in lines:
        new_lines.append(pars_str(line))
    return new_lines


def make_proxy_lists(count_of_threads):
    with open("proxies.txt", 'r') as f:
        lines = f.readlines()
    temp = lines[0].split(':')
    login = temp[0]
    password = temp[1].rstrip()
    proxies = []
    for line in lines[2:]:
        temp = line.split(':')
        proxies.append((temp[0], temp[1].rstrip(), login, password))
    counter = len(proxies) // count_of_threads
    new_proxies = []
    temp = 0
    for i in range(0, count_of_threads):
        new_proxies.append([])
        for j in range(0, counter):
            new_proxies[i].append(proxies[temp])
            temp += 1
    return new_proxies


def answer(captcha_key):
    requests.get("http://dwl.by/php/pl/konsulat/manage_EK_ReCaptcha_v2_and_v3.php?key_prog=4562&g_recaptcha_response="
                 + captcha_key + "&time_ban=100&id=add_PL_EK_ReCaptcha_v2")


def start():
    global count_of_threads
    threads = []
    proxy_list = make_proxy_lists(count_of_threads)
    for i in range(0, count_of_threads):
        new_thread = Thread(target=prepare, args=(proxy_list[i]))
        threads.append(new_thread)
        new_thread.start()


if __name__ == '__main__':
    print("start")
    main_coordinates = pars_file_coors()
    count_of_threads = 1
    start()

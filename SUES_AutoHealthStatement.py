# -*- coding:utf-8 -*-
# @Time : 2022/12/13 上午 9:41
# @Author : Dedicatus1979
# @File : SUES_AutoHealthStatement.py
# @Software : PyCharm

from io import BytesIO
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup
from playwright.sync_api import Playwright, sync_playwright, expect
import re
import time
import json
import datetime
import random
import base64
import cv2
import httpx
import numpy as np


curFileDir = Path(__file__).parent  # 当前文件路径

try:
    with open(curFileDir / "config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except:
    print("载入配置文件出错")
    exit(0)

url = config["system_configs"]["url"]


def captcha_identify(value):
    """用于识别验证码"""
    im = Image.open(BytesIO(value))  # 将bytes数据转为图片
    im = im.resize((60, 20))
    pix = im.load()
    numbers = [
        "111000000011111110000000000011111001111111001111001111111110011100111111111001110011111111100111100111111100111110000000000011111110000000111111",
        "111111111111111110011111111001111001111111100111000111111110011100000000000001110000000000000111111111111110011111111111111001111111111111100111",
        "100111111100011100111111100001110011111100100111001111100110011100111100111001110011100111100111100000111110011111000111111001111111111111111111",
        "100111111100111100111001111001110011100111100111001110011110011100111001111001110011000011000111100001000000111110001110000111111111111111111111",
        "111111110011111111111100001111111111000000111111111000110011111110001111001111110000000000000111000000000000011111111111001111111111111100111111",
        "000000011100111100000001111001110011100111100111001110011110011100111001111001110011110011000111001111000000111100111110000111111111111111111111",
        "111100000011111111000000000011111000110011001111001110011110011100111001111001110011100111100111001110001100011110011100000011111111111000011111",
        "111111111111111100111111111111110011111111100111001111111000011100111110000111110011100011111111001100111111111100000111111111110001111111111111",
        "111111110001111110000110000011110000000011000111001100011110011100111001111001110011100011100111000000001100011110001110000011111111111100011111",
        "110000111111111110000001110011110001100011100111001111001110011100111100111001110011110011100111100110011000111110000000000111111110000001111111"
    ]  # 数字 0-9 对应二值化编码, 这个是将数字二值化为144位长的字符串
    captcha = ""
    num = 0
    while num < 4:  # 这个大while是用来计算二值化后的图片的
        i = 13 * num + 7
        ldString = ""
        # 获取图片中所有数字的二值化编码
        while i < 13 * num + 7 + 9:
            j = 3
            while j < 19:
                pixel = pix[i, j]
                ldString = ldString + str((+(pixel[0] * 0.3 + pixel[1] * 0.59 + pixel[2] * 0.11 >= 128)))
                j += 1
            i += 1
        comLen = []
        # 获取编码对应数字
        for i in range(len(numbers)):
            temp = 0
            for j in range(len(numbers[i])):
                if numbers[i][j] == ldString[j]:
                    temp += 1
            comLen.append(temp)
        captcha += str(comLen.index(max(comLen)))
        num += 1
    # print("二值化识别验证码" + captcha)
    return captcha


def get_offset(backgroundImage, sliderImage):
    """用于获取滑动验证码的滑动距离"""
    bg = np.frombuffer(backgroundImage, dtype=np.uint8)
    tp = np.frombuffer(sliderImage, dtype=np.uint8)

    # 读取背景图片和缺口图片
    bg_img = cv2.imdecode(bg, flags=1)  # 背景图片
    tp_img = cv2.imdecode(tp, flags=1)  # 缺口图片

    # 识别图片边缘
    bg_edge = cv2.Canny(bg_img, 100, 200)
    tp_edge = cv2.Canny(tp_img, 100, 200)

    # 转换图片格式
    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

    # 缺口匹配
    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配

    return max_loc[0]


def offset_change(offset):
    """用于将滑动距离偏移一定距离"""
    if offset > 350:
        return offset * 1.01
    elif offset > 270:
        return offset * 1.06
    elif offset > 220:
        return offset * 1.052
    elif offset > 180:
        return offset * 1.05
    elif offset > 120:
        return offset * 1.052
    elif offset > 100:
        return offset * 1.05
    elif offset > 60:
        return offset * 1.043
    else:
        return offset * 1.025


def push_wechat(param):
    """用于微信推送用"""
    try:
        if config['system_configs']['SendKey']:
            scurl = f"https://sctapi.ftqq.com/{config['system_configs']['SendKey']}.send"
            httpx.post(scurl, params=param)
    except:
        pass


def get_captcha_ending(html_text):
    """用于获取滑动验证码的base64码以及获取最终的结果"""
    soup = BeautifulSoup(html_text, "html.parser")
    temp_1 = soup.find_all('div', {'class': 'ap-slider'})
    temp_2 = soup.find_all('div', {'class': 'layui-layer-content layui-layer-padding'})
    if temp_1:
        image_base64 = re.findall(r'src=".*?"', str(temp_1[0]))
        bg_base64 = image_base64[0].split(",")[-1]
        img_base64 = image_base64[1].split(",")[-1]
        ending = ""
    else:
        ending = re.findall(r"</i>.*?</div>", str(temp_2[0]))
        bg_base64 = ""
        img_base64 = ""
    return bg_base64, img_base64, ending


def run(playwright: Playwright, username, password, **kwargs) -> None:
    """主要实现打卡过程的部分"""
    dicts = kwargs
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    page.get_by_placeholder("账号 Username").fill(username)
    page.get_by_placeholder("密码 Password").fill(password)
    # str_captcha = captcha_identify(page.locator('//img[@class="codeImg fill_form_other"]').screenshot())
    # page.get_by_placeholder("验证码 Verification Code").fill(str_captcha)

    page.get_by_role("button", name="登 录").click()

    time.sleep(2)

    html = page.content()

    def mouse_move(offset_):
        """鼠标移动的子程序"""
        s = page.wait_for_selector('//div[@class="ap-bar-ctr"]', strict=True)
        box = s.bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()
        time.sleep(0.2)
        page.mouse.move(box["x"] + box["width"] / 2 + offset_, box["y"] + box["height"] / 2, steps=10)
        time.sleep(0.1)
        page.mouse.up()
        time.sleep(2)

    for i in range(5):
        bg_base64, img_base64 = get_captcha_ending(html)[:2]

        backgroundImage = base64.b64decode(bg_base64)
        sliderImage = base64.b64decode(img_base64)
        offset = offset_change(get_offset(backgroundImage, sliderImage)) * 0.75

        mouse_move(offset)

        time.sleep(1)

        html = page.content()
        try:
            temp = get_captcha_ending(html)
        except :
            temp = ''

        if temp == '':
            break
        if i == 4:
            context.close()
            browser.close()
            raise Exception("Captcha Error.")
        else:
            print(f"{username} 本次验证码未验证通过,正在尝试第{i+1}次验证.")
    # ---------------------

    time.sleep(1)

    if page.title() != "健康信息填报":
        raise Exception("Url or Time Error.")

    # --------以上是登录部分

    if dicts["in_school"]:
        # --------在校模式
        # page.locator("label").filter(has_text="是").get_by_role("insertion").click()
        page.locator("//*[@id='form']/div[10]/div/div/div[2]/div/div/label[1]").click()     # xpath定位，可直接f12右键
        page.locator("label").filter(has_text="松江校区").get_by_role("insertion").click()
        # page.locator("label").filter(has_text="健康").get_by_role("insertion").click()
        page.get_by_role("textbox", name="请填写宿舍楼").fill(dicts["building"])
        page.get_by_role("textbox", name="请填写寝室").fill(dicts["room"])

    else:
        # --------在家模式      # 无法修改地址...以后再改吧...
        # page.locator("label").filter(has_text="否").get_by_role("insertion").click()
        # page.get_by_text("否").nth(1).click()
        # page.locator(".hover > .iradio_square-green > .iCheck-helper").click()

        # a = page.locator("label").filter(has_text="否")
        # a.check()
        # print(type(a))
        # a.get_by_role("insertion").click()

        # page.get_by_text("否").nth(1).click()
        # page.locator(".hover > .iradio_square-green > .iCheck-helper").click()
        # page.locator(":nth-match(:text('否'), 2)").click()
        # page.locator("button >> visible=true").click()

        page.locator("//*[@id='form']/div[10]/div/div/div[2]/div/div/label[2]").click()     # xpath定位，可直接f12右键

        # page.locator("label").filter(has_text="无风险地区").get_by_role("insertion").click()
        # page.get_by_text("无风险地区").click()

        # page.locator("label").filter(has_text="健康").click()


    if dicts["is_positive"]:
        page.locator("label").filter(has_text="身体异样").get_by_role("insertion").click()
        page.locator("label").filter(has_text="发热").get_by_role("insertion").click()
    else:
        if dicts["is_negative"]:
            page.locator("label").filter(has_text="未感染").get_by_role("insertion").click()
        else:
            page.locator("label").filter(has_text="已康复").get_by_role("insertion").click()

    page.get_by_role("button", name="提交").click()

    # time.sleep(60)
    time.sleep(2)

    # def mouse_move(offset_):
    #     """鼠标移动的子程序"""
    #     s = page.wait_for_selector('//div[@class="ap-bar-ctr"]', strict=True)
    #     box = s.bounding_box()
    #     page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    #     page.mouse.down()
    #     time.sleep(0.2)
    #     page.mouse.move(box["x"] + box["width"] / 2 + offset_, box["y"] + box["height"] / 2, steps=10)
    #     time.sleep(0.1)
    #     page.mouse.up()
    #     time.sleep(2)
    #
    # # 获取验证码以及完成验证操作部分
    # html = page.content()
    # for i in range(5):
    #     bg_base64, img_base64 = get_captcha_ending(html)[:2]
    #
    #     backgroundImage = base64.b64decode(bg_base64)
    #     sliderImage = base64.b64decode(img_base64)
    #     offset = offset_change(get_offset(backgroundImage, sliderImage))
    #
    #     mouse_move(offset)
    #
    #     html = page.content()
    #     temp = get_captcha_ending(html)
    #     if temp[2]:
    #         break
    #     elif i == 4:
    #         context.close()
    #         browser.close()
    #         raise Exception("Captcha Error.")
    #     else:
    #         print(f"{username} 本次验证码未验证通过,正在尝试第{i+1}次验证.")
    # # ---------------------
    context.close()
    browser.close()


if __name__ == '__main__':
    need_time = config["system_configs"]["time_of_clock_in"].split(":")
    timestamp = 3600 * int(need_time[0]) + 60 * int(need_time[1])
    start_time = time.time()
    start_day = start_time - (start_time+28800) % 86400
    times = 0
    success = 0
    error = 0
    error_dict = {"mumber": [],
                  "cause": []}

    while True:
        if (time.time() + 28800) % 86400 > timestamp and \
                (time.time() - start_day) // 86400 >= times:
            now_time = datetime.datetime.now()
            print(now_time.strftime("%Y-%m-%d %H:%M:%S"))
            print(f"当前是本程序第{times + 1}次运行.")
            for i in range(len(config["user_configs"])):
                users = config["user_configs"][i]
                for j in range(3):
                    try:
                        with sync_playwright() as playwright:
                            run(playwright, users["id"], users["password"], in_school=users["in_school"],
                                is_positive=users["is_positive"], is_negative=users["is_negative"],
                                building=users["building"], room=users["room"])


                    except Exception as Error:
                        now_time = datetime.datetime.now()
                        print(now_time.strftime("%Y-%m-%d %H:%M:%S"))
                        print(f"{users['id']} 本次打卡程序发生了错误,错误类型为'{Error}',即将重新打卡,本次为第{j+1}尝试")
                        if j == 2:
                            error += 1
                            print(f"{users['id']} 本次打卡程序发生了'{Error}'错误,错误类型已保存,请自行打卡.")
                            error_dict["mumber"].append(users['id'])
                            error_dict["cause"].append(Error)
                        time.sleep(random.random()*10)
                    else:
                        now_time = datetime.datetime.now()
                        print(now_time.strftime("%Y-%m-%d %H:%M:%S"))
                        print(f"{users['id']} 本日打卡已完成.")
                        success += 1
                        time.sleep(random.random() * 10)
                        break
            print(f"--本日打卡已全部完成--本日打卡人数共{len(config['user_configs'])}人,{success}人打卡成功,{error}人打卡失败--")
            param = {
                'title': f'{now_time.strftime("%Y-%m-%d %H:%M:%S")} 本日健康填报信息推送',  # 推送标题
                'desp': f"""本日打卡人数共{len(config["user_configs"])}人,{success}人打卡成功,{error}人打卡失败,

{error_dict}"""  # 推送内容
            }
            push_wechat(param)
            success, error = 0, 0
            error_dict["mumber"].clear()
            error_dict["cause"].clear()
            times += 1
        else:
            time.sleep(300)


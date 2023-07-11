import pyautogui
import tkinter as tk
import pygetwindow as gw
import threading
import time
import pytesseract
import json
import queue
from chatgpt_web import TranslationEngine
from PIL import Image


from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

import win32gui
import win32con



def start_recognition(lang):
    # 开始文字识别和翻译
    global should_stop
    should_stop = False
    process_image(lang)


def stop_recognition():
    # 停止文字识别和翻译
    global should_stop
    should_stop = True



engine = TranslationEngine()

def translate_gpt(text):
    translation = engine.translate(text)
    return translation


def tencentcloud(text):
    target_text = None
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential("你的SecretId", "你的SecretKey")
        # 实例化一个http选项，可选的，没有特殊需求可以跳过
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        # 实例化一个client选项，可选的，没有特殊需求可以跳过
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        # 实例化要请求产品的client对象,clientProfile是可选的
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile)

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.TextTranslateRequest()

        params = {
            "SourceText": text,
            "Source": "auto",
            "Target": "zh",
            "ProjectId": 0
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个TextTranslateResponse的实例，与请求对象对应
        resp = client.TextTranslate(req)
        resp_string = resp.to_json_string()
        # 输出json格式的字符串回包
        # print(resp_string)
        parsed_resp = json.loads(resp_string)
        target_text = parsed_resp.get("TargetText")
        # print(target_text)

    except TencentCloudSDKException as err:
        print(err)
    return target_text


def process_image(lang,translate):
    global should_stop
    global image_processing_thread

    window = pyautogui.getWindowsWithTitle("Selector Window")[0]
    previous_text = ""

    while not should_stop:
        x, y, width, height = window.left, window.top, window.width, window.height
        screenshot = pyautogui.screenshot(region=(x+7, y+46, width-14, height-52))
        # screenshot.save('screenshot.png')
        grayscale_image = screenshot.convert('L')

        pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract'
        extracted_text = pytesseract.image_to_string(grayscale_image, lang=lang)
        text_with_quotes = f'"{extracted_text}"'

        if text_with_quotes != previous_text:
            previous_text = text_with_quotes
            if translate == "tencentcloud":
                translation_text = tencentcloud(text_with_quotes)
                translation_queue.put((extracted_text, translation_text))
            else:
                translation_text = translate_gpt(text_with_quotes)
                translation_queue.put((extracted_text, translation_text))

def get_translator():
    window = tk.Tk()
    window.title("Selector Window")
    window.geometry("800x300")
    window.attributes('-alpha', 0.3)

    # 创建菜单栏
    menubar = tk.Menu(window)
    window.config(menu=menubar)

    # 创建状态栏菜单
    status_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="状态", menu=status_menu)

    # 创建语言选择子菜单
    language_menu = tk.Menu(status_menu, tearoff=0)
    status_menu.add_cascade(label="语言选择", menu=language_menu)

    # 创建途径选择子菜单
    translate_menu = tk.Menu(status_menu, tearoff=0)
    status_menu.add_cascade(label="途径选择", menu=translate_menu)

    # 添加途径选项到语言选择子菜单
    translate_var = tk.StringVar(window)
    translate_var.set("eng")
    translate_choices = ["tencentcloud", "chatgpt"]
    for translate in translate_choices:
        translate_menu.add_radiobutton(label=translate, variable=translate_var, value=translate)

    # 添加语言选项到语言选择子菜单
    language_var = tk.StringVar(window)
    language_var.set("eng")
    language_choices = ["eng", "jpn"]
    for lang in language_choices:
        language_menu.add_radiobutton(label=lang, variable=language_var, value=lang)

    # 添加开始和停止命令到状态栏菜单
    status_menu.add_command(label="开始", command=lambda: start_translation(language_var.get(),translate_var.get()))
    status_menu.add_command(label="停止", command=stop_translation)

    # 其他代码...
    # 运行窗口的主循环
    window.mainloop()

def start_translation(lang,translate):
    global should_stop
    global image_processing_thread
    should_stop = False
    image_processing_thread = threading.Thread(target=process_image, args=(lang,translate))
    image_processing_thread.start()

def stop_translation():
    global should_stop
    should_stop = True

def update_translation():
    window = tk.Tk()
    window.title("Translation Window")
    window.geometry("800x300")
    # 设置窗口透明度
    window.attributes("-alpha", 0.5)

    # 创建一个标签用于显示翻译结果
    label = tk.Label(window, text="", wraplength=750, justify="left")
    label.pack()

    while True:
        if not translation_queue.empty():
            extracted_text, translation_text = translation_queue.get()
            label.config(text=f"原文本：{extracted_text}\n翻译结果：{translation_text}")



        window.update()

if __name__ == "__main__":
    translation_queue = queue.Queue()
    selector_thread = threading.Thread(target=get_translator)
    selector_thread.start()

    print("创建 Selector Window")
    time.sleep(2)  # 等待 5 秒钟，以便您有足够的时间查看窗口是否正确显示

    # 设置 Selector Window 窗口置顶
    selector_window = gw.getWindowsWithTitle("Selector Window")[0]
    selector_window.activate()
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)


    translation_thread = threading.Thread(target=update_translation)
    translation_thread.start()

    print("创建 Translation Window")
    time.sleep(2)  # 等待 5 秒钟，以便您有足够的时间查看窗口是否正确显示

    # 设置 Selector Window 窗口置顶
    selector_window = gw.getWindowsWithTitle("Translation Window")[0]
    selector_window.activate()
    hwnd = win32gui.GetForegroundWindow()
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    selector_thread.join()
    stop_translation()
    image_processing_thread.join()
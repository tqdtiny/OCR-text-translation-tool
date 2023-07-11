import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class TranslationEngine:
    def __init__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--headless")  # 设置 Chrome 为无界面模式
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--profile-directory=Default")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-service-autorun')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--password-store=basic')
        chrome_options.add_argument('--no-sandbox')

        self.driver = uc.Chrome(options=chrome_options, executable_path='chromedriver')

        # Check if the driver is already logged in
        driver_cookies = self.driver.get_cookies()
        if len(driver_cookies) == 0:
            self.login()
        else:
            # Set the cookies to maintain the session
            for cookie in driver_cookies:
                self.driver.add_cookie(cookie)

    def login(self):
        print("正在登录chatgpt")
        self.driver.get("https://chat.openai.com")
        # Login process code...
        time.sleep(2)
        inputTag = self.driver.find_element(By.XPATH, value="//*[@id='__next']/div[1]/div[1]/div[4]/button[1]")
        inputTag.click()
        time.sleep(5)
        login = self.driver.find_element(By.CSS_SELECTOR, "input.input.c3c2b240e.cd3adfc2e")
        login.send_keys("你的账号")
        login.send_keys(Keys.ENTER)
        time.sleep(5)
        password = self.driver.find_element(By.CSS_SELECTOR, "input.input.c3c2b240e.c17a8e7e0")
        password.send_keys("你的密码")
        password.send_keys(Keys.ENTER)
        time.sleep(10)
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ENTER).perform()
        actions.send_keys(Keys.ENTER).perform()
        time.sleep(5)
        nextt = self.driver.find_element(By.CSS_SELECTOR, "button.btn.relative.btn-neutral.ml-auto")
        nextt.send_keys(Keys.ENTER)
        time.sleep(3)
        nexttt = self.driver.find_element(By.CSS_SELECTOR, "button.btn.relative.btn-primary.ml-auto")
        nexttt.send_keys(Keys.ENTER)
        time.sleep(5)
        keyword = "翻译请求完成"
        element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{keyword}')]")
        self.click_element_and_continue(element)
        print("登录完成")

    def click_element_and_continue(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click().perform()
        time.sleep(3)

    def chatgpt_translate(self, text):
        print("正在请求翻译")
        input_text = self.driver.find_element(By.XPATH, value="//*[@id='prompt-textarea']")
        input_text.send_keys(f"请将下段文字翻译成中文：{text}")
        input_text.send_keys(Keys.ENTER)
        time.sleep(4)
        elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'markdown prose w-full break-words dark:prose-invert light')]")
        result = elements[-1].text
        return result

    def translate(self, text):
        translation_result = self.chatgpt_translate(text)
        print(translation_result)
        return translation_result

    def quit(self):
        self.driver.quit()

if __name__ == "__main__":
    engine = TranslationEngine()
    engine.translate("hello")
    engine.translate("hi")
    # engine.quit()

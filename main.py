import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
#命令行输入 pip install 包名

login_url = 'https://kktix.com/users/sign_in?back_to=https%3A%2F%2Fkktix.com%2F'
# 登录网址

# goal_url = 'https://kktix.com/events/shining03/registrations/new'
goal_url = 'https://kktix.com/events/wellsaid2025/registrations/new'
# 抢票网址,得有new

goal_index = 1
# 第几个票项
begin_time = '2025-01-01 00:00:00'
# 抢票开始时间,格式得是%Y-%m-%d %H:%M:%S
votes = 1
# 要几个票


email = '3029946904@qq.com'
# 邮箱
password = '12345678gu'
# 密码

name = '骨幹也'
# 联系人名字
phone = '18126106878'
# 手机号码

driver_path = r"F:\Develop\Chrome\chromedriver.exe"
# 先试试 driver = webdriver.Chrome()会不会报错
# 如果会报错,就把和.py文件一起发过去的三个文件存到一个文件夹,然后这里填chromedriver.exe的路径(路径最好不要有中文)

PAGE_TIMEOUT = 100  # 页面加载超时时间
TICKET_TIMEOUT = 40 # 不跳转到下个页面超时时间
# 当页面加载超时或不跳转到下个页面超时，会重新刷新当前页面和执行
# 不跳转下个页面: 比如你选好票点提交,一直不给你弹出填个人信息的页面



def find_event(driver, goal_index):

    driver.get(goal_url)
    elements = WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'ticket-quantity ng')]"))
    )
    goal_element = elements[goal_index - 1]
    return goal_element


def login(driver, email, password):

    driver.get(login_url)
    WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_element_located((By.ID, 'user_login'))
    ).send_keys(email)
    driver.find_element(By.ID, 'user_password').send_keys(password)
    driver.find_element(By.NAME, 'commit').click()


def fill_blank(driver, name, phone):

    inputs = WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.controls input[type='text']"))
    )

    name_blank = inputs[0]
    phone_blank = inputs[2]

    driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
        name_blank, name
    )

    driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
        phone_blank, phone
    )

    confirm_btn = WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.element_to_be_clickable((By.LINK_TEXT, '確認表單資料'))
    )
    driver.execute_script("arguments[0].click();", confirm_btn)


    try:
        WebDriverWait(driver, TICKET_TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, '//button[@type = "submit"]'))
        )
    except TimeoutException:
        driver.refresh()
        raise


def buy_ticket(driver, goal_event):

    plus_button = goal_event.find_element(By.CSS_SELECTOR, "button.plus")
    for _ in range(votes):
        plus_button.click()

    agree_checkbox = WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.element_to_be_clickable((By.ID, 'person_agree_terms'))
    )
    driver.execute_script("arguments[0].click();", agree_checkbox)

    submit_button = WebDriverWait(driver, PAGE_TIMEOUT).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'ng-isolate-scope'))
    )
    driver.execute_script("arguments[0].click();", submit_button)

    try:
        WebDriverWait(driver, TICKET_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.controls input[type='text']"))
        )
    except TimeoutException:
        driver.refresh()
        raise


if __name__ == '__main__':
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service)
    login(driver, email, password)
    begin_time_ts = datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S").timestamp()
    wait_flag = True


    while True:
        try:
            # 获取票务元素
            event_element = find_event(driver, goal_index)

            # 等待开票
            if wait_flag:
                while datetime.now().timestamp() < begin_time_ts:
                    time.sleep(0.1)
                wait_flag = False

            # 购票流程
            while True:
                try:
                    buy_ticket(driver, event_element)
                    break
                except Exception as e:
                    print(f'Exception: {e}')
                    event_element = find_event(driver, goal_index)
                    continue

            # 信息填写流程
            while True:
                try:
                    fill_blank(driver, name, phone)
                    break
                except Exception as e:
                    print(f'Exception: {e}')
                    continue

            print("Ticket purchased successfully!")
            time.sleep(600) # 十分钟支付时间
            break

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            continue

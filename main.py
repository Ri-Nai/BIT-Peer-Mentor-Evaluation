# encoding: utf-8
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

absolute_path = os.path.dirname(__file__)
print(absolute_path)
os.chdir(absolute_path)
config = json.load(open("config.json"))


class EvaluationDriver:
    def __init__(self):
        self.website_login_url = config["website_login_url"]
        self.user_account = config["user_account"]
        self.user_password = config["user_password"]
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 无头模式
        options.add_argument("--disable-gpu")  # 禁用 GPU
        options.add_argument("--no-sandbox")  # 解决无权限问题（某些系统下）
        options.add_argument("--disable-dev-shm-usage")  # 共享内存的禁用
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging", "enable-automation"]
        )
        self.driver = webdriver.Chrome(options=options)

    def login(self):

        self.driver.get(self.website_login_url)
        time.sleep(1)

        login_form = self.driver.find_element(
            By.XPATH, "/html/body/div[1]/div[2]/div/section/div[2]/div[1]/div/form"
        )
        login_form.find_element(By.XPATH, "div/div[1]/div[1]/input").send_keys(
            self.user_account
        )
        login_form.find_element(By.XPATH, "div/div[1]/div[2]/input[1]").send_keys(
            self.user_password
        )

        time.sleep(0.5)
        login_form.find_element(By.XPATH, "div/div[3]/a").click()

        time.sleep(2)

        # 刷新页面
        self.driver.refresh()

        time.sleep(2)

    def evaluate(self):
        print("正在获取学生列表")
        total_students = int(
            self.driver.find_element(
                By.XPATH,
                "/html/body/main/article/section/div[3]/div[2]/div/div[10]/div/div/div[1]/span[1]",
            ).text.split()[-1]
        )
        page_num = int(
            self.driver.find_element(
                By.XPATH,
                "/html/body/main/article/section/div[3]/div[2]/div/div[10]/div/div/div[1]/span[2]",
            ).text.split()[1]
        )

        print(f"共有{total_students}个学生需要评价")
        print(f"共有{page_num}页")
        for i in range(page_num):
            self.process_page(i)

    def process_page(self, page_num):
        print(f"正在处理第{page_num + 1}页")

        def find_students():
            return self.driver.find_elements(
                By.XPATH,
                "/html/body/main/article/section/div[3]/div[2]/div/div[4]/div[2]/div/table/tbody/tr",
            )

        student_num = len(find_students())
        for i in range(student_num):
            print(f"正在处理第{page_num + 1}页的第{i + 1}个学生")
            self.process_student(find_students()[i])

        self.driver.find_element(
            By.XPATH,
            "/html/body/main/article/section/div[3]/div[2]/div/div[10]/div/div/div[1]/a[3]",
        ).click()
        time.sleep(1)

    def process_student(self, student):
        student_id = student.find_element(By.XPATH, "td[6]/span").text
        student_name = student.find_element(By.XPATH, "td[7]/span").text
        class_name = student.find_element(By.XPATH, "td[11]/span").text
        print(f"正在评价学生：{student_name}，学号：{student_id}，班级：{class_name}")

        status = student.find_element(By.XPATH, "td[3]/span").text
        if status == "已评价":
            print("已评价，跳过")
            return

        student.find_element(By.XPATH, "td[2]/a").click()
        time.sleep(1)
        self.evaluate_questions()

    def evaluate_questions(self):
        questions = self.driver.find_elements(By.CLASS_NAME, "scenes-cbrt-record")
        for question in questions:
            title = question.find_element(By.XPATH, "div/div/div/div[1]/label").text
            star = question.find_element(By.XPATH, "div/div/div/div[3]/div/div/span[7]")
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", star
            )
            star.click()
            print(f"{title}：7⭐")

        self.driver.find_element(
            By.XPATH, "/html/body/div[9]/div/div[2]/footer/a"
        ).click()
        self.driver.find_element(
            By.XPATH, "/html/body/div[10]/div[1]/div[1]/div[2]/div[2]/a[1]"
        ).click()
        print("评价完成!")
        time.sleep(3)


if __name__ == "__main__":
    driver = EvaluationDriver()
    driver.login()
    driver.evaluate()

from selenium import webdriver
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from sql import Sql
import datetime

def first_landing(new_bro,config):
    url = config['url']
    css_selector = str(config['css_selector'])
    new_bro.get(url)

    print('正在加载主页')
    sleep(2)
    print('正在寻找登陆按钮')

    flag = WebDriverWait(new_bro, 120, 0.2).until(
        lambda x: x.find_element_by_css_selector("#idp_section_buttons > button")).text  # 等待登陆按钮
    log_in = new_bro.find_element_by_xpath('//*[@id="idp_section_buttons"]/button')  # 找到登陆按钮

    print('点击登陆按钮')
    log_in.click()  # 点击登陆按钮
    print('开始加载第一页')

    each_flag = WebDriverWait(new_bro, 120, 0.2).until(lambda x: x.find_element_by_css_selector(css_selector % 10)).text  # 等待第一页case加载完毕

    # 返回加载完毕的浏览器实例对象
    return new_bro

class Salesforce:

    def __init__ (self, db, bro, config):
        self.db = db
        self.bro = bro
        self.sql = Sql(db)
        self.config = config
        self.css_selector = str(config['css_selector'])
        self.refresh_button = str(config['refresh_button'])

    def get_day_time (self):
        day_time = datetime.datetime.now().strftime('%Y-%m-%d')
        return day_time

    def tran_date(self,date):
        dl = date.split(' ')
        day_list = dl[0].split('-')
        time = dl[1]
        year = day_list[0]
        mouth = day_list[1]
        day = day_list[2]
        old_hour = time.split(':')[0][2:]
        minn = time.split(':')[1]
        sec = '00'
        fg = time[0:2]
        if fg =='PM':
            hour = int(old_hour) + 12
            if hour ==24:
                hour = int(old_hour)
        else:
            hour = old_hour
        new_date = datetime.datetime(int(year), int(mouth), int(day),int(hour),int(minn),int(sec))
        result_date = str(new_date)[:-3]
        return result_date

    def refresh_get_source(self,page):
        refresh = self.bro.find_element_by_xpath(self.refresh_button)
        refresh.click()
        print('自动点击刷新按钮，刷新salesforce页面')
        sleep(8)
        for i in range(1, page+1):
            print('自动翻页，当前第%s页'%i)
            each_css_selector = self.css_selector % (25*i)
            each_flag = WebDriverWait(self.bro, 30, 0.2).until(lambda x: x.find_element_by_css_selector(each_css_selector)).text
            each_target = self.bro.find_element_by_css_selector(each_css_selector)
            self.bro.execute_script("arguments[0].scrollIntoView();", each_target)

        fina_flag = WebDriverWait(self.bro, 30, 0.2).until(lambda x: x.find_element_by_css_selector(self.css_selector % (25 * (page + 1)))).text
        page_source = self.bro.page_source


        return page_source

    def customer_case(self,insert_sql,update_sql,new_select_sql,insert_dict):
        continue_flag = 0
        wait_flag = 0
        cursor = self.db.cursor()
        cursor.execute(new_select_sql)
        result = cursor.fetchone()
        if result:
            if result[-1] == 'N':
                insert_dict['customer_ID'] = result[0]
                continue_flag, wait_flag = self.sql.sub_sql([insert_sql, update_sql, new_select_sql, insert_dict])
        return continue_flag,wait_flag

    def parse (self, source):
        tree = etree.HTML(source)
        tr_list = tree.xpath(
            '//*[@id="brandBand_1"]/div/div/div/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div/div/table/tbody/tr')
        num = 0
        wait_flag = 0
        for tr in tr_list[1:]:
            case_number = tr.xpath('./th/span/a/text()')[0][2:]
            case_subject1 = tr.xpath('./td[4]/span//div/a/text()')
            status = tr.xpath('./td[5]/span/span/text()')[0]
            web_email1 = tr.xpath('./td[7]/span/a/@href')
            open_date = self.tran_date(tr.xpath('./td[9]/span/span/text()')[0])
            modified_date = self.tran_date(tr.xpath('./td[10]/span/span/text()')[0])
            case_responsible1 = tr.xpath('./td[11]/span/a/text()')
            if case_subject1:
                subject = case_subject1[0]
            else:
                subject = 'NULL'
            if web_email1:
                web_email = web_email1[0].split(':')[-1]
            else:
                web_email = 'NULL'
            if case_responsible1:
                case_responsible = case_responsible1[0]
            else:
                case_responsible = 'NULL'
            insert_dict = {
                'case_number':case_number,
                'subject':subject,
                'status':status,
                'web_email':web_email,
                'open_date':open_date,
                'modified_date':modified_date,
                'case_responsible':case_responsible
            }
            insert_sql = f"insert into salesforce \
                        ( workorder_ID, case_number, subject, statues, web_email, open_date, modified_date, case_responsible)\
                        VALUES ( '%s','{case_number}',\
                        '{subject}',\
                        '{status}',\
                        '{web_email}',\
                        '{open_date}',\
                        '{modified_date}',\
                        '{case_responsible}');\
                        "
            update_sql = f"insert into salesforce \
                    ( workorder_ID, case_number, subject, statues, web_email, open_date, modified_date, case_responsible)\
                    VALUES ('%s', '{case_number}',\
                    '{subject}',\
                    '{status}',\
                    '{web_email}',\
                    '{open_date}',\
                    '{modified_date}',\
                    '{case_responsible}')\
                    on duplicate key update \
                    subject = '{subject}',\
                    statues = '{status}',\
                    web_email = '{web_email}',\
                    open_date = '{open_date}',\
                    modified_date = '{modified_date}',\
                    case_responsible = '{case_responsible}';\
                    "
            select_sql = f"select salesforce.workorder_ID \
                    from salesforce where salesforce.case_number = '{case_number}';\
                    "
            update_customer_case_sql = f"insert into salesforce \
                    VALUES ('%s', '{case_number}',\
                    '{subject}',\
                    '{status}',\
                    '{web_email}',\
                    '{open_date}',\
                    '{modified_date}',\
                    '{case_responsible}',\
                    'Y')\
                    on duplicate key update \
                    workorder_ID = '%s',\
                    subject = '{subject}',\
                    statues = '{status}',\
                    web_email = '{web_email}',\
                    open_date = '{open_date}',\
                    modified_date = '{modified_date}',\
                    case_responsible = '{case_responsible}',\
                    flag = 'Y';\
                    "
            select_customer_case_sql = f"select * \
                    from customer_case where customer_case.case_number = '{case_number}';\
                    "
            try:
                continue_flag,wait_flag = self.sql.sub_sql([insert_sql,update_sql,select_sql,insert_dict])
                continue_flag,wait_flag = self.customer_case(insert_sql,update_customer_case_sql,select_customer_case_sql,insert_dict)
            except BaseException as e:
                print("提交salesforce数据出错,case number:",case_number)
                continue
            num += 1
        return num,wait_flag

    def main_def(self):
        source = self.refresh_get_source(self.config['page'])

        print('已获取最新salesforce源码数据')
        sleep(3)
        print('开始解析salesforce源码数据')

        num,wait_flag = self.parse(source)

        print('本次刷新case数：', num)


if __name__ == '__main__':
    import pymysql
    from selenium.webdriver.chrome.options import Options

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    new_bro = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

    db = pymysql.connect("localhost", "root", "123456", "kuka")
    bro = first_landing(new_bro)
    salesforce = Salesforce(db,bro)
    for i in range(10):
        salesforce.main_def()
        print('第%s次'%i)
    db.close()
    bro.close()
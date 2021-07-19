import traceback
import requests
import re
from sql import Sql
from post import Udesk
from time import sleep
import time
import datetime
import sys

class Parts:
    def __init__ (self,db,config):
        self.sql = Sql(db)
        self.order_re = r"\d\d\d\d\d\d\d"
        self.notification_re = r"\d\d\d\d\d\d\d\d\d"
        self.sn_re = r"\d\d\d\d\d\d\d?"
        self.an_re = r"0*?(2000)?(\d\d)?-?(\d\d\d)-?(\d\d\d)"
        self.parts_count = 0
        self.udesk = Udesk()
        self.config = config

    def get_time (self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=self.config['days'])
        yesterday = today - one_day
        return [str(yesterday), str(today)]

    def get_data (self):
        login_url = 'https://wx1.kuka-robotics.cn/kd/adminapi/login'
        login_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'wx1.kuka-robotics.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://wx1.kuka-robotics.cn/partsadmin/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }
        data = {
            'password': '123456',
            'username': 'hotline'
        }
        print('正在执行备件平台远程虚拟登陆')
        auth = requests.post(url=login_url,headers=login_headers,data=data).json()['data']['token']
        authorization = 'bearer' + auth

        url = self.config['url']
        headers = {
            'authorization':authorization,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'wx1.kuka-robotics.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://wx1.kuka-robotics.cn/partsadmin/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }
        time_list = self.get_time()
        params = {
            "filter[created_at]": f"{time_list[0]}%2000:00:00,{time_list[1]}%2000:00:00",
            "page": 1,
            "limit": self.config['number']
        }
        page_json = requests.get(url=url,params=params,headers=headers).json()
        return page_json

    def parse(self, page_json):
        num = 0
        wait_flag = 0
        for pre_part in page_json['data']:
            id = pre_part['id']
            order = pre_part['so']
            proposer = pre_part['name']
            rsn = pre_part['sn']
            csn = pre_part['control_sn']
            an = pre_part['material_no']
            quantity = pre_part['material_no_num']
            customer_name = pre_part['customer_user']
            customer_company = pre_part['customer_name']
            customer_phone = pre_part['customer_mobile']
            order_state = pre_part['status']
            sf_info = pre_part['sf']

            if order:
                order_re_result = re.match(self.order_re, order, re.S)
                if order_re_result:
                    order1 = order_re_result.group()
                else:
                    order1 = 'NULL'
            else:
                order1 = 'NULL'
            if rsn:
                rsn_re_result = re.match(self.sn_re, rsn, re.S)
                if rsn_re_result:
                    rsn = rsn_re_result.group()
                else:
                    rsn = 'NULL'
            else:
                rsn = 'NULL'

            if csn:
                csn_re_result = re.match(self.sn_re, csn, re.S)
                if csn_re_result:
                    csn = csn_re_result.group()
                else:
                    csn = 'NULL'
            else:
                csn = 'NULL'

            if an:
                an_re_result = re.findall(self.an_re, an, re.S)
                if len(an_re_result) == 0:
                    an = 'NULL'
                else:
                    an = ''.join(an_re_result[0])
            else:
                an = 'NULL'

            if not sf_info:
                sf_info = 'NULL'

            #if order1 == 'NULL':
            #    continue

            #if rsn == 'NULL' and csn == 'NULL':
            #    continue
            #elif an == 'NULL':
            #    continue

            insert_dict = {
                "parts_id":id,
                "order1":order1,
                'proposer':proposer,
                'rsn':rsn,
                'csn':csn,
                'an':an,
                'quantity':quantity,
                'customer_name':customer_name,
                'customer_company':customer_company,
                'customer_phone':customer_phone,
                'order_state':order_state,
                'sf_info':sf_info
            }
            insert_sql = f"insert into kuka.parts \
                        VALUES ('%s','{id}', \
                        '{order1}',\
                        '{proposer}',\
                        '{rsn}',\
                        '{csn}',\
                        '{an}',\
                        '{quantity}',\
                        '{customer_name}',\
                        '{customer_company}',\
                        '{customer_phone}',\
                        '{order_state}',\
                        '{sf_info}')\
                        "
            update_sql = f"insert into kuka.parts \
                VALUES ('%s','{id}', \
                '{order1}',\
                '{proposer}',\
                '{rsn}',\
                '{csn}',\
                '{an}',\
                '{quantity}',\
                '{customer_name}',\
                '{customer_company}',\
                '{customer_phone}',\
                '{order_state}',\
                '{sf_info}')\
                on duplicate key update\
                parts_order1 = '{order1}',\
                order_state = '{order_state}',\
                sf_info = '{sf_info}',\
                proposer = '{proposer}',\
                rsn = '{rsn}',\
                csn = '{csn}',\
                an = '{an}',\
                quantity = '{quantity}',\
                customer_name = '{customer_name}',\
                customer_company = '{customer_company}',\
                customer_phone = '{customer_phone}';\
                "
            select_sql = f"select parts.workorder_ID \
                from parts where parts.parts_ID = '{id}';\
                "
            try:
                continue_flag,wait_flag = self.sql.sub_sql([insert_sql,update_sql,select_sql,insert_dict])
            except BaseException as e:
                print("提交parts数据出错",insert_sql)
                continue
            num += 1
        return num,wait_flag

    def main_def (self):
        page_json = self.get_data()

        print('已获取最新parts源码数据')
        sleep(3)
        print('开始解析parts源码数据')

        num,wait_flag = self.parse(page_json)
        print('本次刷新备件数：',num)


if __name__ == '__main__':
    import pymysql
    import json
    fp = open("./config.json", 'r')
    config = json.load(fp)
    parts_config = config['parts']
    db = pymysql.connect("10.86.193.139", "root", "123456", "kuka")
    parts = Parts(db,parts_config)
    parts.main_def()
    db.close()
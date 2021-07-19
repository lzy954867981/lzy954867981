import re
import requests
import datetime
import xlrd
from sql import Sql
from lxml import etree
from parse_order_type import parse_order_type
from time import sleep


def get_detail_headers (config):
    session = requests.Session()

    start_url = config['start_url']
    log_in_url = config['log_in_url']

    start_headers = {
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
        'Connection': 'Keep-Alive',
        'Host': 'wx1.kuka-robotics.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
    }
    log_in_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '43',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'wx1.kuka-robotics.cn',
        'Origin': 'http://wx1.kuka-robotics.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://wx1.kuka-robotics.cn/index.php/Qwadmin/login/index.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    }
    detail_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'wx1.kuka-robotics.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://wx1.kuka-robotics.cn/index.php/Qwadmin/login/index.html',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
    }
    data = {
        'user': 'allen.liu@kuka.com',
        'password': 'kuka2020'
    }
    print('正在执行派遣平台远程虚拟登陆')
    response1 = session.post(url=start_url, headers=start_headers)
    request_cookie = response1.headers['Set-Cookie'].split(';')[0]
    log_in_headers['Cookie'] = request_cookie

    response2 = session.post(url=log_in_url, headers=log_in_headers, data=data, allow_redirects=False)
    response_cookie = response2.headers['Set-Cookie'].split(';')[0]
    detail_headers['Cookie'] = request_cookie + '; ' + response_cookie

    return detail_headers, session


class Assignment:

    def __init__ (self, db, config):
        self.filename = './two_days_case_details.xls'
        self.sn_re = r"\d\d\d\d\d\d\d?"
        self.phone_re = r"(\d\d\d)[-\s]?(\d\d\d\d)[-\s]?(\d\d\d\d)"
        self.sql = Sql(db)
        self.detail_headers, self.session = get_detail_headers(config)
        self.config = config

    def get_time (self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=self.config['days'])
        yesterday = today - one_day
        return [str(yesterday), str(today)]

    def get_complete_order_source (self, complete_list, headers):
        for each_order in complete_list:
            sql = "SELECT assignment_ID,order_state FROM kuka.assignment where assignment_ID ='%d'" % each_order
            self.sql.sub_sql(sql)
            each_url = 'http://wx1.kuka-robotics.cn/index.php/Qwadmin/Baoxiu/newgzd/id/%d.html' % each_order
            page_resource = self.session.post(url=each_url, headers=headers).text
            tree = etree.HTML(page_resource)
            order_list = tree.xpath('/html/body/div/div/table//tr[3]/td[3]/div/h2/text()')
            if order_list:
                order_list.split('/')

    def get_source (self):
        time_list = self.get_time()
        details_url = 'http://wx1.kuka-robotics.cn/index.php/Qwadmin/Baoxiu/expUser/keyword1/%s/keyword2/%s' % (
            time_list[0], time_list[1])
        '''
        start_headers = {
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
            'Connection': 'Keep-Alive',
            'Host': 'wx1.kuka-robotics.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'
        }

        log_in_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '43',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'wx1.kuka-robotics.cn',
            'Origin': 'http://wx1.kuka-robotics.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://wx1.kuka-robotics.cn/index.php/Qwadmin/login/index.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }
        detail_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'wx1.kuka-robotics.cn',
            'Pragma': 'no-cache',
            'Referer': 'http://wx1.kuka-robotics.cn/index.php/Qwadmin/login/index.html',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
        }
        data = {
            'user': 'allen.liu@kuka.com',
            'password': 'kuka2020'
        }
        
        print('正在执行派遣平台远程虚拟登陆')
        response1 = session.post(url=start_url, headers=start_headers)
        request_cookie = response1.headers['Set-Cookie'].split(';')[0]
        log_in_headers['Cookie'] = request_cookie

        response2 = session.post(url=log_in_url, headers=log_in_headers, data=data, allow_redirects=False)
        response_cookie = response2.headers['Set-Cookie'].split(';')[0]
        detail_headers['Cookie'] = request_cookie + '; ' + response_cookie
        '''
        while True:
            try:
                response3 = self.session.get(url=details_url, headers=self.detail_headers)
                break
            except:
                self.detail_headers, self.session = get_detail_headers()

        with open(self.filename, 'wb') as fp:
            fp.write(response3.content)
        return None

    def parse (self, row):
        serial_list = []
        phone_list = []
        insert_dict = {
            'assignment_ID': 'NULL',
            'order1': 'NULL',
            'order2': 'NULL',
            'product_info': 'NULL',
            'product_type': 'NULL',
            'serial1': 'NULL',
            'serial2': 'NULL',
            'serial3': 'NULL',
            'serial4': 'NULL',
            'serial5': 'NULL',
            'serial6': 'NULL',
            'customer_name': 'NULL',
            'customer_phone': 'NULL',
            'customer_phone2': 'NULL',
            'customer_email': 'NULL',
            'customer_company': 'NULL',
            'customer_address': 'NULL',
            'service_content': 'NULL',
            'engineer1': 'NULL',
            'engineer2': 'NULL',
            'order_state': 'NULL',
            'start_time': '1970-01-01',
            'end_time': '1970-01-01',
            'open_time': '1970-01-01 08:00',
            'normal_hours': '0',
            'order_type': 'NULL'
        }
        ass_id = int(row[0])
        if type(row[1]) == float:
            order = str(int(row[1]))
        else:
            order = str(row[1])
        prod_info = str(row[2])
        prod_type = str(row[3])
        serial = str(row[4])
        name = str(row[5])
        phone = str(row[6])
        email = str(row[7])
        request = str(row[8])
        eng1 = str(row[10])
        open_time = str(row[11])
        order_state = str(row[12])
        company = str(row[13])
        address = str(row[14])
        eng2 = str(row[15])
        ass_time = str(row[24])
        normal_hours = str(row[25])

        if prod_info:
            insert_dict['product_info'] = prod_info
            prod_info_result = re.findall(self.sn_re, prod_info, re.S)
            if len(prod_info_result) > 0:
                for each_serial1 in prod_info_result:
                    if each_serial1 not in serial_list:
                        serial_list.append(each_serial1)
        if prod_type:
            insert_dict['product_type'] = prod_type
            prod_type_result = re.findall(self.sn_re, prod_type, re.S)
            if len(prod_type_result) > 0:
                for each_serial2 in prod_type_result:
                    if each_serial2 not in serial_list:
                        serial_list.append(each_serial2)
        if serial:
            serial_result = re.findall(self.sn_re, serial, re.S)
            if len(serial_result) > 0:
                for each_serial3 in serial_result:
                    if each_serial3 not in serial_list:
                        serial_list.append(each_serial3)
        if phone:
            phone_result = re.findall(self.phone_re, phone, re.S)
            if phone_result:
                for i in phone_result:
                    each_phone = ''.join(i)
                    if each_phone not in phone_list:
                        phone_list.append(each_phone)
        if order:
            order_list = order.split('/')
        if ass_time:
            if ass_time == '-':
                insert_dict['start_time'] = '1970-01-01'
                insert_dict['end_time'] = '1970-01-01'
            else:
                insert_dict['start_time'] = ass_time[:10]
                insert_dict['end_time'] = ass_time[11:]
        else:
            insert_dict['start_time'] = '1970-01-01'
            insert_dict['end_time'] = '1970-01-01'
        if ass_id:
            insert_dict['assignment_ID'] = ass_id
        if name:
            insert_dict['customer_name'] = name
        if email:
            insert_dict['customer_email'] = email
        if company:
            insert_dict['customer_company'] = company
        if address:
            insert_dict['customer_address'] = address
        if request:
            insert_dict['service_content'] = request
        if eng1:
            insert_dict['engineer1'] = eng1
        if eng2:
            insert_dict['engineer2'] = eng2
        if order_state:
            insert_dict['order_state'] = order_state
        if open_time:
            insert_dict['open_time'] = open_time
        else:
            insert_dict['open_time'] = '1970-01-01 08:00'
        if ass_time:
            insert_dict['assignment_date'] = ass_time
        if normal_hours:
            insert_dict['normal_hours'] = normal_hours
        else:
            insert_dict['normal_hours'] = '0'
        if insert_dict['order_state'] == '已完成':
            complete_id = insert_dict['assignment_ID']
        else:
            complete_id = None

        try:
            insert_dict['serial1'] = serial_list[0]
            insert_dict['serial2'] = serial_list[1]
            insert_dict['serial3'] = serial_list[2]
            insert_dict['serial4'] = serial_list[3]
            insert_dict['serial5'] = serial_list[4]
            insert_dict['serial6'] = serial_list[5]
        except:
            pass

        try:
            insert_dict['order1'] = order_list[0]
            insert_dict['order2'] = order_list[1]
        except:
            pass

        try:
            insert_dict['customer_phone'] = phone_list[0]
            insert_dict['customer_phone2'] = phone_list[1]
        except:
            pass
        finally:
            return insert_dict

    def sql_parse (self, insert_dict):
        order1 = insert_dict['order1']
        order2 = insert_dict['order2']
        order_type = parse_order_type(order1=order1,order2=order2)
        insert_dict['order_type'] = order_type
        insert_sql = f"insert into assignment \
                    VALUES ( '%s','{insert_dict['assignment_ID']}',\
                    '{insert_dict['order1']}',\
                    '{insert_dict['order2']}',\
                    '{insert_dict['order_type']}',\
                    '{insert_dict['serial1']}',\
                    '{insert_dict['serial2']}',\
                    '{insert_dict['serial3']}',\
                    '{insert_dict['serial4']}',\
                    '{insert_dict['serial5']}',\
                    '{insert_dict['serial6']}',\
                    '{insert_dict['customer_name']}',\
                    '{insert_dict['customer_phone']}',\
                    '{insert_dict['customer_phone2']}',\
                    '{insert_dict['customer_email']}',\
                    '{insert_dict['customer_company']}',\
                    '{insert_dict['customer_address']}',\
                    '{insert_dict['service_content']}',\
                    '{insert_dict['engineer1']}',\
                    '{insert_dict['engineer2']}',\
                    '{insert_dict['order_state']}',\
                    '{insert_dict['start_time']}',\
                    '{insert_dict['end_time']}',\
                    '{insert_dict['open_time']}',\
                    '{insert_dict['normal_hours']}');\
                    "
        update_sql = f"insert into assignment \
                VALUES ( '%s','{insert_dict['assignment_ID']}',\
                '{insert_dict['order1']}',\
                '{insert_dict['order2']}',\
                '{insert_dict['order_type']}',\
                '{insert_dict['serial1']}',\
                '{insert_dict['serial2']}',\
                '{insert_dict['serial3']}',\
                '{insert_dict['serial4']}',\
                '{insert_dict['serial5']}',\
                '{insert_dict['serial6']}',\
                '{insert_dict['customer_name']}',\
                '{insert_dict['customer_phone']}',\
                '{insert_dict['customer_phone2']}',\
                '{insert_dict['customer_email']}',\
                '{insert_dict['customer_company']}',\
                '{insert_dict['customer_address']}',\
                '{insert_dict['service_content']}',\
                '{insert_dict['engineer1']}',\
                '{insert_dict['engineer2']}',\
                '{insert_dict['order_state']}',\
                '{insert_dict['start_time']}',\
                '{insert_dict['end_time']}',\
                '{insert_dict['open_time']}',\
                '{insert_dict['normal_hours']}')\
                on duplicate key update \
                order_state = '{insert_dict['order_state']}',\
                ass_order1 = '{insert_dict['order1']}',\
                ass_order2 = '{insert_dict['order2']}',\
                order_type = '{insert_dict['order_type']}',\
                serial1 = '{insert_dict['serial1']}',\
                serial2 = '{insert_dict['serial2']}',\
                serial3 = '{insert_dict['serial3']}',\
                serial4 = '{insert_dict['serial4']}',\
                serial5 = '{insert_dict['serial5']}',\
                serial6 = '{insert_dict['serial6']}',\
                customer_name = '{insert_dict['customer_name']}',\
                customer_phone = '{insert_dict['customer_phone']}',\
                customer_phone2 = '{insert_dict['customer_phone2']}',\
                customer_email = '{insert_dict['customer_email']}',\
                customer_company = '{insert_dict['customer_company']}',\
                customer_address = '{insert_dict['customer_address']}',\
                service_content = '{insert_dict['service_content']}',\
                engineer1 = '{insert_dict['engineer1']}',\
                engineer2 = '{insert_dict['engineer2']}',\
                start_time = '{insert_dict['start_time']}',\
                end_time = '{insert_dict['end_time']}',\
                open_time = '{insert_dict['open_time']}',\
                normal_hours = '{insert_dict['normal_hours']}';\
                "
        select_sql = f"select assignment.workorder_ID \
                    from assignment where assignment.assignment_ID = '{insert_dict['assignment_ID']}';\
                    "
        return [insert_sql,update_sql,select_sql,insert_dict]#,continue_flag

    def open_xls_and_sub_sql (self):
        num = 0
        wait_flag = 0
        book = xlrd.open_workbook(self.filename)
        sheet = book.sheet_by_index(0)
        rows = sheet.nrows
        for i in range(1, rows):
            each_row = sheet.row_values(i)
            insert_dict = self.parse(each_row)
            sql_list = self.sql_parse(insert_dict)

            # 解析出已完成的case和未处理的case，获取已完成case详情页的内容，生成未处理case工单
            try:
                continue_flag,wait_flag = self.sql.sub_sql(sql_list)
            except BaseException as e:
                print("提交assignment数据出错",sql_list[0])
                continue
            num += 1
        return num,wait_flag

    def main_def (self):
        self.get_source()

        print('已获取最新assignment源码数据')
        sleep(3)
        print('开始解析assignment源码数据')

        num,wait_flag = self.open_xls_and_sub_sql()

        print('本次刷新派遣数:',num)

if __name__ == '__main__':
    import pymysql
    db = pymysql.connect("localhost", "root", "123456", "kuka")
    assignment = Assignment(db)
    assignment.main_def()
    db.close()
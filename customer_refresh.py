from time import perf_counter
import time
from post import Udesk
import requests

"""
{'id': 210091, 'name': '6-10次', 'active': True}, {'id': 210119, 'name': '系统集成商', 'active': True}, 
{'id': 210120, 'name': '最终用户', 'active': True}, {'id': 210121, 'name': '所有留资客户', 'active': True}, 
{'id': 218923, 'name': '仅1次（有效）', 'active': True}, {'id': 218924, 'name': '2次', 'active': True}, 
{'id': 218925, 'name': '3-5次', 'active': True}, {'id': 234714, 'name': '所有有效客户', 'active': True}, 
{'id': 266723, 'name': 'IM来源/交互 客户', 'active': True}, {'id': 266724, 'name': '热线来源/交互 客户', 'active': True}, 
{'id': 266725, 'name': '直播来源/未交互 客户', 'active': True}, {'id': 266726, 'name': '服务来源/未交互 客户', 'active': True}, 
{'id': 326976, 'name': 'IM来源无手机号客户', 'active': True}, {'id': 327171, 'name': 'yangjp自来水短信发送', 'active': False}, 
{'id': 327740, 'name': '8.24预发送', 'active': False}, {'id': 327764, 'name': '8.25预发送', 'active': False}, 
{'id': 327773, 'name': '8.26预发送', 'active': False}, {'id': 327781, 'name': '8.27 预发送', 'active': False}, 
{'id': 327803, 'name': '8.28日预发送', 'active': False}, {'id': 328625, 'name': '202009月NPS回访', 'active': False}, 
{'id': 329167, 'name': '111', 'active': False}, {'id': 329202, 'name': '202010月NPS回访', 'active': False}, 
{'id': 329940, 'name': '信息完整的客户', 'active': True}, {'id': 330047, 'name': '大客户', 'active': True}, 
{'id': 330052, 'name': '本周更新客户', 'active': True}]}
TextField_12524 :case_number
'nick_name':customer_name
email:customer_email
"""


def customer_refresh(db):
    print('正在刷新udesk客户')
    time.sleep(10)
    cursor = db.cursor()
    udesk = Udesk()
    for i in range(1,10):
        params = {
            'filter_id':'330052',
            'page':i,
            'page_size':'100'
        }
        url = udesk.get_url()[3]
        response_json = requests.get(url=url,params=params).json()
        if 'status' in response_json and response_json['status'] == 429:
            break
        customer_list = response_json['customers']
        for each_customer in customer_list:
            insert_dict = dict(customer_ID='NULL', customer_name='NULL', customer_phone='NULL', customer_phone_ID='NULL',
                               customer_phone2='NULL', customer_phone2_ID='NULL', customer_email='NULL',
                               customer_company_ID='NULL', case_number1='NULL', case_number2='NULL', case_number3='NULL',
                               case_number4='NULL', case_number5='NULL', case_number6='NULL')

            insert_dict['customer_ID'] = each_customer['id']
            insert_dict['customer_name'] = each_customer['nick_name']

            try:
                insert_dict['customer_phone_ID'] = each_customer['cellphones'][0]['id']
                insert_dict['customer_phone'] = each_customer['cellphones'][0]['content']
                insert_dict['customer_phone2_ID'] = each_customer['cellphones'][1]['id']
                insert_dict['customer_phone2'] = each_customer['cellphones'][1]['content']
            except:
                pass
            if each_customer['email'] == '':
                insert_dict['customer_email'] = 'NULL'
            else:
                insert_dict['customer_email'] = each_customer['email']

            if not each_customer['organization_id']:
                insert_dict['customer_company_ID'] = 'NULL'
            else:
                insert_dict['customer_company_ID'] = each_customer['organization_id']
            try:
                case_number_list = each_customer['custom_fields']['TextField_12524'].split('\n')
                insert_dict['case_number1'] = case_number_list[0]
                insert_dict['case_number2'] = case_number_list[1]
                insert_dict['case_number3'] = case_number_list[2]
                insert_dict['case_number4'] = case_number_list[3]
                insert_dict['case_number5'] = case_number_list[4]
                insert_dict['case_number6'] = case_number_list[5]
            except:
                pass
            update_sql = f"insert into customer \
                        VALUES ('{insert_dict['customer_ID']}',\
                        '{insert_dict['customer_name']}',\
                        '{insert_dict['customer_phone']}',\
                        '{insert_dict['customer_phone_ID']}',\
                        '{insert_dict['customer_phone2']}',\
                        '{insert_dict['customer_phone2_ID']}',\
                        '{insert_dict['customer_email']}',\
                        '{insert_dict['customer_company_ID']}',\
                        '{insert_dict['case_number1']}',\
                        '{insert_dict['case_number2']}',\
                        '{insert_dict['case_number3']}',\
                        '{insert_dict['case_number4']}',\
                        '{insert_dict['case_number5']}',\
                        '{insert_dict['case_number6']}')\
                        on duplicate key update \
                        customer_name = '{insert_dict['customer_name']}',\
                        customer_phone = '{insert_dict['customer_phone']}',\
                        customer_phone_ID = '{insert_dict['customer_phone_ID']}',\
                        customer_phone2 = '{insert_dict['customer_phone2']}',\
                        customer_phone2_ID = '{insert_dict['customer_phone2_ID']}',\
                        customer_email = '{insert_dict['customer_email']}',\
                        customer_company_ID = '{insert_dict['customer_company_ID']}',\
                        case_number1 = '{insert_dict['case_number1']}',\
                        case_number2 = '{insert_dict['case_number2']}',\
                        case_number3 = '{insert_dict['case_number3']}',\
                        case_number4 = '{insert_dict['case_number4']}',\
                        case_number5 = '{insert_dict['case_number5']}',\
                        case_number6 = '{insert_dict['case_number6']}';\
                        "
            flag = cursor.execute(update_sql)
            db.commit()
    print('udesk客户刷新完毕')


if __name__ == '__main__':
    import pymysql
    db = pymysql.connect("localhost", "root", "123456", "kuka")
    customer_refresh(db)
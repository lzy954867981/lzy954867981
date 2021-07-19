import requests
import random
import hashlib
import time
import json


class Udesk:
    """
    备件模板编号：28210
    派遣模板编号：28209
    case模板编号：28211
    """

    udesk_dict = {
        '项目号': 'TextField_12443',
        '项目类别': 'SelectField_7180',
        '附加项目号': 'TextField_12444',
        'assignment_ID': 'TextField_12446',
        '派遣项目状态': 'SelectField_7181',
        '派遣序列号1': 'TextField_12447',
        '派遣序列号2': 'TextField_12448',
        '派遣序列号3': 'TextField_12449',
        '派遣序列号4': 'TextField_12450',
        '派遣序列号5': 'TextField_12451',
        '派遣序列号6': 'TextField_12452',
        '派遣联系人': 'TextField_12453',
        '派遣联系人电话': 'TextField_12455',
        '派遣联系人电话2': 'TextField_12456',
        '派遣联系人邮箱': 'TextField_12457',
        '派遣联系人公司': 'TextField_12458',
        '派遣联系人地址': 'TextField_12459',
        '派遣服务内容': 'TextField_12460',
        '派遣工程师1': 'TextField_12461',
        '派遣工程师2': 'TextField_12462',
        '派遣开始日期': 'TextField_12463',
        '派遣结束日期': 'TextField_12464',
        '派遣创建时间': 'TextField_12465',
        '派遣计划服务时长': 'TextField_12466',
        'parts_ID': 'TextField_12467',
        '备件申请人': 'TextField_12468',
        '备件申请RSN': 'TextField_12469',
        '备件申请CSN': 'TextField_12470',
        '备件申请物料号': 'TextField_12471',
        '备件申请数量': 'TextField_12472',
        '备件申请收货人': 'TextField_12473',
        '备件申请收货人公司': 'TextField_12474',
        '备件申请收货人电话': 'TextField_12475',
        '备件申请顺丰单号': 'TextField_12476',
        '备件申请状态': 'SelectField_7182',
        'case_number': 'TextField_12528',
        'case状态': 'SelectField_7183',
        'case标题': 'TextField_12478',
        'case邮箱': 'TextField_12479',
        'case创建时间': 'TextField_12480',
        'case最近更新时间': 'TextField_12481'
    }
    workorder_type_list = ['保修', '销售', '收费', '成本中心', '保修Q-info', 'NULL']
    assignment_state_list = ['已派遣', '已完成', '未处理', '已处理-无需派遣', '已处理-需派遣']
    parts_state_list = ['申请已收到', '申请处理中', '申请已完成', '申请已拒绝', '已提交']
    case_state_list = ['KUKA Takes Action', 'Customer Action Required', 'Closed', 'New', 'Invoicing']

    def get_open_api_token (self):
        url1 = 'https://kuka.s2.udesk.cn/open_api_v1/log_in'
        data = {
            'email': 'sunbing.yan@kuka.com',
            'password': 'hot4008208865'
        }
        # open_api_token = requests.post(url1, data=data).json()['open_api_auth_token']
        return 'd98f057b-6e44-4f49-b397-d3e23a3563af'

    def get_nonce (self):
        nonce = ''
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length = len(base_str) - 1
        for i in range(50):
            nonce += base_str[random.randint(0, length)]

        return nonce

    def get_url (self):
        open_api_token = self.get_open_api_token()
        email = 'sunbing.yan@kuka.com'
        timestamp = str(int(time.time()))
        nonce = self.get_nonce()
        sign_version = 'v2'
        flag = '&'
        pre_sign = email + flag + open_api_token + flag + timestamp + flag + nonce + flag + sign_version
        pre_sign = pre_sign.encode('utf-8')
        sign = hashlib.sha256(pre_sign).hexdigest()
        create_new_url = 'https://kuka.s2.udesk.cn/open_api_v1/tickets?email=sunbing.yan@kuka.com&timestamp=%(timestamp)s&sign=%(sign)s&nonce=%(nonce)s&sign_version=v2' % {
            "timestamp":timestamp, "sign":sign, "nonce":nonce}
        update_old_url = 'https://kuka.s2.udesk.cn/open_api_v1/tickets/(workorder_id)?email=sunbing.yan@kuka.com&timestamp=%(timestamp)s&sign=%(sign)s&nonce=%(nonce)s&sign_version=v2' % {
            "timestamp":timestamp, "sign":sign, "nonce":nonce}
        create_new_customer_url = 'https://kuka.s2.udesk.cn/open_api_v1/customers?email=sunbing.yan@kuka.com&timestamp=%(timestamp)s&sign=%(sign)s&nonce=%(nonce)s&sign_version=v2' % {
            "timestamp":timestamp, "sign":sign, "nonce":nonce}
        customer_list_url = 'https://kuka.s2.udesk.cn/open_api_v1/customers?email=sunbing.yan@kuka.com&timestamp=%(timestamp)s&sign=%(sign)s&nonce=%(nonce)s&sign_version=v2' % {
            "timestamp": timestamp, "sign": sign, "nonce": nonce}
        return create_new_url, update_old_url, create_new_customer_url,customer_list_url

    def create_new_customer (self, insert_dict, workorder_type):
        # 构造不同data
        url = self.get_url()[2]
        if workorder_type == 'parts' or workorder_type == 'assignment':
            data = {
                "customer": {
                    "nick_name": insert_dict['customer_name'],
                    "cellphones": [[None, insert_dict['customer_phone']]],
                    "custom_fields": {
                        "TextField_4094": insert_dict['customer_company']
                    }
                }
            }
        else:
            data = {}
        page_json = requests.post(url=url, json=data).json()
        print(workorder_type,page_json)
        return page_json['code']

    def udesk_post(self,insert_update_flag, insert_dict, workorder_type,workorder_id =None):
        time.sleep(1.5)
        wait_flag = 0
        rollback_flag = 0
        continue_flag = 0
        new_workorder_id = None
        try:
            new_workorder_id, rollback_flag, continue_flag = self.post(insert_update_flag, insert_dict, workorder_type,workorder_id=workorder_id)
        except requests.exceptions.ConnectionError as e:
            print('服务器无响应，正在尝试重新执行')
            rollback_flag = 1
        return new_workorder_id, rollback_flag, continue_flag,wait_flag

    def post (self, insert_update_flag, insert_dict, workorder_type,workorder_id = None):
        create_new_url, update_old_url, create_new_customer_url,x = self.get_url()
        new_workorder_id = None
        rollback_flag = 0
        continue_flag = 0
        # 创建或更新备件工单
        if workorder_type == 'parts':
            # 创建备件工单
            if insert_update_flag == 'insert':
                # 构造创建工单data
                data = \
                {"ticket":
                    {
                        "subject": "备件申请-%s-%s-%s" % (
                            insert_dict['proposer'], insert_dict['customer_company'], insert_dict['an']),
                        "content": "备件申请-%s-%s-%s" % (
                            insert_dict['proposer'], insert_dict['customer_company'], insert_dict['an']),
                        "template_id": 28210,
                        "type": 'cellphone',
                        "type_content": insert_dict['customer_phone'],
                        "ticket_field":
                        {
                            f"{self.udesk_dict['项目号']}": insert_dict['order1'],
                            f"{self.udesk_dict['parts_ID']}": str(insert_dict['parts_id']),
                            f"{self.udesk_dict['备件申请人']}": insert_dict['proposer'],
                            f"{self.udesk_dict['备件申请RSN']}": insert_dict['rsn'],
                            f"{self.udesk_dict['备件申请CSN']}": insert_dict['csn'],
                            f"{self.udesk_dict['备件申请物料号']}": insert_dict['an'],
                            f"{self.udesk_dict['备件申请数量']}": insert_dict['quantity'],
                            f"{self.udesk_dict['备件申请收货人']}": insert_dict['customer_name'],
                            f"{self.udesk_dict['备件申请收货人公司']}": insert_dict['customer_company'],
                            f"{self.udesk_dict['备件申请收货人电话']}": insert_dict['customer_phone'],
                            f"{self.udesk_dict['备件申请状态']}": str(
                                self.parts_state_list.index(insert_dict['order_state'])),
                            f"{self.udesk_dict['备件申请顺丰单号']}": insert_dict['sf_info']
                        }
                    }
                }
                # 每分钟最多请求60次
                page_json = requests.post(url=create_new_url, json=data).json()
                print(workorder_type,page_json)
                # 如果请求成功,则返回码为1000
                if page_json['code'] == 1000:
                    # 解析到新生成的工单id
                    new_workorder_id = page_json['ticket_id']

                # 如果没有请求成功
                else:
                    # 创建新客户
                    create_new_customer_code = self.create_new_customer(insert_dict, workorder_type)
                    # 如果成功，回调flag置1
                    if create_new_customer_code == 1000:
                        rollback_flag = 1
                    else:
                        continue_flag = 1
            # 更新备件工单
            elif insert_update_flag == 'update':
                update_old_url = update_old_url.replace('(workorder_id)',str(workorder_id))
                data = \
                {"ticket":
                    {
                        "subject": "备件申请-%s-%s-%s" % (insert_dict['proposer'], insert_dict['customer_company'], insert_dict['an']),
                        "custom_fields":
                            {
                                f"{self.udesk_dict['项目号']}": insert_dict['order1'],
                                f"{self.udesk_dict['parts_ID']}": str(insert_dict['parts_id']),
                                f"{self.udesk_dict['备件申请人']}": insert_dict['proposer'],
                                f"{self.udesk_dict['备件申请RSN']}": insert_dict['rsn'],
                                f"{self.udesk_dict['备件申请CSN']}": insert_dict['csn'],
                                f"{self.udesk_dict['备件申请物料号']}": insert_dict['an'],
                                f"{self.udesk_dict['备件申请数量']}": insert_dict['quantity'],
                                f"{self.udesk_dict['备件申请收货人']}": insert_dict['customer_name'],
                                f"{self.udesk_dict['备件申请收货人公司']}": insert_dict['customer_company'],
                                f"{self.udesk_dict['备件申请收货人电话']}": insert_dict['customer_phone'],
                                f"{self.udesk_dict['备件申请状态']}": str(
                                    self.parts_state_list.index(insert_dict['order_state'])),
                                f"{self.udesk_dict['备件申请顺丰单号']}": insert_dict['sf_info']
                            }
                    }
                }
                page_json = requests.put(update_old_url,json=data).json()
                response_code = page_json['code']
                new_workorder_id = page_json['ticket']['id']
                if response_code != 1000:
                    continue_flag = 1

        # 创建或更新派遣工单
        elif workorder_type == 'assignment':
            # 创建派遣工单
            if insert_update_flag == 'insert':
                # 构造创建工单data
                data = \
                {"ticket":
                    {
                        "subject": "派遣服务-%s-%s-%s" % (
                            insert_dict['engineer1'], insert_dict['customer_company'], insert_dict['service_content']),
                        "content": "派遣服务-%s-%s-%s" % (
                            insert_dict['engineer1'], insert_dict['customer_company'], insert_dict['service_content']),
                        "template_id": 28209,
                        "type": 'cellphone',
                        "type_content": insert_dict['customer_phone'],
                        "ticket_field":
                        {
                            f"{self.udesk_dict['项目号']}": insert_dict['order1'],
                            f"{self.udesk_dict['附加项目号']}": insert_dict['order2'],
                            f"{self.udesk_dict['项目类别']}": str(self.workorder_type_list.index(insert_dict['order_type'])),
                            f"{self.udesk_dict['assignment_ID']}": insert_dict['assignment_ID'],
                            f"{self.udesk_dict['派遣序列号1']}": insert_dict['serial1'],
                            f"{self.udesk_dict['派遣序列号2']}": insert_dict['serial2'],
                            f"{self.udesk_dict['派遣序列号3']}": insert_dict['serial3'],
                            f"{self.udesk_dict['派遣序列号4']}": insert_dict['serial4'],
                            f"{self.udesk_dict['派遣序列号5']}": insert_dict['serial5'],
                            f"{self.udesk_dict['派遣序列号6']}": insert_dict['serial6'],
                            f"{self.udesk_dict['派遣联系人']}": insert_dict['customer_name'],
                            f"{self.udesk_dict['派遣联系人电话']}": insert_dict['customer_phone'],
                            f"{self.udesk_dict['派遣联系人电话2']}": insert_dict['customer_phone2'],
                            f"{self.udesk_dict['派遣联系人邮箱']}": insert_dict['customer_email'],
                            f"{self.udesk_dict['派遣联系人公司']}": insert_dict['customer_company'],
                            f"{self.udesk_dict['派遣联系人地址']}": insert_dict['customer_address'],
                            f"{self.udesk_dict['派遣服务内容']}": insert_dict['service_content'],
                            f"{self.udesk_dict['派遣工程师1']}": insert_dict['engineer1'],
                            f"{self.udesk_dict['派遣工程师2']}": insert_dict['engineer2'],
                            f"{self.udesk_dict['派遣项目状态']}": str(self.assignment_state_list.index(insert_dict['order_state'])),
                            f"{self.udesk_dict['派遣开始日期']}": insert_dict['start_time'],
                            f"{self.udesk_dict['派遣结束日期']}": insert_dict['end_time'],
                            f"{self.udesk_dict['派遣创建时间']}": insert_dict['open_time'],
                            f"{self.udesk_dict['派遣计划服务时长']}": insert_dict['normal_hours']
                        }
                    }
                }
                page_json = requests.post(url=create_new_url, json=data).json()
                print(workorder_type,page_json)
                # 如果请求成功,则返回码为1000
                if page_json['code'] == 1000:
                    # 解析到新生成的工单id
                    new_workorder_id = page_json['ticket_id']

                # 如果没有请求成功
                else:
                    # 创建新客户
                    create_new_customer_code = self.create_new_customer(insert_dict, workorder_type)
                    # 如果成功，回调flag置1
                    if create_new_customer_code == 1000:
                        rollback_flag = 1
                    else:
                        continue_flag = 1

            # 更新派遣工单
            elif insert_update_flag == 'update':
                update_old_url = update_old_url.replace('(workorder_id)', str(workorder_id))
                data = \
                    {"ticket":
                        {"subject": "派遣服务-%s-%s-%s" % (
                        insert_dict['engineer1'], insert_dict['customer_company'], insert_dict['service_content']),
                        "custom_fields":
                            {
                                f"{self.udesk_dict['项目号']}": insert_dict['order1'],
                                f"{self.udesk_dict['附加项目号']}": insert_dict['order2'],
                                f"{self.udesk_dict['项目类别']}": str(self.workorder_type_list.index(insert_dict['order_type'])),
                                f"{self.udesk_dict['assignment_ID']}": insert_dict['assignment_ID'],
                                f"{self.udesk_dict['派遣序列号1']}": insert_dict['serial1'],
                                f"{self.udesk_dict['派遣序列号2']}": insert_dict['serial2'],
                                f"{self.udesk_dict['派遣序列号3']}": insert_dict['serial3'],
                                f"{self.udesk_dict['派遣序列号4']}": insert_dict['serial4'],
                                f"{self.udesk_dict['派遣序列号5']}": insert_dict['serial5'],
                                f"{self.udesk_dict['派遣序列号6']}": insert_dict['serial6'],
                                f"{self.udesk_dict['派遣联系人']}": insert_dict['customer_name'],
                                f"{self.udesk_dict['派遣联系人电话']}": insert_dict['customer_phone'],
                                f"{self.udesk_dict['派遣联系人电话2']}": insert_dict['customer_phone2'],
                                f"{self.udesk_dict['派遣联系人邮箱']}": insert_dict['customer_email'],
                                f"{self.udesk_dict['派遣联系人公司']}": insert_dict['customer_company'],
                                f"{self.udesk_dict['派遣联系人地址']}": insert_dict['customer_address'],
                                f"{self.udesk_dict['派遣服务内容']}": insert_dict['service_content'],
                                f"{self.udesk_dict['派遣工程师1']}": insert_dict['engineer1'],
                                f"{self.udesk_dict['派遣工程师2']}": insert_dict['engineer2'],
                                f"{self.udesk_dict['派遣项目状态']}": str(self.assignment_state_list.index(insert_dict['order_state'])),
                                f"{self.udesk_dict['派遣开始日期']}": insert_dict['start_time'],
                                f"{self.udesk_dict['派遣结束日期']}": insert_dict['end_time'],
                                f"{self.udesk_dict['派遣创建时间']}": insert_dict['open_time'][:-3],
                                f"{self.udesk_dict['派遣计划服务时长']}": insert_dict['normal_hours']
                            }
                        }
                    }
                page_json = requests.put(update_old_url, json=data).json()
                print(workorder_type,page_json)
                response_code = page_json['code']
                if response_code != 1000:
                    continue_flag = 1
                else:
                    new_workorder_id = page_json['ticket']['id']
        # 创建或更新case工单
        elif workorder_type == 'salesforce':
            # 创建case工单
            if insert_update_flag == 'insert':
                # 构造创建工单data
                data = \
                    {"ticket":
                        {
                            "subject": "CASE-%s-%s-%s" % (
                                insert_dict['case_responsible'], insert_dict['case_number'], insert_dict['subject']),
                            "content": "备件申请-%s-%s-%s" % (
                                insert_dict['case_responsible'], insert_dict['case_number'], insert_dict['subject']),
                            "template_id": 28211,
                            "ticket_field":
                                {
                                    f"{self.udesk_dict['case_number']}": str(insert_dict['case_number']),
                                    f"{self.udesk_dict['case标题']}": insert_dict['subject'],
                                    f"{self.udesk_dict['case邮箱']}": insert_dict['web_email'],
                                    f"{self.udesk_dict['case创建时间']}": insert_dict['open_date'],
                                    f"{self.udesk_dict['case最近更新时间']}": insert_dict['modified_date'],
                                    f"{self.udesk_dict['case状态']}": str(
                                        self.case_state_list.index(insert_dict['status'])),
                                }
                        }
                    }
                # 每分钟最多请求60次
                page_json = requests.post(url=create_new_url, json=data).json()
                print(workorder_type,page_json)
                # 如果请求成功,则返回码为1000
                if page_json['code'] == 1000:
                    # 解析到新生成的工单id
                    new_workorder_id = page_json['ticket_id']

                # 更新case工单
            elif insert_update_flag == 'update':
                update_old_url = update_old_url.replace('(workorder_id)', str(workorder_id))
                data = \
                    {"ticket":
                        {
                            "subject": "CASE-%s-%s-%s" % (
                            insert_dict['case_responsible'], insert_dict['case_number'], insert_dict['subject']),
                            "custom_fields":
                                {
                                    f"{self.udesk_dict['case_number']}": str(insert_dict['case_number']),
                                    f"{self.udesk_dict['case标题']}": insert_dict['subject'],
                                    f"{self.udesk_dict['case邮箱']}": insert_dict['web_email'],
                                    f"{self.udesk_dict['case创建时间']}": insert_dict['open_date'],
                                    f"{self.udesk_dict['case最近更新时间']}": insert_dict['modified_date'],
                                    f"{self.udesk_dict['case状态']}": str(
                                    self.case_state_list.index(insert_dict['status'])),
                                }
                        }
                    }
                page_json = requests.put(update_old_url, json=data).json()
                response_code = page_json['code']
                new_workorder_id = page_json['ticket']['id']
                if response_code != 1000:
                    continue_flag = 1
        elif workorder_type == 'case_update':
            if insert_update_flag == 'insert':
                # 构造创建工单data
                data = \
                    {"ticket":
                        {
                            "subject": "CASE-%s-%s-%s" % (
                                insert_dict['case_responsible'], insert_dict['case_number'], insert_dict['subject']),
                            "content": "备件申请-%s-%s-%s" % (
                                insert_dict['case_responsible'], insert_dict['case_number'], insert_dict['subject']),
                            "template_id": 28211,
                            "type": 'customer_id',
                            "type_content": insert_dict['customer_ID'],
                            "ticket_field":
                                {
                                    f"{self.udesk_dict['case_number']}": str(insert_dict['case_number']),
                                    f"{self.udesk_dict['case标题']}": insert_dict['subject'],
                                    f"{self.udesk_dict['case邮箱']}": insert_dict['web_email'],
                                    f"{self.udesk_dict['case创建时间']}": insert_dict['open_date'],
                                    f"{self.udesk_dict['case最近更新时间']}": insert_dict['modified_date'],
                                    f"{self.udesk_dict['case状态']}": str(
                                        self.case_state_list.index(insert_dict['status'])),
                                }
                        }
                    }
                page_json = requests.post(url=create_new_url, json=data).json()
                print(workorder_type,page_json)
                if page_json['code'] == 1000:
                    # 解析到新生成的工单id
                    new_workorder_id = page_json['ticket_id']

        return new_workorder_id, rollback_flag, continue_flag

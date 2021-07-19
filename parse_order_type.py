def parse_order_type(order1, order2='xxxxxxx'):
    order_type1 = 'NULL'
    order1 = order1.strip()
    order2 = order2.strip()

    # 未处理,重复或取消申请
    if order1 == 'NULL' or order1 == '重复申请' or order1 == 'NA' or order1 == '取消申请':
        order_type1 = 'NULL'

    # order是保修类
    if order1[0:2] == '51':
        order_type1 = '保修'

    # order是收费类
    if order1[0:2] == '50' or order1[0:4] == '8300' or order1[0:2] == 'SM' or order1[0:2] == '52':
        order_type1 = '收费'

    # order是成本中心
    if order1[-1] == 'T' or order1[-1] == 't':
        order_type1 = '成本中心'

    # order是销售
    if order1[0:3] == 'VCN' or order1[0:3] == 'vcn' or order1[0:4] == '3195' or order1[0:4] == '8031' or order2[-1] == 'T':
        order_type1 = '销售'

    # order是Q-info
    if order2[0] == 'Q' or order2[0] == 'q':
        order_type1 = '保修Q-info'

    return order_type1

import pymysql
from post import Udesk

class Sql:
    def __init__(self,db):
        self.udesk = Udesk()
        self.db = db
        self.cursor = self.db.cursor()

    def sub_sql(self,sql_list):
        global insert_update_flag
        insert_flag = 0
        update_flag = 0
        continue_flag = 0
        wait_flag = 0
        new_workorder_id = 0
        for i in range(3):
            if ":\\" in sql_list[i] or "''" in sql_list[i]:
                sql_list[i] = sql_list[i].replace(":\\" , ' ')
                sql_list[i] = sql_list[i].replace("''" , "'")

        insert_sql = sql_list[0]
        update_sql = sql_list[1]
        select_sql = sql_list[2]
        insert_dict = sql_list[3]
        if len(sql_list[3]) == 27:
            workorder_type = 'assignment'
        elif len(sql_list[3]) == 12:
            workorder_type = 'parts'
        elif len(sql_list[3]) == 7:
            workorder_type = 'salesforce'
        elif len(sql_list[3]) == 8:
            workorder_type = 'case_update'
        else:
            workorder_type = None

        if workorder_type != 'case_update':
            # 先查询数据库里有无此条记录
            self.cursor.execute(select_sql)
            workorder_id_result = self.cursor.fetchone()
            if workorder_id_result:
                workorder_id = workorder_id_result[0]
            else:
                workorder_id = 0
        else:
            workorder_id = 0
        # 如果数据库里没有，则udesk也没有，post给udesk生成工单，返回工单ID
        if not workorder_id:
            insert_update_flag = 'insert'
            new_workorder_id,rollback_flag,continue_flag,wait_flag = self.udesk.udesk_post(insert_update_flag,insert_dict,workorder_type)
            # 如果出现错误，则重新执行
            while rollback_flag:
                new_workorder_id, rollback_flag, continue_flag,wait_flag = self.udesk.udesk_post(insert_update_flag, insert_dict, workorder_type)
            if workorder_type != 'case_update':
                insert_sql = insert_sql % new_workorder_id
                # 携带workorder_id，插入数据库
                try:

                    insert_flag = self.cursor.execute(insert_sql)
                    self.db.commit()
                except pymysql.err.ProgrammingError as e:
                    print(e,insert_sql)
            else:
                update_sql = update_sql % (new_workorder_id,new_workorder_id)
                try:
                    insert_flag = self.cursor.execute(update_sql)
                    self.db.commit()
                except pymysql.err.ProgrammingError as e:
                    print(e,update_sql)
            # 如果数据库里有，获取数据库内workorder_id,构造update_sql,更新数据库，如果数据库有更新，则更新udesk
        else:
            insert_update_flag = 'update'
            update_sql = update_sql % workorder_id
            try:
                update_flag = self.cursor.execute(update_sql)
                self.db.commit()
            except pymysql.err.ProgrammingError as e:
                print(e,update_sql)

            # 如果更新成功，说明数据有变化，这时再更新udesk
            if update_flag:
                new_workorder_id,rollback_flag,continue_flag,wait_flag = self.udesk.udesk_post(insert_update_flag,insert_dict,workorder_type,workorder_id = workorder_id)
                # 如果出现错误，则重新执行
                while rollback_flag:
                    new_workorder_id, rollback_flag, continue_flag,wait_flag = self.udesk.udesk_post(insert_update_flag, insert_dict, workorder_type,workorder_id=workorder_id)

                update_flag = 1

        if insert_flag:
            print(new_workorder_id,'新工单已创建')
        elif update_flag:
            print(workorder_id,'工单已更新')
        else:
            print(workorder_id,'工单未更新')

        return continue_flag,wait_flag

from salesforce import Salesforce
from parts import Parts
from assignment import Assignment
from customer_refresh import customer_refresh
from salesforce import first_landing
from selenium import webdriver
from time import sleep
import json
import pymysql



fp = open("./config.json",'r')
config = json.load(fp)
mysql_config = config['mysql']
salesforce_config = config['salesforce']
parts_config = config['parts']
assignment_config = config['assignment']
fp.close()

db = pymysql.connect(mysql_config['ip'],mysql_config['user'], mysql_config['password'], mysql_config['database'])
print('数据库已打开')

new_bro = webdriver.Chrome(executable_path=salesforce_config['path'])
print('浏览器已打开')

if salesforce_config['enable']:
    salesforce = Salesforce(db,first_landing(new_bro,salesforce_config),salesforce_config)
if parts_config['enable']:
    parts = Parts(db,parts_config)
if assignment_config['enable']:
    assignment = Assignment(db,assignment_config)

while True:
	if salesforce_config['enable']:
		try:
			customer_refresh(db)
		except BaseException as error1:
			print("刷新客户时出错。")
			print(error1)
			
	if salesforce_config['enable']:
		try:
			salesforce.main_def()
		except BaseException as error2:
			print("salesforce出错")
			print(error2)

	if assignment_config['enable']:
		#try:
		assignment.main_def()
		#except BaseException as error3:
		#	print("assignment出错")
		#	print(error3)

	if parts_config['enable']:
		try:
			parts.main_def()
		except BaseException as error4:
			print("parts出错")
			print(error4)
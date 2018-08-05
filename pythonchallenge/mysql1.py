# 导入MySQL驱动
import pymysql
#注意把password设为你的root口令：
conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db='test',charset='utf8')
cursor = conn.cursor()

#创建user表：
cursor.execute('drop table if exists user')
cursor.execute('create table user (id varchar(20) primary key,name varchar(20))')
cursor.execute('insert into user (id,name) values(%s,%s)',('1','Michael'))
print('受影响行数：%d'% cursor.rowcount)

#提交事务：
conn.commit()
cursor.close()

#运行查询：
cursor = conn.cursor()
cursor.execute('select * from user where id=%s','1')
values = cursor.fetchall()
print('查询结果：%s' % values)

cursor.close()
conn.close()
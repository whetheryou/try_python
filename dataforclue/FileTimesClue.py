# coding=utf-8
'''
Created on 2017-02-17

@author: LuDan
'''
from util import MySQLUtil
import datetime
from dateutil.relativedelta import relativedelta
from algorithm import Employees

def queryLogonTime(employees):    #查询并统计每个离职员工每个月、各时间段（以小时为单位）、复制文件的次数
    db=MySQLUtil.ITDB()
    resultlist=[] #最后要输出的结果
    for i in range(len(employees)): #对于每一个离职员工
        employee=employees[i][0] #提取员工名
        leavetime=employees[i][1]+relativedelta(days=1) #各职员离职时间（最末时间）
        stime=datetime.datetime.strptime('2010-01-01','%Y-%m-%d').date() #定义起始时间
        while stime<=leavetime: #在职期间
            etime=stime+relativedelta(months=1) #每次只统计一个月
            sql="SELECT date_format(date,'%H') as a,substring_index(filename,'.',-1),count(substring_index(filename,'.',-1)) FROM threat_4_2.threat_action_file where user='"+employee+"' and date>='"+stime.strftime('%Y-%m-%d')+"' and date<'"+etime.strftime('%Y-%m-%d')+"' group by a,substring_index(filename,'.',-1) order by a ;"
            result=db.querytl(sql) #统计结果为：一个月内，每小时，复制各个文件的次数
            for j in range(len(result)):
                resultlist.append((employee,stime.strftime('%Y-%m-%d'),result[j][0],result[j][1],result[j][2]))
                #append是指添加一行到末尾，添加到结果里的为：（用户，计数月份初始日，几点（时），PC名，登入次数）
            stime=etime #继续统计下个月
        #print i,employee
    return resultlist #返回结果
     
if __name__ == '__main__':
    employees=Employees.queryLeaveEmployees() #统计离职员工名单
    resultlist=queryLogonTime(employees) #得到统计（用户名，计数月份初始日，几点（时），PC名，登入次数），即每人每月在某点登入各PC的次数
    #print resultlist 
    db=MySQLUtil.ITDB() #写入表格
    db.inserttl("insert into threat_4_2.threat_clue_file_times (employee_id,date,hour,filetype,times) values (%s,%s,%s,%s,%s);", resultlist)

        

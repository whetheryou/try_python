# coding=utf-8
'''
Created on 2017-02-17

@author: LuDan
'''
from util import MySQLUtil
import datetime
import numpy
from dateutil.relativedelta import relativedelta
from algorithm import Employees
from algorithm import NormalDistributionTest

def queryLogonTime(employees):    #查询并统计每个离职员工每个月、各时间段（以小时为单位）、复制文件的次数
    db=MySQLUtil.ITDB()
    resultlist=[] #最后要输出的结果
    for i in range(len(employees)): #对于每一个离职员工
        employee=employees[i][0] #提取员工名
        leavetime=employees[i][1]+relativedelta(days=1) #各职员离职时间（最末时间）
        stime=datetime.datetime.strptime('2010-01-01','%Y-%m-%d').date() #定义起始时间
        while stime<=leavetime: #在职期间
            etime=stime+relativedelta(months=1) #每次只统计一个月
            sql="SELECT date_format(date,'%H') as a,filename,count(filename) FROM threat_4_2.threat_action_file where user='"+employee+"' and date>='"+stime.strftime('%Y-%m-%d')+"' and date<'"+etime.strftime('%Y-%m-%d')+"' group by a,filename order by a ;"
            result=db.querytl(sql) #统计结果为：一个月内，每小时，复制各个文件的次数
            for j in range(len(result)):
                resultlist.append((employee,stime.strftime('%Y-%m-%d'),result[j][0],result[j][1],result[j][2]))
                #append是指添加一行到末尾，添加到结果里的为：（用户，计数月份初始日，几点（时），PC名，登入次数）
            stime=etime #继续统计下个月
        #print i,employee
    return resultlist #返回结果

def countLogonTimes(Logtype):   #在已经得到threat_clue_logon_times表格的基础上，统计工作/非工作时间的登录次数
    db=MySQLUtil.ITDB()
    sql=""
    if Logtype==1:  #统计非工作时间登录次数
        sql="SELECT employee_id,date_format(date,'%Y-%m'),sum(times) FROM threat_4_2.threat_clue_file_1_times where hour<9 or hour>17 group by employee_id,date;"
    elif Logtype==2:  #统计工作时间登录次数
        sql="SELECT employee_id,date_format(date,'%Y-%m'),sum(times) FROM threat_4_2.threat_clue_file_1_times where hour>=9 and hour<=17 group by employee_id,date;"
    elif Logtype==3:  #统计总登录次数
        sql="SELECT employee_id,date_format(date,'%Y-%m'),sum(times) FROM threat_4_2.threat_clue_file_1_times group by employee_id,date;"
    result=db.querytl(sql) #输出：用户名，计数月份，一月总次数
    resultDict={}
    tempemployee=result[0][0] #第一个用户名
    emLogonTimes={}
    employee=''
    for i in range(len(result)):
        employee=result[i][0]
        date=result[i][1]
        count=result[i][2]
        if employee==tempemployee: #当跟前一个姓名是同一个人时，建立字典{日期1：次数1，日期2：次数2....}
            emLogonTimes[date]=count #字典
        else: #换到第二个人时
            #emLogonTimes1=sorted(emLogonTimes.iteritems(),key=lambda d:d[0])
            resultDict[tempemployee]=emLogonTimes #将整体的数据写入另外一个字典，写为：{员工名1：{日期1：次数1，日期2：次数2....}}
            emLogonTimes={} #初始化
            emLogonTimes[date]=count #写入字典
        tempemployee=employee #一个一个姓名的轮
        
    #emLogonTimes1=sorted(emLogonTimes.iteritems(),key=lambda d:d[0])
    resultDict[employee]=emLogonTimes # 写入最后一员工记录
    return resultDict
    #最后得到的为相嵌字典{员工名1：{日期1：次数1，日期2：次数2....}，员工名2：{日期1：次数1，日期2：次数2....}，....}

def saveAbnormalLogonClue(employee,abnormalDatelist,LogType):   #将线索异常情况存入数据库
    db=MySQLUtil.ITDB()
    abnormalcluelist=[] #正常日期列表
    for i in range(len(abnormalDatelist)):
        sql=""
        if LogType==1: #非工作时间登入的人员
            sql="SELECT id FROM threat_4_2.threat_clue_logon_times where employee_id='"+employee+"' and date_format(date,'%Y-%m')='"+abnormalDatelist[i]+"' and (hour<7 or hour>16);"
        elif LogType==2: #工作时间
            sql="SELECT id FROM threat_4_2.threat_clue_logon_times where employee_id='"+employee+"' and date_format(date,'%Y-%m')='"+abnormalDatelist[i]+"' and hour>=7 and hour<=16;"
        elif LogType==3: #总时间
            sql="SELECT id FROM threat_4_2.threat_clue_logon_times where employee_id='"+employee+"' and date_format(date,'%Y-%m')='"+abnormalDatelist[i]+"';"
        result=db.querytl(sql)
        #输出结果为：id号，自动生成的？
        for j in range(len(result)): #1代表,'线索ID, 对应threat_system_clue_conf表中clue_id值',
            rrr = numpy.array(result[j])
            abnormalcluelist.append((employee,1,'threat_clue_logon_times',rrr[0]))
            #输出结果为：（员工，1，'threat_clue_logon_times'，id号码）
    db.inserttl("insert into threat_4_2.threat_abnormal_file_1 (employee_id,clue_id,table_name,table_id) values (%s,%s,%s,%s);", abnormalcluelist)
                                        #写入threat_abnormal_clue表，内容：（员工，1，表格名，表格里对应id）

if __name__ == '__main__':
    employees=Employees.queryLeaveEmployees() #统计离职员工名单
    resultlist=queryLogonTime(employees) #得到统计（用户名，计数月份初始日，几点（时），PC名，登入次数），即每人每月在某点登入各PC的次数
    print resultlist 
    #db=MySQLUtil.ITDB() #写入表格
    #db.inserttl("insert into threat_4_2.threat_clue_file_1_times (employee_id,date,hour,filename,times) values (%s,%s,%s,%s,%s);", resultlist)
    #LogType=2  #1是非工作时间，2是工作时间，3是总时间
    #resultDict=countLogonTimes(LogType) #{员工名1：{日期1：次数1，日期2：次数2....}，员工名2：{日期1：次数1，日期2：次数2....}，....}
    #print resultDict
    
    #for k in resultDict: #k为字典中的键，即为人员代号
    #   abnormalDatelist=NormalDistributionTest.NormalDistTest(k, resultDict[k]) #正态分布检测用户
        #print k,abnormalDatelist
        #if len(abnormalDatelist)>0:
         #   saveAbnormalLogonClue(k, abnormalDatelist,LogType)
        

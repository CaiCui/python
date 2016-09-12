'''
程序思路;
前期工作:先用抓实时sn.py抓今天的实时车辆(粗略)存入数据库，再用下面代码跑，理论上可以减轻错误的抓取
本程序执行的工作：
首先在main()中利用本机ip声明一个AfcCrawler()对象，用于执行一次登陆获取该次的cookies，
然后进入数据库将每个线程要处理的数据段取出放入列表，然后开始设置十个线程，分别挂10个代理，这十个线程的work()执行的是
通过AfcCrawler()中的get_cookies_content()方法获取每个线程对应的list中的info内容，存入到返回list中，所有
的页面都存入后再统一调用页面解析函数getHtmlContent()，将每个线程处理的列表统一插入数据库，即一次登陆，
共享cookies，同时处理，统一写入数据库。
部分优化:gps位置请求去掉，等数据抓完再处理，优先多线程网络请求
测试结果：
10线程:测试每个线程800个数据，总是在7600左右卡住，第一次跑了1个小时，带写入文件
单线程：分配800个数据，运行4分钟
5线程：分配4000个数据，运行10分钟
待解决的问题：
越往后速度越慢，代理服务器占有一定原因。。。
开启10个线程的时候平均速度最快，平均可以1分钟1200个页面抓取。因为发现有的代理可能好，请求访问速度极快。
由于是动态数据，所以第一次利用抓实时sn.py抓取的页面可能在爬取得过程中丢失，也会造成访问该页面一直请求不到访问过慢，大大降低执行效率
本程序当作一次学习实践，还有不足，以后改进
2016-08-08 made by cuiyifeng
'''
# -*- coding: utf-8 -*-
import urllib2
import urllib
import cookielib
import re
from bs4 import BeautifulSoup
import requests
import json
from threading import Thread,Lock,stack_size
from Queue import Queue
import time
import MySQLdb
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )
stack_size(32768*16)#设定线程的栈大小,防止内存崩溃
global login_url
login_url="http://xx.xx.xx.xxx/users/sign_in"
global pro //代理设置
pro={
    '967790010448':{
            'http': 'http://183.245.147.24:80',
            'https': 'https://183.245.147.24:80',
        },
    '967790129595':{
            'http': 'http://111.11.122.7:80',
            'https': 'https://111.11.122.7:80',
    },
    '967790133688':{'http': 'http://111.13.136.36:80',
            'https': 'https://111.13.136.36:80',},
    '967790137813':{'http': 'http://117.135.250.88:80',
            'https': 'https://117.135.250.88:80',},
    '967790141407':{'http': 'http://211.110.127.210:3128',
            'https': 'https://211.110.127.210:3128',},
    '967790146752':{'http': 'http://118.244.239.2:3128',
            'https': 'https://118.244.239.2:3128',},
    '967790203515':{'http': 'http://202.106.16.36:3128',
            'https': 'https://202.106.16.36:3128',},
    '967790208391':{'http': 'http://202.100.167.160:80',
            'https': 'https://202.100.167.160:80',},
    '967790211680':{'http': 'http://115.182.15.27:8080',
            'https': 'https://115.182.15.27:8080',},
    '967790217209':{'http': 'http://202.100.167.144:80',
            'https': 'https://202.100.167.144:80',}
}
global fnum
fnum=[]
##########################################################
class thread_op:#多线程操作类
    def __init__(self,threads,list,first_cookie):
        self.lock=Lock()
        self.q_req=Queue()#任务队列
        self.q_ans=Queue()#结果队列
        self.threads=threads
        self.snlist=list
        self.craw = first_cookie#使用第一次登陆的afc对象来操作
        for i in range(threads):#thread start
            t = Thread(target=self.threadget)
            t.setDaemon(True)
            t.start()
        self.running = 0

    def work(self,arg):#设置执行的AfcCrawler操作
        res = self.craw.get_cookies_content(self.snlist,arg)#利用同一个cookies访问
        v = self.craw.getHtmlContent(res)#v 将是解析后的列表，存储该session下2000多个所有的解析后车的信息
        return v

    def threadget(self):#Queue set
        while True:
            req = self.q_req.get()#取任务元素
            with self.lock:#保证任务队列取操作的原子性
                self.running+=1
            try:
                ans = self.work(req)
            except Exception,what:
                ans =''
                print what
            self.q_ans.put(ans)#任务结果进队，这里是抓取的页面...
            with self.lock:
                self.running-=1
            self.q_req.task_done()
            time.sleep(0.5)

    def __del__(self):#析构时等待两个队列执行完成
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def push(self,req):
        self.q_req.put(req)

    def pop(self):
        return self.q_ans.get()

    def taskleft(self):
        return self.q_req.qsize()+self.q_ans.qsize()+self.running

class AfcCrawler:
    def __init__(self):#
        #self.value = []
        self.cookie = {}
    def __del__(self):#
        #self.value=[]
        pass
    def get_cookies_content(self,biao,first): #创建一个新session，使用login1登录后的cookie,first是每2000个数据的第一个，biao就是snlist对应的字典key的value
        _session=requests.Session()
        _session.cookies.update(self.cookie)
        res=[]
        for i in biao[first]:
            str="http://xxxxxxxxxxxxx" + i + "/info"
            try:
                response=_session.get(str,proxies=pro[first]).text
                res.append(response)
                print i
            except requests.ConnectionError, e:
                #print ("ConnectionError: " + str(e))
                continue
            except requests.HTTPError, e:
                #print  ("HTTPError: " + str(e))
                continue
            except requests.ConnectTimeout, e:
                #print  ("TimeOutError: " + str(e))
                continue
        return res
    def getHtml(self,url):#模拟登陆+获取ACT页面内容
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36"
        headers = dict({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8",
            # "Cache-Control":"max-age=0",
            "Connection": "keep-alive",
            # "Content-Length":"187",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "xxx.xxx.xxx.xxx",
            "Referer": "http://xx.xx.xx.xx",
            "User-Agent": user_agent})
        session1 = requests.session()
        # 利用session来获取并存储请求的页面的cookie,否则先获取token,cookie会过期
        html = session1.get(url, headers=headers)
        # 利用带有Session的页面通过BeautifulSoup抓取token验证码
        '''
        常用异常
        except requests.ConnectionError,e:
            print ("ConnectionError: "+str(e))
        except requests.HTTPError,e:
            print  ("HTTPError: "+str(e))
        except requests.ConnectTimeout,e:
            print  ("TimeOutError: " + str(e))
       '''
        htmlDoc = BeautifulSoup(html.text, 'html.parser')
        token = htmlDoc.find_all('meta')[-1]['content']
        # 构造请求数据
        postdata = {"utf8": "✓",
                    "authenticity_token": token,
                    "user[username]": "abc",
                    "user[password]": "12345678",
                    "user[remember_me]": "0",
                    "commit": "登录"}
        try:
            sessioncommon=requests.Session()
            sessioncommon.cookies.update(html.cookies)
            response=sessioncommon.post(url=url, params=postdata, headers=headers)
            print (response)
            self.cookie = response.cookies
        except urllib2.HTTPError,e:
            print e.code,e.reason
        # 抓取登录后的页面
        #res = session.get("http://xx.xx.xx.xx"+sn+"/info").text
        #return res
    def get_reslist(self,session,sn):#sn是一个列表，用于爬取所有的同一个session下的页面
        res=[]
        for snn in sn:
           str =session.get("http://xx.xx.xx.xx" + snn + "/info").text
           res.append(str)
        return res
    def getGpsLoction(self,lat,lng):# 通过gpsApi的json数据请求地址信息,这一步可以省略，应为有gps坐标所以可以全部处理完再写一个查询位置的py来操作
        gps_headers = dict({
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Host": 'www.gpsspg.com',
            "Rerfer": "http://www.gpsspg.com/iframe/maps/baidu_160703.htm?mapi=1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        })
        gps_url = 'http://www.gpsspg.com/apis/maps/geo/?output=jsonp&lat=' + lat + '&lng=' + lng + '&type=0&callback=jQuery1102022599503531810905_1469696687375&_=1469696687376'
        str = requests.get(gps_url, headers=gps_headers).text
        str_json = json.loads(str[str.find('{'):str.rfind('}') + 1])
        loc = str_json['result'][0]['address']
        return loc
    def getHtmlContent(self,res):
        fin_value=[]
        for res_i in res:
            type = BeautifulSoup(res_i, 'html.parser')
            tabcontent = type.findAll('table')
            if(tabcontent):
                value=[]
                for tb in tabcontent:
                    for tr in tb.findAll('tr'):
                        for td in tr.findAll('td'):
                            try:
                                if (tb == tabcontent[2]):
                                    continue
                            except IndexError,e:
                                    continue
                            try:
                                if (tb == tabcontent[0] and tr == tb.findAll('tr')[2]):
                            #str = td.getText()
                            #strnum = str[str.find('(') + 1:str.rfind(')')].split(',')
                            #lat = strnum[1].strip()
                            #lng = strnum[0].strip()
                            #location=self.getGpsLoction(lat,lng)
                                    location='####'
                            except IndexError,e:
                                    continue
                            try:
                                if (tb == tabcontent[0] and tr == tb.findAll('tr')[4]):
                                    str = td.getText() + location+'\n'
                            #print str
                                    value.append(td.getText() + location)
                                else:
                            #print td.getText()
                                    value.append(td.getText())
                            except IndexError, e:
                                    continue
        fin_value.append(value)
        return fin_value#fin_str,value
class DataBase:
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host='localhost',user='myhost',passwd='123',db='test',port=3306,charset='utf8')
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    def __del__(self):
        self.cur.close()
        self.conn.close()
    def insert(self,value):
        try:
            self.cur = self.conn.cursor()
            p = self.cur.execute(
                'insert into afc_test(RecTime,CarType,Coordinates,Speed,Direction,GPS,RecTimeInfo,mileageID,SpeedInfo,Rev,Temperature,Air,APKV,Oil,TotalMiles,OilC1,OilC2,OilAve,Sn,City,Vin) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                value)
            self.conn.commit()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
    def search(self,idnum1,idnum2):
        try:
            self.cur = self.conn.cursor()
            if(idnum1==7200):
                idnum2=8116
            self.cur.execute('select sn from sn88 where id > '+str(idnum1)+' and id < '+str(idnum2))
            f = self.cur.fetchall()
            self.conn.commit()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        return f
    def insertMany(self,value):
        try:
            self.cur = self.conn.cursor()
            sql='insert into afc_carinfo(RecTime,CarType,Coordinates,Speed,Direction,GPS,RecTimeInfo,mileageID,SpeedInfo,Rev,Temperature,Air,APKV,Oil,TotalMiles,OilC1,OilC2,OilAve,Sn,City,Vin) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            #sql = 'insert into sntest(sn) values(%s)'
            p = self.cur.executemany(sql,value)
            self.conn.commit()
        except MySQLdb.Error, e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def main():
    #每一个代理的入口sn号
    sn = ['967790010448','967790129595','967790133688','967790137813','967790141407','967790146752','967790203515','967790208391','967790211680','967790217209']
    #sn = ['967790010448']
    #本机登陆，并保存cookies
    fisrt_login=AfcCrawler()
    fisrt_login.getHtml(login_url)
    #执行数据库逻辑

    data=DataBase()
    i=0
    while i< 7210:
        j=i+801
        f =data.search(i,j)
        vv=[]
        for m in f:
            vv.append(str(m[0]))
        fnum.append(vv)
        i=j-1
    #fnum=[['967790010448'],['967790129595'],['967790133688'],['967790137813'],['967790141407'],['967790146752'],['967790203515'],['967790208391'],['967790211680'],['967790217209']]
    snlis = {
            '967790010448': fnum[0],
            '967790129595': fnum[1],
            '967790133688': fnum[2],
            '967790137813': fnum[3],
            '967790141407': fnum[4],
            '967790146752': fnum[5],
            '967790203515': fnum[6],
            '967790208391': fnum[7],
            '967790211680': fnum[8],
            '967790217209': fnum[9],
        }#列表映射,key为该组session对象，后面列表为该session下爬取得页面sn组
    f = thread_op(10,snlis,fisrt_login)  # 设置线程数
    for snn in sn:
        f.push(snn)
    while f.taskleft():
       #content,dataval=f.pop()#返回结果
        res = f.pop()# 返回结果
        #t=fisrt_login.getHtmlContent(res)
        data.insertMany(res)  # 一次插入一个线程的处理结果[[],[],[]........[]]
       #fo.write(content)
       # close
       #print content
       #print dataval
if __name__=='__main__':
    main()







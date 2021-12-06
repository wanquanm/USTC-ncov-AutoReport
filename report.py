# encoding=utf8
import requests
import json
import time
import datetime
import pytz
import re
import sys
import argparse
import PIL
import io
from datetime import datetime, timedelta
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from bs4 import BeautifulSoup

class Report(object):
    def __init__(self, stuid, password, data_path):
        self.stuid = stuid
        self.password = password
        self.data_path = data_path

    def report(self):
        loginsuccess = False
        retrycount = 2
        while (not loginsuccess) and retrycount:
            session = self.login()
            cookies = session.cookies
            getform = session.get("https://weixine.ustc.edu.cn/2020")
            print(getform.url)
            retrycount = retrycount - 1
            if getform.url != "https://weixine.ustc.edu.cn/2020/home":
                print("Login Failed! Retrying...")
            else:
                print("Login Successful!")
                loginsuccess = True
        if not loginsuccess:
            return False
        
        data = getform.text
        data = data.encode('ascii','ignore').decode('utf-8','ignore')
        soup = BeautifulSoup(data, 'html.parser')
        token = soup.find("input", {"name": "_token"})['value']

        
        today = datetime.now().weekday() + 1
        if(today == 1):
            data1 = dict(
                _token=token,
                start_date=datetime.now().strftime('%Y-%m-%d'),
                end_date=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            )

            header1 = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cache-control': 'max-age=0',
                'content-length': '480',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://weixine.ustc.edu.cn',
                'referer': 'https://weixine.ustc.edu.cn/2020/apply/daliy',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1'
            }

            url1 = "https://weixine.ustc.edu.cn/2020/apply/daliy/post"
            resp1=session.post(url1, data=data1, headers=header1)
            print(resp1.status_code)
            if resp1.status_code != 200:
                print("error")
            else:
                print("Weekly report success")
        else:
            print("Not today for weekly report")
                      
        with open(self.data_path, "r+") as f:
            data = f.read()
            data = json.loads(data)
            data["_token"]=token

        headers = {
            'authority': 'weixine.ustc.edu.cn',
            'origin': 'https://weixine.ustc.edu.cn',
            'upgrade-insecure-requests': '1',
            'content-type': 'application/x-www-form-urlencoded',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'referer': 'https://weixine.ustc.edu.cn/2020/home',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Connection': 'close',
            'cookie': "PHPSESSID=" + cookies.get("PHPSESSID") + ";XSRF-TOKEN=" + cookies.get("XSRF-TOKEN") + ";laravel_session="+cookies.get("laravel_session"),
        }

        url = "https://weixine.ustc.edu.cn/2020/daliy_report"
        resp=session.post(url, data=data, headers=headers)
        data = session.get("https://weixine.ustc.edu.cn/2020").text
        soup = BeautifulSoup(data, 'html.parser')
        pattern = re.compile("202[0-9]-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}")
        token = soup.find(
            "span", {"style": "position: relative; top: 5px; color: #666;"})
        flag = False
        if pattern.search(token.text) is not None:
            date = pattern.search(token.text).group()
            print("Latest report: " + date)
            date = date + " +0800"
            reporttime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
            timenow = datetime.now(pytz.timezone('Asia/Shanghai'))
            delta = timenow - reporttime
            print("{} second(s) before.".format(delta.seconds))
            if delta.seconds < 120:
                flag = True
        if flag == False:
            print("Report FAILED!")
        else:
            print("Report SUCCESSFUL!")
        return flag

    def login(self):
        url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
        data = {
            'model': 'uplogin.jsp',
            'CAS_LT': '',
            'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
             'warn': '',
            'showCode': '1',
            'username': self.stuid,
            'password': str(self.password),
            'button': '',
        }
        session = requests.Session()
        CAS_LT_url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
        session.headers["User-Agent"]="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
        CAS_LT_res = session.get(CAS_LT_url, params={"service": "https://weixine.ustc.edu.cn/2020/caslogin"})
        CAS_LT_html = CAS_LT_res.content.decode()
        CAS_LT = re.findall('(?<=name="CAS_LT" value=")(.*?)(?=")', CAS_LT_html)[0]
        print(CAS_LT)
        data["CAS_LT"]=CAS_LT
        LT_url = 'https://passport.ustc.edu.cn/validatecode.jsp?type=login'
        LT_img = session.get(LT_url).content
        img = Image.open(io.BytesIO(LT_img))
        text = pytesseract.image_to_string(img)
        LT = re.sub("\D", "", text)
        print(CAS_LT)
        print(LT)
        data["LT"]=LT
        print(data)
        session.post(url, data=data)

        print("login...")
        return session


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='URC nCov auto report script.')
    parser.add_argument('data_path', help='path to your own data used for post method', type=str)
    parser.add_argument('stuid', help='your student number', type=str)
    parser.add_argument('password', help='your CAS password', type=str)
    args = parser.parse_args()
    autorepoter = Report(stuid=args.stuid, password=args.password, data_path=args.data_path)
    count = 5
    while count != 0:
        ret = autorepoter.report()
        if ret != False:
            break
        print("Report Failed, retry...")
        count = count - 1
    if count != 0:
        exit(0)
    else:
        exit(-1)

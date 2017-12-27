#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
from bs4 import BeautifulSoup
import datetime
import time

def get_url_html(url, encoding=None):
    r = requests.get(url)
    if not encoding:
        encoding = r.encoding
    return r.content.decode(encoding).encode('utf-8')


def get_holiday_url(year, html_doc):
    soup = BeautifulSoup(html_doc, "lxml")
    td_list = soup.findAll("td", {"class": "info"})
    for td in td_list:
        link = td.find("a")
        title = "".join(link.contents)
        search = re.search(ur'国务院办公厅关于(\d+)年部分节假日安排的通知', title)
        if search and int(search.group(1)) == year:
            return link["href"]
    return None


def match_holiday(html_doc, year=datetime.datetime.now().year + 1):
    html_doc = re.sub(r'<(/|)br(/|)>', '\n', html_doc) # 将标签换行改为换行符。
    html_doc = html_doc.replace('　', '')  # 过滤掉全角空格
    soup = BeautifulSoup(html_doc, "lxml")
    td_content = soup.find("td", {"class": "b12c"})
    html = td_content.get_text()
    html = html.split(u"\n")
    holiday = []
    for line in html:
        mat = re.search(ur"^[一二三四五六七八九十]*?、(.*?)$", line.strip())
        if mat:
            desc = mat.group(1)
            name, plan = desc.split(u"：", 2)
            holiday_mat = re.search(ur"(?P<holiday>\d+月\d+日.*?)放假", plan)
            workday_mat = re.search(ur"[，。](?P<workday>\d+月\d+日[^，。]*?)上班", plan)
            holiday_desc = holiday_mat.group("holiday") if holiday_mat else ""
            workday_desc = workday_mat.group("workday") if workday_mat else ""
            holiday_parse = parse_date(holiday_desc, year)
            workday_parse = parse_date(workday_desc, year)
            if not holiday_parse:
                raise Exception(u"解析{}年节日{}假期失败！".format(year, name))
            holiday.append({
                "name": name,
                "holiday": holiday_parse,
                "workday": workday_parse,
            })

    return holiday


def parse_date(desc, year):
    mat_days = re.findall(
        ur"(?P<from_month>\d+)月(?P<from_day>\d+)日至(?P<to_month>\d+)月(?P<to_day>\d+)日", desc)
    if mat_days:
        days = []
        month_day = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
            month_day[2] = 29
        for mat in mat_days:
            from_month, from_day, to_month, to_day = mat
            day_begin = from_day
            for month in range(int(from_month), int(to_month) + 1):
                if month == int(to_month):
                    day_end = to_day
                else:
                    day_end = month_day[month - 1]
                for day in range(int(day_begin), int(day_end) + 1):
                    days.append(get_time_stamp(year, month, day))
                day_begin = 1
        return days
    mat_days = re.findall(ur"(?P<month>\d+)月(?P<from>\d+)日至(?P<to>\d+)日", desc)
    if mat_days:
        days = []
        for mat in mat_days:
            month, from_day, to_day = mat
            for day in range(int(from_day), int(to_day) + 1):
                days.append(get_time_stamp(year, int(month), day))
        return days
    mat_days = re.findall(ur"(?P<month>\d+)月(?P<from>\d+)日", desc)
    if mat_days:
        days = []
        for mat in mat_days:
            month, day = mat
            days.append(get_time_stamp(year, int(month), int(day)))
        return days

    return []

def get_time_stamp(year, month, day):
    return int(time.mktime(
        datetime.datetime(
            year, month, day, 0, 0, 0, 0
        ).timetuple()
    ))

def get_holiday(year):
    url = "http://sousuo.gov.cn/list.htm?q=&n=15&t=paper&childtype=&subchildtype=gc189&pcodeJiguan=%E5%9B%BD%E5%8A%9E%E5%8F%91%E6%98%8E%E7%94%B5&pcodeYear=&pcodeNum=&location=%25E7%25BB%25BC%25E5%2590%2588%25E6%2594%25BF%25E5%258A%25A1%25E5%2585%25B6%25E4%25BB%2596&sort=pubtime&searchfield=title%3Acontent%3Apcode%3Apuborg%3Akeyword&title=&content=&pcode=&puborg=&timetype=timeqb&mintime=&maxtime="    
    holiday_url = get_holiday_url(year, get_url_html(url))
    if holiday_url:
        return match_holiday(get_url_html(holiday_url, 'utf-8'), year)
    return None

if __name__ == "__main__":
    print get_holiday(datetime.datetime.now().year)

# -*- coding:utf-8 -*-
import random
import threading
import time
from collections import defaultdict
from typing import Dict

import requests
from bs4 import BeautifulSoup as Bs4
from cachetools import TTLCache, cached

base_url = ""
student_list = defaultdict(str)
renew_thread: threading.Thread


def check_url() -> bool:
    """
    檢查網址是否還可用

    若網址無法連線，則嘗試使用其他網址
    """

    global base_url

    try:
        requests.head(base_url, timeout=3)

    except requests.exceptions.RequestException:
        ip_url = "http://120.126.197.52/"
        ips_url = "https://120.126.197.52/"
        real_url = "https://lms.ntpu.edu.tw/"

        for url in [ip_url, ips_url, real_url]:
            try:
                requests.head(url, timeout=3)
                base_url = url
                break

            except requests.exceptions.RequestException:
                base_url = ""

    return base_url


@cached(TTLCache(maxsize=9999, ttl=60 * 60 * 24 * 7))
def get_student_by_id(number: str) -> str:
    """取得單一學生的資料(快取一週)"""

    global base_url

    if student_list[number] == "":
        try:
            res = requests.get(
                f"{base_url}portfolio/search.php?fmScope=2&page=1&fmKeyword={number}",
                timeout=5,
            )
            res.encoding = "utf-8"
            soup = Bs4(res.text, "html.parser")
            student = soup.find("div", {"class": "bloglistTitle"})

            if student is not None:
                student_list[number] = student.find("a").text
            else:
                return ""

        except requests.exceptions.RequestException:
            base_url = ""
            return ""

    return student_list[number]


@cached(TTLCache(maxsize=99, ttl=60 * 60 * 24 * 7))
def get_students_by_year_and_department(year: str, department: str) -> Dict[str, str]:
    """取得某年某系(限大學日間部)學生名單(快取一週)"""

    global base_url

    students: Dict[str, str] = {}
    url = (
        f"{base_url}portfolio/search.php?fmScope=2&page=1&fmKeyword=4{year}{department}"
    )

    try:
        with requests.Session() as s:
            res = s.get(url, timeout=5)
            res.encoding = "utf-8"
            data = Bs4(res.text, "html.parser")
            pages = len(data.find_all("span", {"class": "item"}))
            for i in range(1, pages):
                time.sleep(random.uniform(0.05, 0.25))
                url = f"{base_url}portfolio/search.php?fmScope=2&page={i}&fmKeyword=4{year}{department}"
                res = s.get(url, timeout=5)
                res.encoding = "utf-8"

                data = Bs4(res.text, "html.parser")
                for item in data.find_all("div", {"class": "bloglistTitle"}):
                    name = item.find("a").text
                    number = item.find("a").get("href").split("/")[-1]
                    students[number] = name
                    student_list[number] = name

    except requests.exceptions.RequestException:
        base_url = ""
        return {}

    return students

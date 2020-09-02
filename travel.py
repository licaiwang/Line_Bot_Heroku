import requests
import re
import random
import csv
import math as m
from bs4 import BeautifulSoup


URL = "https://shaoweiwu088.pixnet.net/blog/post/262765884"
INDEX = ["id", "name", "dir", "county", "town", "latitude and longitude", "loc"]
WORD = ["市", "縣", "區", "鄉", "鎮"]


def initSight():
    content = requests.get(URL)
    content.encoding = "utf-8"
    soup = BeautifulSoup(content.text)
    inf = []
    index = -2
    for datas in soup.select("tr"):
        if "行程" not in datas.text:
            temp = []
            temp.append(index)
            for data in datas.select("td"):
                temp.append(data.text)
            inf.append(temp)
            index += 1
    inf.pop(0)
    inf.pop(0)
    inf.insert(0, INDEX)
    with open("data/sight.csv", "w", newline="", encoding="utf-8") as sightData:
        writer = csv.writer(sightData)
        writer.writerows(inf)


def allSight(loc: str) -> ([str, [float, float], str], [str, [float, float], str]):
    loc = loc.replace("臺", "台")
    (candi_one, candi_two) = searchAll(loc)
    if candi_two == []:
        candi_two = searchOnly(loc)
        return (candi_one, candi_two)
    return (candi_one, candi_two)


def replaceWord(content: str) -> str:
    search = ""
    for word in WORD:
        if word in content:
            search = content.replace(word, "")
            return search
    return content


def searchAll(loc: str):
    candi_one = []
    candi_two = []
    with open("data/sight.csv", "r", newline="", encoding="utf-8") as sightData:
        datas = csv.reader(sightData)
        for data in datas:
            if len(data) == 7:
                # 先搜大範圍
                search = replaceWord(data[3])
                if search in loc:
                    try:
                        candi_one.append([data[1], getLatLong(data[5]), data[6]])
                    except:
                        pass
                # 再搜兩個都有的 ex: 南投信義
                search_2 = replaceWord(data[4])
                if search_2 in loc and search in loc:
                    try:
                        candi_two.append([data[1], getLatLong(data[5]), data[6]])
                    except:
                        pass
    return (candi_one, candi_two)


def searchOnly(loc: str):
    candi_two = []
    with open("data/sight.csv", "r", newline="", encoding="utf-8") as sightData:
        datas = csv.reader(sightData)
        # 只搜單一 ex: 信義
        for data in datas:
            if len(data) == 7:
                search_2 = replaceWord(data[4])
                if search_2 in loc and len(search_2) >= len(loc):
                    try:
                        candi_two.append([data[1], getLatLong(data[5]), data[6]])
                    except:
                        pass
    return candi_two


def getLatLong(latLong: str) -> [float, float]:
    num = latLong.replace(",", "").split()
    latitude = float(num[0].replace(" ", ""))
    longitude = float(num[1].replace(" ", ""))
    return [latitude, longitude]


def searchShortlest(loc, latitude, longitude):
    loc = loc.replace("臺", "台")
    (loc_1, loc_2) = allSight(loc)
    loc_1.extend(loc_2)
    return countDistance(loc_1, latitude, longitude)


def countDistance(locs: list, cur_la: float, cur_lo: float):
    all_distance = []
    for loc in locs:
        la = float(loc[1][0])
        lo = float(loc[1][1])
        all_distance.append(m.sqrt(m.pow((cur_la - la), 2) + m.pow((cur_lo - lo), 2)))
    i = all_distance.index(min(all_distance))
    return locs[i]

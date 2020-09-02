from bs4 import BeautifulSoup
import requests

arrayDict = {
    "基隆": "10017",
    "台北": "63",
    "新北": "65",
    "桃園": "68",
    "新竹市": "10018",
    "新竹": "10004",
    "苗栗": "10005",
    "臺中": "66",
    "彰化": "10007",
    "南投": "10008",
    "雲林": "10009",
    "嘉義市": "10020",
    "嘉義": "10010",
    "台南": "67",
    "高雄": "64",
    "屏東": "10013",
    "宜蘭": "10002",
    "花蓮": "10015",
    "台東": "10014",
    "澎湖": "10016",
    "金門": "09020",
    "連江": "09007",
}
IMGURE_URL = "https://i.imgur.com/"
iconArray = [
    # 晴
    [["H5qIkm9.png"]],
    # 雲
    [["VszoSla.png"]],
    # 陰
    [["YvIimkP.png"]],
    # 雨
    [
        [
            # 雲
            # + 雨
            "JAsKSBn.png",
            # + 雷 + 雨
            "1BWyLss.png",
            # + 雲 + 局部雨
            "fKe3c9Q.png",
            "fKe3c9Q.png",
        ],
        [
            #  陰
            # + 雨
            "whiKNIx.png",
            # + 雷 + 雨
            "Esi1z95.png",
            # + 局部雨
            "MhAGbdV.png",
            # + 雷 + 局部雨
            "R3LowHU.png",
        ],
        # 雷雨
        ["whiKNIx.png"],
    ],
    [
        [  #  午後 + 雨
            "cEbCS6t.png",
            #  午後  + 雷(雨)
            "zqPxtik.png",
        ]
    ],
]


url = "https://www.cwb.gov.tw/V8/C/W/County/MOD/Week/"


def weekInf(loc: str) -> (list, list, list):
    content = requests.get(url + loc + "_Week_m.html")
    soup = BeautifulSoup(content.text)
    date = []
    inf = []
    tmp = []
    for datas in soup.select("h4"):
        date.append(datas.find("span", attrs={"class": "date"}).text)
        tps = datas.find_all("span", attrs={"class": "tem-C is-active"})
        for tp in tps:
            tmp.append(tp.text)
        for img in datas.select("img"):
            inf.append(img["alt"])
    inf = [inf[i : i + 2] for i in range(0, len(inf), 2)]
    tmp = [tmp[i : i + 2] for i in range(0, len(tmp), 2)]
    return date, inf, tmp


def searchWeather(name: str) -> (str, list, list, list):
    name = name.replace("臺", "台")
    for key in arrayDict.keys():
        if key in name:
            date, inf, tmp = weekInf(arrayDict.get(key))
            return (key, date, inf, tmp)
    return None


def stickerSelect(inf: str):
    # 優先度 午後 ->   雨    -> 陰  -> 雲 -> 晴
    idx = [0, 0, 0]
    patterns = ["晴", "雲", "陰", "雨", "午"]
    for i, pattern in enumerate(patterns):
        if pattern in inf:
            idx[0] = i
    patterns.remove(patterns[idx[0]])

    if idx[0] == 4:
        if "雷" in inf:
            idx[2] = 1
        else:
            idx[2] = 0

    elif idx[0] == 3:
        for i, pattern in enumerate(["雲", "陰"]):
            if pattern in inf:
                idx[1] = i
            else:
                idx[1] = 2
        else:
            if "雷" and "局" in inf:
                idx[2] = 3
            elif "局" in inf:
                idx[2] = 2
            elif "雷" in inf:
                idx[2] = 1

    elif idx[0] < 3:
        idx.append(0)
        idx.append(0)

    imgUrl = iconArray[idx[0]][idx[1]][idx[2]]
    return IMGURE_URL + imgUrl

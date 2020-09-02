import xml.etree.cElementTree as et
import requests
import re
import random


RESULT = ["呵呵沒中，笑死", "沒中，可憐", "差一點點，可惜", "沒中，再來 yee 次", "加油一點兄弟", "中了!..........才怪"]
PRIZE = f"""
統一發票獎金一覽表：\n
    特別獎：一千萬元\n
    特獎：二百萬元\n
    頭獎：二十萬元\n
    二獎：四萬元\n
    三獎：一萬元\n
    四獎：四千元\n
    五獎：一千元\n
    六獎：二百元 """


def initData(n: int) -> (str, list):
    """
    Args：
        n：
           期別，第 0 期就是最新月的開獎，依此類推回每一期差 2 個月，最多回朔 8 年
    Returns：
        title:
            回傳月份字串
        prizes：
            回傳內容為 str 中獎號碼 list，長度為 6：
                0 : 特別獎 1000 萬
                1 : 特獎 200 萬
                2 : 頭獎 -1 20 萬
                3 : 頭獎 -2 20 萬
                4 : 頭獎 -3 20 萬
                5 : 增開六獎 200 元
    """
    content = requests.get("https://invoice.etax.nat.gov.tw/invoice.xml")
    tree = et.fromstring(content.text)
    items = list(tree.iter(tag="item"))
    title = items[n][0].text
    temp_prize = (
        items[n][2].text.replace("<p>", "").replace("</p>", "\n").replace("、", "\n")
    )  # 中獎號碼
    prizes = temp_prize.split("\n")
    for (i, prize) in enumerate(prizes):
        prizes[i] = re.sub("\\D", "", prize)
    prizes.pop(-1)  # 去掉，因最後一個元素為空
    return (title, prizes)


def askPrize(mon: int) -> str:
    """
    Args :
        n：欲查詢的期別
    Returns：
        查詢結果字串
    """
    (date, data) = initData(mon)
    date = f"{date}月\n"
    ssp_prize = f"特別獎：{data[0]}\n"
    sp_prize = f"特獎：{data[1]}\n"
    first_prize = f"頭獎：{data[2]}、{data[3]}、{data[4]}\n"
    six_prize = f"六獎：{data[2][5:]}、{data[3][5:]}、{data[4][5:]}、{data[5]}\n"
    return date + ssp_prize + sp_prize + first_prize + six_prize


def checkWinPrize(num: str) -> (bool, int):
    (date_1, data_1) = initData(0)
    (date_2, data_2) = initData(1)
    six_prize_1 = [data_1[2][5:], data_1[3][5:], data_1[4][5:], data_1[5]]
    six_prize_2 = [data_2[2][5:], data_2[3][5:], data_2[4][5:], data_2[5]]
    # 若輸入 3 個數字先檢查當期 6 獎有沒有中，再檢查前期 (最多也只能換到前一期而已)
    if num in six_prize_1:
        return (1, f"恭喜你中了{date_1}月的發票六獎，200 塊！")
    elif num in six_prize_2:
        return (2, f"恭喜你中了{date_2}月的發票六獎，200 塊！")
    return (0, RESULT[random.randint(0, 5)])

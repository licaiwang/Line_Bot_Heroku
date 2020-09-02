import random


applyBreakfast = {"加料": ["吐司", "漢堡", "蛋餅", "乳酪餅"]}

singleBreakfast = {"不加料": ["黑胡椒鐵板麵", "肉醬鐵板麵", "蘿蔔糕", "水煎包", "蔥抓餅", "飯糰加蛋", "鍋貼"]}

breakfast = [applyBreakfast, singleBreakfast]

drinkItem = ["咖啡", "紅茶", "綠茶", "奶茶", "紅茶拿鐵", "巧克力牛奶", "柳橙汁", "養樂多", "開水"]

toastItem = ["花生", "草莓", "藍莓", "香蒜", "巧克力", "奶酥"]


def selectBreakfast() -> str:
    applyItem = [
        "玉米",
        "鮪魚",
        "熱狗",
        "培根",
        "火腿",
        "起司",
        "肉排",
        "豬肉",
        "卡拉雞",
        "燻雞肉",
        "香雞",
        "總匯",
        "薯餅",
    ]
    breakfast_dict = random.choices(breakfast, weights=[0.65, 0.35], k=1)[0]
    apply = ""
    food = ""
    if next(iter(breakfast_dict)) == "不加料":
        food = random.choice(breakfast_dict.get("不加料"))
    else:
        food = random.choice(breakfast_dict.get("加料"))
        if food == "吐司":
            applyItem.extend(toastItem)
        elif food == "蛋餅":
            applyItem.append("蔬菜")
        apply = random.choice(applyItem)

    drink = random.choices(
        drinkItem, weights=[0.5, 0.7, 0.4, 0.5, 0.2, 0.3, 0.1, 0.1, 0.07], k=1
    )[0]
    return f"推薦您早餐吃：\n {apply}{food} + {drink}"

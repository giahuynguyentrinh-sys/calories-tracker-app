from datetime import date, datetime, timedelta
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
valid_types = ["breakfast", "lunch", "afternoon snack", "dinner", "late snack"]
log_today = []
class entry():
    def __init__(self, name,weight, mealtype, entrydate =None):
        if weight <= 0 or weight >= 5000:
            raise ValueError("weight must in [0,5000]g")
        if entry.validtype(mealtype):
            raise ValueError(f"Loại bữa phải là một trong: {', '.join(valid_types)}")
        self.name = name
        self.weight = weight
        self.mealtype = mealtype
        self.date = entrydate if entrydate is not None else date.today()
        entry.macroscaculated(self)
    def guessmealtype():
        hour = datetime.now().hour
        if 5 <= hour <= 10:
            return "breakfast"
        elif 10 <= hour <= 14:
            return "lunch"
        elif 14 <=  hour <= 17:
            return "afternoon snack"
        elif 17 <= hour <= 21:
            return "dinner"
        elif hour >= 21 or hour <= 5:
            return "late snack"
    @staticmethod
    def validtype(mealtype):
        return mealtype not in valid_types
    def datetoobject(date_str):
        return datetime.strptime(date_str, "%Y%m%d").date()
    def datetostring(d):
        return d.strftime("%Y%m%d")
    def add_food(name, protein, carb, fat):
        name = name.strip()
        if name == "":
            raise ValueError("Tên món không được để trống")
        checks = [
            0 <= protein <= 10000,
            0 <= carb <= 10000,
            0 <= fat <= 10000
        ]
        if not all(checks):
            raise ValueError("protein/carb/fat phải trong khoảng 0 đến 10000")

        with open("fooddatabase.json", "r") as f:
            database = json.load(f)

        database[name] = {"protein": protein, "carb": carb, "fat": fat}

        with open("fooddatabase.json", "w") as f:
            json.dump(database, f, indent=4) 
    def macroscaculated(self):
        with open("fooddatabase.json", "r") as f:
            database = json.load(f)
        info = database[self.name]
        ratio = (self.weight / 100 ) 
        self.protein = info["protein"] * ratio
        self.carb = info["carb"] * ratio
        self.fat = info["fat"] * ratio
        self.calories = (self.protein * 4) + (self.carb * 4) + (self.fat * 9)
        return self.protein, self.carb, self.fat, self.calories       
    def todict(self):
        return {
            "name": self.name, 
            "date": entry.datetostring(self.date),
            "weight": self.weight,
            "mealtype": self.mealtype
        }
    @classmethod
    def fromdict(cls, data):
        new_entry = cls(
            name = data["name"],
            entrydate = entry.datetoobject(data["date"]),
            weight = data["weight"],
            mealtype = data["mealtype"]
        )
        return new_entry
    @classmethod
    def entry_today(cls, foodweight,username,mealtype, userdate = None):
        if  0>foodweight or foodweight > 5000:
            raise ValueError("Khối lượng phải trong khoảng (0, 5000] gram")
        meal = cls(
            name = username,
            weight = foodweight,
            entrydate = userdate,
            mealtype = mealtype
        )
        return meal
    
class user():
    def __init__(self, name, weight, height, age, sex, workout, goal):
        name = name.strip()
        if name == "":
            raise ValueError("name should be Nguyen Van A not none")
        checks = [
                        20 <= weight <= 200,
                        50 <= height <= 250,
                        1 <= age <= 120
        ]
        if not all(checks):
            raise ValueError("invalid weight, height or age")
        if sex not in ["female", "male"]:
            raise ValueError("invalid sex, type either female or male")
        if goal not in [1,2,3]:
            raise ValueError("invalid goal must be a number [1,3]")
        if workout not in [1.2,1.375,1.55,1.725,1.9]:
            raise ValueError("invalid workout must be a number in [1.2,1.375,1.55,1.725,1.9]")
        self.name= name
        self.weight= weight
        self.height= height
        self.age = age
        self.sex= sex
        self.workout = workout
        self.goal = goal
        
    def todict(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "height": self.height,
            "age": self.age,
            "sex": self.sex,
            "workout": self.workout,
            "goal": self.goal
            }
    @classmethod
    def fromdict(cls, data):
        return cls(
            name = data["name"],
            weight = data["weight"],
            height = data["height"],
            age = data["age"],
            sex = data["sex"],
            workout = data["workout"],
            goal = data["goal"]
        ) 
    def bmr(self):
        if self.sex == "male":
            bmrscore = 10*self.weight + 6.25*self.height - 5*self.age + 5
        elif self.sex == "female":
            bmrscore = 10*self.weight + 6.25*self.height - 5*self.age-161
        return bmrscore
    def tdee(self):
        bmrscore = self.bmr()
        tdeescore = bmrscore*self.workout
        return tdeescore
    def caloriesadvice(self):
        tdeescore = self.tdee()
        if self.goal == 1:
            caloriesneeded = tdeescore - 500
        elif self.goal == 2:
            caloriesneeded = tdeescore
        elif self.goal == 3:
            caloriesneeded = tdeescore + 300
        return caloriesneeded
    def proteinadvice(self):
        if self.goal == 1:
            proteinneeded = self.weight * 1.6
        elif self.goal == 2:
            proteinneeded = self.weight * 1.4
        elif self.goal == 3:
            proteinneeded = self.weight * 1.6
        return proteinneeded
def read_foods():
    try:
        with open("fooddatabase.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def foods_in_use():
    """Tên các món đang xuất hiện trong log.json."""
    try:
        with open("log.json", "r") as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return set()
    return {log["name"] for log in logs}

def delete_food(name):
    database = read_foods()
    if name not in database:
        raise ValueError(f"Không tìm thấy món '{name}'")
    if name in foods_in_use():
        raise ValueError(f"'{name}' đang được dùng trong nhật ký ăn, không thể xóa")
    del database[name]
    with open("fooddatabase.json", "w") as f:
        json.dump(database, f, indent=4)
   
def add_food(name, protein, carb, fat):
    name = name.strip()
    if name == "":
        raise ValueError("Tên món không được để trống")
    checks = [
        0 <= protein <= 10000,
        0 <= carb <= 10000,
        0 <= fat <= 10000
    ]
    if not all(checks):
        raise ValueError("protein/carb/fat phải trong khoảng 0 đến 10000")
    with open("fooddatabase.json", "r") as f:
        database = json.load(f)
    database[name] = {"protein": protein, "carb": carb, "fat": fat}
    with open("fooddatabase.json", "w") as f:
        json.dump(database, f, indent=4)
#save/load       
def save_entry(newentry):
    try:
        with open("log.json", "r") as f: #mo file log.json luu du lieu
            #file trong do duoi bien "f"
            entries = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        entries = [] 
    if isinstance(newentry, list):
        for e in newentry:
            entries.append(e.todict())
    else:
        entries.append(newentry.todict())
    with open("log.json", "w") as file:
        json.dump(entries, file, indent = 4)

def load_entry():
    try:
        with open("log.json", "r") as file:
            data = json.load(file)
    except(FileNotFoundError, json.JSONDecodeError):
        print("no file found")
        return
    newentries = []
    for newentry in data:
        newentry = entry.fromdict(newentry)
        newentries.append(newentry)
    return newentries

def save_user(u):
    with open("personstat.json", "w") as f:
        json.dump(user.todict(u), f, indent = 4)
def load_user():
    try: 
        with open("personstat.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    newuser = user.fromdict(data)
    return newuser
#editmeal
def editmeal(index, d, name, weight, mealtype):
    d_str = entry.datetostring(d)
    with open("log.json", "r") as f:
        data = json.load(f)
    try:
        with open("log.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    positions = [i for i, log in enumerate(data) if log["date"] == d_str]
    if not 0<= index < len(positions):
        raise ValueError("Số thứ tự không hợp lệ")
    new = entry(name, weight, mealtype)
    data[positions[index]] = new.todict()
    with open("log.json","w") as f:
        json.dump(data, f, indent = 4)
    
        
def get_logs_by_date(d):
    """Log của ngày d, xếp theo thứ tự bữa trong ngày."""
    d_str = entry.datetostring(d)
    try:
        with open("log.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    day_logs = [log for log in data if log["date"] == d_str]
    day_logs.sort(key=lambda log: valid_types.index(log["mealtype"]))
    return day_logs


def delete_log(d, index):
    d_str = entry.datetostring(d)
    try:
        with open("log.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    other_logs = [log for log in data if log["date"] != d_str]   
    day_logs = get_logs_by_date(d)                            
    if not (0 <= index < len(day_logs)):
        raise ValueError("Số thứ tự không hợp lệ")
    del day_logs[index]
    with open("log.json", "w") as f:
        json.dump(other_logs + day_logs, f, indent=4)
    
def input_float(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            print("invalid number")
def input_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("invalid number")
#showing, printing
def searchlogbydate(d):
    if d > date.today():
        raise ValueError("future date not allowed")
    try:
        with open("log.json", "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    d_str = entry.datetostring(d)
    logs = []
    for log in data:
        if log["date"] == d_str:
            logs.append(log)
    return logs
def mealmenu():
    print("""================================
          MANAGE MEALS
================================
1. Add meal
2. Edit meal
3. Delete meal
4. Exit
================================""")
    userchoice = input_int("choose: ")
    if userchoice == 1:
        meal = entry.entry_today()
        log_today.append(meal)   
    if userchoice == 2:
        editmeal()
    elif userchoice == 3:
        delete_log()
    elif userchoice == 4:
        save_entry(log_today)
        print("you exit")
        return
    else:
        print("invalid choice")
def show_menu(u):
    goal_map = {1: "Lose weight", 2: "Maintain weight", 3: "Gain weight"}
    time = date.today()

    print(f"""======================================== 
          CALORIES TRACKER 
========================================
 Day: {time}
 User: {u.name}
 Goal: {goal_map[u.goal]}
 Target: {u.caloriesadvice():.0f} kcal
---------------------------------------- 
  1. Manage meal 
  2. Today's log 
  3. Search log by date
  4. View user stats 
  5. Change profile 
  6. See statistics
  7. Save & exit 
========================================""")
    
#numpycombipandas

def logpandas():
    with open("log.json", "r") as f:
        data = json.load(f)
    with open("fooddatabase.json", "r") as file:
        dtb = json.load(file)
    data = pd.DataFrame(data)
    return data, dtb
def macros(row, key, dtb):
    food = dtb.get(row["name"])
    if food is None:
        return 0
    return food[key] * row["weight"] /100    
def subnutrientnumpy(udays, logchart, dtb):
    start_date = pd.Timestamp(date.today() - timedelta(days=udays))
    logchart["date"] = pd.to_datetime(logchart["date"])
    mask = (logchart["date"] >= start_date) & (logchart["date"] <= pd.Timestamp(date.today()))
    logchart = logchart[mask]   
    if udays <= 21:
        logchart["period_key"] = logchart["date"].dt.to_period("D")
    elif udays <= 90:
        logchart["period_key"] = logchart["date"].dt.to_period("W")
    elif udays <= 365:
        logchart["period_key"] = logchart["date"].dt.to_period("M")
    elif udays <= 1089:
        logchart["period_key"] = logchart["date"].dt.to_period("Q")
    else:
        logchart["period_key"] = logchart["date"].dt.to_period("Y")
    nutrients = ["protein", "carb", "fat", "calories"]
    for nutrient in nutrients:
        logchart[nutrient] = logchart.apply(lambda row: macros(row, nutrient, dtb), axis = 1)
    x = logchart.groupby("period_key")[["protein", "carb", "fat", "calories"]].sum()
    ymean = logchart.groupby("period_key")[["protein", "carb", "fat", "calories"]].mean()
    zstd = logchart.groupby("period_key")[["protein", "carb", "fat", "calories"]].std()
    qcv = ( zstd / ymean ) * 100
    return x, ymean, zstd, qcv
def nutrientnumpy():
    logchart, dtb = logpandas()  
    udays = input("Type number of dates or enter to review all data: ")
    if udays == "":
        udays = len(logchart)
    else:
        udays = int(udays)
    return subnutrientnumpy(udays, logchart, dtb)
def chooseunit():
    units = {1: "protein", 2: "carb", 3: "fat", 4: "calories"}
    while True:
        print("""
===== CHOOSE UNIT =====
1. Protein
2. Carb
3. Fat
4. Calories
=======================""")
        c = input_int("Choose a unit: ")
        if c in units:
            return units[c]
        print("Invalid choice")

def drawchart(df, unit, title, ylabel):
    plt.plot(df.index.to_timestamp(), df[unit], marker="o")
    plt.title(f"{title} of {unit}")
    plt.xlabel("Time")
    plt.ylabel(ylabel)
    plt.show()

def chartstatsum(nt, unit):
    drawchart(nt, unit, "Sum chart", unit)

def chartstatmean(ymean, unit):
    drawchart(ymean, unit, "Mean chart", f"Mean {unit}")

def chartstatstd(zstd, unit):
    drawchart(zstd, unit, "Std chart", f"Std {unit}")

def chartstatqcv(qcv, unit):
    drawchart(qcv, unit, "CV chart", f"CV {unit} (%)")
    
def today_totals(d=None):
    """Tổng protein/carb/fat/calories đã ăn trong ngày d (mặc định hôm nay)."""
    d = d or date.today()
    foods = read_foods()
    total = {"protein": 0, "carb": 0, "fat": 0, "calories": 0}
    for log in get_logs_by_date(d):
        food = foods.get(log["name"])
        if food is None:          # món đã bị xóa khỏi database thì bỏ qua
            continue
        ratio = log["weight"] / 100
        p = food["protein"] * ratio
        c = food["carb"] * ratio
        f = food["fat"] * ratio
        total["protein"] += p
        total["carb"] += c
        total["fat"] += f
        total["calories"] += p * 4 + c * 4 + f * 9
    return total


def macro_targets(u):
    """Mục tiêu hằng ngày. Protein và calories lấy từ class user,
    fat = 25% calories, carb = phần calories còn lại."""
    calories = u.caloriesadvice()
    protein = u.proteinadvice()
    fat = calories * 0.25 / 9
    carb = max((calories - protein * 4 - fat * 9) / 4, 0)
    return {"calories": calories, "protein": protein, "carb": carb, "fat": fat}

import os

AVATAR_PATH = "avatar.png"

def save_avatar(uploaded_file):
    """Lưu ảnh người dùng upload thành avatar.png."""
    with open(AVATAR_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())

def load_avatar():
    """Trả về đường dẫn ảnh nếu có, không thì None."""
    return AVATAR_PATH if os.path.exists(AVATAR_PATH) else None
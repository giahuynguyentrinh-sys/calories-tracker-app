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
    def validtype(userinput):
        if userinput not in valid_types:
            raise ValueError(f"Loại bữa phải là một trong: {', '.join(valid_types)}")
        return userinput
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
        while True:
            try:
                with open("fooddatabase.json", "r") as f:
                    database = json.load(f)
                info = database[self.name]
                break
            except KeyError:
                print("no data food found in database")
                entry.databaseappend()        
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
        entries = [] #neu ko tim thay file entries tu dong tao ra mot entries
        #rong de luu gia tri vao
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
def editmealmenu():
    while True:
        print("""
    What do you want to edit?
    1. Name
    2. Weight
    3. Meal type
    4. Cancel""")
        userchoice= input_int("type: ")
        if 1 <= userchoice <= 4:
            return userchoice
        else:
            print("invalid")
#editmeal
def editmeal():
    date_logs = searchlogbydate()
    if not date_logs:
        print("no log found that day")
        return
    datetoobject = entry.datetoobject(date_logs[0]["date"])
    datetostring = date_logs[0]["date"]
    print(f"date: {datetoobject}")
    n= False
    while n == False:
        date_logs.sort(key = lambda log: log["mealtype"])
        print("Breakfast: ")
        while True:
            usermeal = input_int(f"choose a number or choose {len(date_logs)} to save and exit: ")
            if usermeal == len(date_logs):
                print("you exit")
                n = True
                break
            elif usermeal < 0 or usermeal > len(date_logs):
                print("wrong number")
                continue
            else:
                while True:
                    userchoice = editmealmenu()
                    if userchoice == 1:
                        date_logs[usermeal]["name"] = input("type food name: ")
                    elif userchoice == 2:
                        date_logs[usermeal]["weight"] = input_float("type weight: ")
                    elif userchoice == 3:
                        date_logs[usermeal]["mealtype"] = entry.type()
                    elif userchoice ==4:
                        break
                    else:
                        print("invalid")
    with open("log.json", "r") as f:
        data = json.load(f)
    new_data = []
    for log in data:
        if log["date"] != datetostring:
            new_data.append(log)
    for log in date_logs:
        new_data.append(log)
    with open("log.json", "w") as f:
        json.dump(new_data, f, indent = 4)

def deletemeal():
    date_logs = searchlogbydate()
    if not date_logs:
            print("no log found that day")
            return
    datetoobject = entry.datetoobject(date_logs[0]["date"])
    datetostring = date_logs[0]["date"]
    print(f"date: {datetoobject}")
    n = False
    while n == False:
        date_logs.sort(key = lambda log: log["mealtype"])
        print("Breakfast: ")
        while True:
            usermeal = input_int(f"choose a number to delete or choose {len(date_logs)} to save and exit: ")
            if usermeal == len(date_logs):
                print("you exit")
                n = True
                break
            elif usermeal < 0 or usermeal > len(date_logs):
                print("wrong number")
                continue
            else:
                del date_logs[usermeal]
    with open("log.json", "r") as f:
        data = json.load(f)
        new_data = []
        for log in data:
            if log["date"] != datetostring:
                new_data.append(log)
        for log in date_logs:
            new_data.append(log)
        with open("log.json", "w") as f:
            json.dump(new_data, f, indent = 4)
    
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
def viewlog(loglist,u):
    caloriesneeded = u.caloriesadvice()
    proteineeded = u.proteinadvice()
    protein = 0
    calories = 0
    if len(loglist) == 0:
        print("No log found for today.")
        return
    print("Today's food log:")
    for i, log in enumerate(loglist, start=1):
        print(f"{i}. {log.name} ({log.weight}g)")
        print(f"   protein: {log.protein:.1f}, calories: {log.calories:.1f}kcal")
        protein += log.protein
        calories += log.calories
    if calories >= caloriesneeded:
        print(f"Exceeding calories: {calories - caloriesneeded}")
    if  protein >= proteineeded:
        print(f"Exceeding protein: {protein - proteineeded}")
    if caloriesneeded > calories:
        print(f"Calories left: {caloriesneeded - calories}")
    if proteineeded > protein:
        print(f"Protein left: {proteineeded - protein}")
def searchlogbydate():
        logs = []
        try:
            with open("log.json", "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            data=[]
        userinput = input("choose date yyyymmdd: ")
        userdate = date.today() if userinput == "" else entry.datetoobject(userinput)
        while userdate > date.today():
            print("no future date allow")
            userinput = input("choose date yyyymmdd: ").strip()
            userdate = entry.datetoobject(userinput)
        userdatestr = entry.datetostring(userdate)
        for log in data:
            if log["date"] == userdatestr:
                logs.append(log)
        return logs
def viewuserstat(u):
    print(f"Name: {u.name}")
    print(f"Age: {u.age}")
    print(f"Weight: {u.weight} kg")
    print(f"Height: {u.height} cm")
    print(f"Sex: {u.sex}")
    activity_levels = {
    1.2: "Sedentary",
    1.375: "Lightly active",
    1.55: "Moderately active",
    1.725: "Very active",
    1.9: "Extra active",
    } 
    print(f"Activity level: {activity_levels[u.workout]}")
    goal_map = {1: "Lose weight", 2: "Maintain weight", 3: "Gain weight"}
    print(f"Goal: {goal_map[u.goal]}")
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
        deletemeal()
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

def chartstatmenu():
    nt, ymean, zstd, qcv = nutrientnumpy()
    unit = chooseunit()
    while True:
        print(f"""
===== CHART STATS =====
1. Show sum chart
2. Show chart average (mean)
3. Show chart variation (std)
4. Show chart consistency (CV %)
5. Change unit (currently: {unit})
6. Exit
=======================""")
        choice = input_int("Choose an option: ")

        if choice == 1:
            chartstatsum(nt, unit)
        elif choice == 2:
            chartstatmean(ymean, unit)
        elif choice == 3:
            chartstatstd(zstd, unit)
        elif choice == 4:
            chartstatqcv(qcv, unit)
        elif choice == 5:
            unit = chooseunit()
        elif choice == 6:
            break
        else:
            print("Invalid choice")
                
def statnumpy():    
    while True:
        print("""
        ===== NUTRITION STATS =====
        1. Show average (mean)
        2. Show variation (std)
        3. Show consistency (CV %)
        4. See overall statistics
        5. See chart menu
        6. Exit
        ============================
        """)
        choice = input_int("Choose an option: ")

        if choice == 1:
            nt, ymean,zstd,qcv = nutrientnumpy()
            print(ymean)
        elif choice == 2:
            nt, ymean,zstd,qcv = nutrientnumpy()
            print(zstd)
        elif choice == 3:
            nt, ymean,zstd,qcv = nutrientnumpy()
            print(qcv)
        elif choice == 4:
            nt, ymean,zstd,qcv = nutrientnumpy()
            print(nt)
        elif choice == 5:
            chartstatmenu()
        elif choice == 6:
            print("you exit")
            return
        else:
            print("invalid")
def main(u):
    load_user()
    while True:
        show_menu()
        userchoice = input_float("type number: ")
        if userchoice == 1:
            mealmenu()
        elif userchoice == 2:
            viewlog(log_today)
        elif userchoice == 3:
            logs = searchlogbydate()
        elif userchoice == 4:
            viewuserstat()
        elif userchoice == 5:
            user.stat()
        elif userchoice == 6:
            statnumpy()
        elif userchoice == 7:
            save_user(u)
            save_entry(log_today)
            exit()
        else:
            print('invalid')
if __name__ == "__main__":
    main()
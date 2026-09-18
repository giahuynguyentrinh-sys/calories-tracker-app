from datetime import date, datetime, timedelta
import json
import numpy as np
import matplotlib.pyplot as plt
currentuser = None
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
    def type():
        default_type = entry.guessmealtype()
        valid_types = ["breakfast", "lunch", "afternoon snack", "dinner", "late snack"]

        userinput = input(f"mealtype:[{default_type}] (nhấn Enter hoặc gõ loại khác: )")
        while userinput != "" and userinput not in valid_types:
            userinput = input(f"Không hợp lệ, nhập lại (Enter để dùng '{default_type}'): ")
        meal_type = default_type if userinput == "" else userinput
        return meal_type
    def datetoobject(date_str):
        return datetime.strptime(date_str, "%Y%m%d").date()
    def datetostring(d):
        return d.strftime("%Y%m%d")
    @staticmethod
    def databaseappend():
            with open("fooddatabase.json", "r") as f:
                database = json.load(f)
            name = input("press food name: ")
            while True:
                protein = input_float("press protein g: ")
                carb = input_float("press carb g: ")
                fat = input_float("press fat g: ")
                checks = [
                    0<= protein <= 10000,
                    0<= carb <= 10000,
                    0 <= fat <= 10000
                ]
                if all(checks):
                    database[name] = {"protein": protein,"carb": carb,"fat": fat}
                    break
                else:
                    print("invalid")
            with open("fooddatabase.json", 'w') as f:
                json.dump(database, f, indent = 4) 
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
    def entry_today(cls):
        userdate = input("type date (YYYYMMDD): ")
        username = input("type food name: ")
        while True:
            userweight = input_float("type weight kg: ")
            if 0< userweight < 150:
                break
        meal = cls(
            name = username,
            weight = userweight,
            entrydate = date.today() if userdate == "" else entry.datetoobject(userdate),
            mealtype = entry.type()
        )
        return meal
    
class user():
    def __init__(self, name, weight, height, age, sex, workout, goal):
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

    @classmethod
    def stat(cls):
        global currentuser
        name = input("name: ")
        while True:
            weight = input_float("weight in kg: ")
            height = input_float("height in cm: ")
            age = input_int("age: ")
            checks = [
                20 <= weight <= 150,
                50 <= height <= 250,
                1 <= age <= 120
            ]
            if all(checks):
                break
            else:
                print("invalid")
        sex = input("female/male: ")
        while sex not in ["female", "male"]:
            sex = input("female/male: ")
        workout = cls.activity()
        goal = input_int("""
What is your goal?

1. Lose weight
2. Maintain weight
3. Gain weight

Choose (1-3): """)
        while goal not in [1, 2, 3]:
            goal = int(input("""
What is your goal?

1. Lose weight
2. Maintain weight
3. Gain weight

Choose (1-3): """)) 
        userstat = cls(
            name = name,
            weight = weight,
            height = height,
            age = age,
            sex = sex, 
            goal = goal,
            workout = workout
        )
        
        currentuser = userstat
        return userstat
        
    @staticmethod
    def activity():
        n = 0
        while n not in [1,2,3,4,5]:
            n = input_int("""
            How active are you?
                
            1. Sedentary
            Little or no exercise
                
            2. Lightly active
            Light exercise 1-3 days/week
                
            3. Moderately active
            Moderate exercise 3-5 days/week
                
            4. Very active
            Hard exercise 6-7 days/week
                
            5. Extra active
            Very hard exercise / physical job
                
            Choose (1-5): 
            """)
        if n == 1: 
            return 1.2
        elif n == 2:
            return 1.375
        elif n == 3:
            return 1.55
        elif n == 4: 
            return 1.725
        elif n ==5:
            return 1.9       
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

def save_user(userstat):
    with open("personstat.json", "w") as f:
        json.dump(user.todict(userstat), f, indent = 4)
def load_user():
    global currentuser
    try: 
        with open("personstat.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("no save file found")
        newuser = user.stat()
        return newuser
    newuser = user.fromdict(data)
    currentuser = newuser
    return newuser
#subeditmeal()
def searchandprint(datelogs, mealtype):
    count = -1
    for i,log in enumerate(datelogs):
        count += 1
        if log["mealtype"] == mealtype:
            print(count,log)
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
        searchandprint(date_logs, "breakfast")
        print("Lunch: ")
        searchandprint(date_logs, "lunch")
        print("Afternoon snack")
        searchandprint(date_logs, "afternoon snack")
        print("Dinner")
        searchandprint(date_logs, "dinner")
        print("late snack")
        searchandprint(date_logs, "late snack")
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
        searchandprint(date_logs, "breakfast")
        print("Lunch: ")
        searchandprint(date_logs, "lunch")
        print("Afternoon snack")
        searchandprint(date_logs, "afternoon snack")
        print("Dinner")
        searchandprint(date_logs, "dinner")
        print("late snack")
        searchandprint(date_logs, "late snack")
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
def viewlog(loglist):
    caloriesneeded = currentuser.caloriesadvice()
    proteineeded = currentuser.proteinadvice()
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
def printlog(date_logs):
    if not date_logs:
        print("no log found that day")
        return
    datetoobject = entry.datetoobject(date_logs[0]["date"])
    print(f"date: {datetoobject}")
    date_logs.sort(key = lambda log: log["mealtype"])
    print("Breakfast: ")
    searchandprint(date_logs, "breakfast")
    print("Lunch: ")
    searchandprint(date_logs, "lunch")
    print("Afternoon snack")
    searchandprint(date_logs, "afternoon snack")
    print("Dinner")
    searchandprint(date_logs, "dinner")
    print("late snack")
    searchandprint(date_logs, "late snack")
def viewuserstat():
    global currentuser
    print(f"Name: {currentuser.name}")
    print(f"Age: {currentuser.age}")
    print(f"Weight: {currentuser.weight} kg")
    print(f"Height: {currentuser.height} cm")
    print(f"Sex: {currentuser.sex}")
    activity_levels = {
    1.2: "Sedentary",
    1.375: "Lightly active",
    1.55: "Moderately active",
    1.725: "Very active",
    1.9: "Extra active",
    } 
    print(f"Activity level: {activity_levels[currentuser.workout]}")
    goal_map = {1: "Lose weight", 2: "Maintain weight", 3: "Gain weight"}
    print(f"Goal: {goal_map[currentuser.goal]}")
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
def show_menu():
    goal_map = {1: "Lose weight", 2: "Maintain weight", 3: "Gain weight"}
    time = date.today()

    print(f"""======================================== 
          CALORIES TRACKER 
========================================
 Day: {time}
 User: {currentuser.name}
 Goal: {goal_map[currentuser.goal]}
 Target: {currentuser.caloriesadvice():.0f} kcal
---------------------------------------- 
  1. Manage meal 
  2. Today's log 
  3. Search log by date
  4. View user stats 
  5. Change profile 
  6. See statistics
  7. Save & exit 
========================================""")
    
#numpy

def logdict():
    try:
        with open("chart.json", "r") as f:
            logchart = json.load(f)
            return logchart
    except (FileNotFoundError,json.JSONDecodeError):
        logchart = {}
        with open("log.json", "r") as f:
            data = json.load(f)
        for log in data:
            log_date = log["date"]
            if log["date"] not in logchart:
                logchart[log_date] = []
                logchart[log_date].append(log)
            elif log["date"] in logchart:
                logchart[log_date].append(log)
        with open("chart.json", "w") as f:
            json.dump(logchart, f, indent = 4)
        return logchart
def get_group_key(day, group_by):
    if group_by == 'day':
        return day
    elif group_by == 'week':
        return (day.isocalendar()[0], day.isocalendar()[1])  # (nam, tuan)
    elif group_by == 'month':
        return (day.year, day.month)
    elif group_by == 'quarter':
        return (day.year, (day.month - 1) // 3 + 1)
 
 
def subnutrientnumpy(udays):
    # quyet dinh gom theo gi dua vao so ngay yeu cau
    if udays <= 21:
        group_by = 'day'
    elif udays <= 90:
        group_by = 'week'
    else:
        group_by = 'month'
 
    logchart = logdict()
    date_start = date.today() - timedelta(days=udays)
 
    seen_keys = set()
    grouped_data = {}
 
    for day_str, loglist in logchart.items():
        if not loglist:
            continue
 
        day = entry.datetoobject(day_str)
 
        if not (date_start <= day <= date.today()):
            continue
 
        protein0 = 0
        carb0 = 0
        fat0 = 0
        calories0 = 0
        for log in loglist:
            log =  entry.fromdict(log)
            protein, carb, fat, calories = entry.macroscaculated(log)
            protein0 += protein
            carb0 += carb
            fat0 += fat
            calories0 += calories
 
        group_key = get_group_key(day, group_by)
 
        if group_key not in seen_keys:
            seen_keys.add(group_key)
            grouped_data[group_key] = {
                'protein': protein0,
                'carb': carb0,
                'fat': fat0,
                'calories': calories0,
            }
        else:
            grouped_data[group_key]['protein'] += protein0
            grouped_data[group_key]['carb'] += carb0
            grouped_data[group_key]['fat'] += fat0
            grouped_data[group_key]['calories'] += calories0
 
    proteinlist = [v['protein'] for v in grouped_data.values()]
    carblist = [v['carb'] for v in grouped_data.values()]
    fatlist = [v['fat'] for v in grouped_data.values()]
    calorieslist = [v['calories'] for v in grouped_data.values()]

    thatday = []
    for group_key in grouped_data.keys():
        if group_by == 'day':
            actual_date = group_key
        elif group_by == 'week':
            year = group_key[0]
            week = group_key[1]
            actual_date = date.fromisocalendar(year, week, 1)
        elif group_by == 'month':
            year = group_key[0]
            month = group_key[1]
            actual_date = date(year, month, 1)
        elif group_by == 'quarter':
            year = group_key[0]
            quarter_number = group_key[1]
            first_month_of_quarter = (quarter_number - 1) * 3 + 1
            actual_date = date(year, first_month_of_quarter, 1)
        thatday.append(actual_date)
    return proteinlist, carblist, fatlist, calorieslist, thatday               
def nutrientnumpy():
    logchart = logdict()
    udays = input("Enter the number of days, or press Enter to view all data: ")
    if udays == "":
        udays = len(logchart)
        proteinlist, carblist, fatlist,calorieslist,thatday = subnutrientnumpy(udays)
        return proteinlist, carblist, fatlist, calorieslist,thatday
    else:
        udays = int(udays)
        proteinlist, carblist, fatlist,calorieslist,thatday = subnutrientnumpy(udays)
        return proteinlist, carblist, fatlist, calorieslist,thatday
def nutrientarray():
    proteinlist, carblist, fatlist, calorieslist,thatday = nutrientnumpy()
    proteinarray = np.array(proteinlist)
    carbarray = np.array(carblist)
    fatarray = np.array(fatlist)    
    caloriesarray = np.array(calorieslist)
    return proteinarray, carbarray, fatarray, caloriesarray
def nutrientmean_all(proteinarray, carbarray, fatarray, caloriesarray):
    return proteinarray.mean(), carbarray.mean(), fatarray.mean(), caloriesarray.mean()
def nutrientstd_all(proteinarray, carbarray, fatarray, caloriesarray):
    return proteinarray.std(), carbarray.std(), fatarray.std(), caloriesarray.std()
def calostd_all():
    proteinarray, carbarray, fatarray, caloriesarray = nutrientarray()
    proteinstd, carbstd, fatstd, caloriesstd = nutrientstd_all(proteinarray, carbarray, fatarray, caloriesarray)
    proteinmean, carbmean, fatmean, caloriesmean = nutrientmean_all(proteinarray, carbarray, fatarray, caloriesarray)

    protein_cv = proteinstd / proteinmean if proteinmean != 0 else 0
    carb_cv = carbstd / carbmean if carbmean != 0 else 0
    fat_cv = fatstd / fatmean if fatmean != 0 else 0
    calories_cv = caloriesstd / caloriesmean if caloriesmean != 0 else 0
    return protein_cv, carb_cv, fat_cv, calories_cv
def difftarget_all():
    proteinarray, carbarray, fatarray, caloriesarray = nutrientarray()
    proteinmean, carbmean, fatmean, caloriesmean = nutrientmean_all(proteinarray, carbarray, fatarray, caloriesarray)
    print(f"Overall calo: {caloriesmean}/{currentuser.caloriesadvice()}")
    print(f"Overall protein: {proteinmean}/{currentuser.proteinadvice()}")
def cv_label(cv):
    if cv < 0.15:
        return "khá ổn định"
    elif cv < 0.30:
        return "hơi thất thường"
    else:
        return "biến động mạnh"
def chartstat():
    proteinlist, carblist, fatlist, calorieslist,thatday = nutrientnumpy()
    plt.plot(thatday, calorieslist, marker = "o")
    plt.xlabel("Ngày")
    plt.ylabel("Calories")
    plt.axhline(y=currentuser.caloriesadvice(), color = "red", linestyle = "-",label = "your calories aim")
    plt.gcf().autofmt_xdate()
    plt.show()
def statnumpy():
    while True:
        print("""
        ===== NUTRITION STATS =====
        1. Show average (mean)
        2. Show variation (std)
        3. Show consistency (CV %)
        4. Compare to your target
        5. See chart
        6. Exit
        ============================
        """)
        choice = input_int("Choose an option: ")

        if choice == 1:
            proteinarray, carbarray, fatarray, caloriesarray = nutrientarray()
            protein, carb, fat, calories = nutrientmean_all(proteinarray, carbarray, fatarray, caloriesarray)
            print(f"Protein: {protein:.1f}g | Carb: {carb:.1f}g | Fat: {fat:.1f}g | Calories: {calories:.1f}")
        elif choice == 2:
            proteinarray, carbarray, fatarray, caloriesarray = nutrientarray()
            protein, carb, fat, calories = nutrientstd_all(proteinarray, carbarray, fatarray, caloriesarray)
            print(f"Protein: {protein:.1f}g | Carb: {carb:.1f}g | Fat: {fat:.1f}g | Calories: {calories:.1f}")
        elif choice == 3:
            protein_cv, carb_cv, fat_cv, calories_cv = calostd_all()
            print(f"Protein consistency: {protein_cv*100:.1f}% ({cv_label(protein_cv)})")
            print(f"Carb consistency:    {carb_cv*100:.1f}% ({cv_label(carb_cv)})")
            print(f"Fat consistency:     {fat_cv*100:.1f}% ({cv_label(fat_cv)})")
            print(f"Calorie consistency: {calories_cv*100:.1f}% ({cv_label(calories_cv)})")
        elif choice == 4:
            difftarget_all()
        elif choice == 5:
            chartstat()
        elif choice == 6:
            print("you exit")
            return
        else:
            print("invalid")
def main():
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
            printlog(logs)
        elif userchoice == 4:
            viewuserstat()
        elif userchoice == 5:
            user.stat()
        elif userchoice == 6:
            statnumpy()
        elif userchoice == 7:
            save_user(currentuser)
            save_entry(log_today)
            exit()
        else:
            print('invalid')
main()
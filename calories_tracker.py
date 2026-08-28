from datetime import date
import json
currentuser = None
class entry():
    def __init__(self, name,weight, entrydate =None):
        self.name = name
        self.weight = weight
        self.date = entrydate if entrydate is not None else date.today()
        entry.macroscaculated(self)
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
            "entrydate": str(self.date),
            "weight": self.weight
        }
    @classmethod
    def fromdict(cls, data):
        new_entry = cls(
            name = data["name"],
            entrydate = date.fromisoformat(data["entrydate"]),
            weight = data["weight"],
        )
        return new_entry
    @classmethod
    def entry_today(cls):
        meal = cls(
            name = input("type food name: "),
            weight = input_float("type weight g: "),
            entrydate = date.fromisoformat(input("type date (YYYYMMDD): "))
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
        weight = input_float("weight in kg: ")
        height = input_float("height in cm: ")
        age = input_int("age: ")
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
    except FileNotFoundError:
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
    with open("log.json", "r") as file:
        data = json.load(file)
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

#logic try/except
def input_float(message):
    while True:
        try:
            return float(input(message))
        except ValueError:
            return print("invalid number")
def input_int(message):
    while True:
        try:
            return int(input(message))
        except ValueError:
            return print("invalid number")
log_today = []
#showing, printing
def show_menu():
    print("""
========================================
       CALORIE TRACKER - v1
========================================
  1. Add meal
  2. View today's log
  3. Your stat
  4. Change your stat
  5. Save & exit
========================================
""")
    
def viewtodaylog():
    caloriesneeded = currentuser.caloriesadvice()
    proteineeded = currentuser.proteinadvice()
    todayprotein = 0
    todaycalories = 0
    if len(log_today) == 0:
        print("No log found for today.")
        return

    print("Today's food log:")
    for i, log in enumerate(log_today, start=1):
        print(f"{i}. {log.name} ({log.weight}g)")
        print(f"   protein: {log.protein:.1f}g, carb: {log.carb:.1f}g, fat: {log.fat:.1f}g, calories: {log.calories:.1f}kcal")
        todayprotein += log.protein
        todaycalories += log.calories
    if todaycalories >= caloriesneeded:
        print(f"exceeding calories: {todaycalories - caloriesneeded}")
    if todayprotein >= proteineeded:
        print(f"exceeding protein: {todayprotein - proteineeded}")
    if caloriesneeded > todaycalories:
        print(f"calories left: {caloriesneeded - todaycalories}")
    if proteineeded > todayprotein:
        print(f"protein left: {proteineeded - todayprotein}")

def viewuserstat():
    global currentuser
    goal_map = {1: "Lose weight", 2: "Maintain weight", 3: "Gain weight"}
    print(f"Goal: {goal_map[currentuser.goal]}")
    print(f"Name: {currentuser.name}")
    print(f"Age: {currentuser.age}")
    print(f"Weight: {currentuser.weight} kg")
    print(f"Height: {currentuser.height} cm")
    print(f"Sex: {currentuser.sex}")
    print(f"Activity level: {currentuser.workout}")
    print(f"Goal: {currentuser.goal}")
def main():
    load_user()
    while True:
        show_menu()
        userchoice = input_float("type number: ")
        if userchoice == 1:
            log = entry.entry_today()
            log_today.append(log)  
        elif userchoice == 2:
            viewtodaylog()
        elif userchoice == 3:
            viewuserstat()
        elif userchoice == 4:
            user.stat()
        elif userchoice == 5:
            save_user(currentuser)
            save_entry(log_today)
            exit()
main()        
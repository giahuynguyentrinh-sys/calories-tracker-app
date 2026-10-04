import streamlit as st
from calories_tracker import *
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
def page_profile():
    st.title("Hồ sơ")

    msg = st.session_state.pop("profile_msg", None)
    if msg:
        st.success(msg)

    u = load_user()

    workout_options = {
        "Ít vận động (1.2)": 1.2,
        "Tập nhẹ 1-3 buổi/tuần (1.375)": 1.375,
        "Tập vừa 3-5 buổi/tuần (1.55)": 1.55,
        "Tập nặng 6-7 buổi/tuần (1.725)": 1.725,
        "Rất nặng / lao động chân tay (1.9)": 1.9,
    }
    goal_options = {"Giảm cân": 1, "Giữ cân": 2, "Tăng cân": 3}

    # giá trị mặc định: lấy từ hồ sơ cũ, nếu chưa có thì dùng số gợi ý
    d_name = u.name if u else ""
    d_age = u.age if u else 18
    d_height = float(u.height) if u else 165.0
    d_weight = float(u.weight) if u else 60.0
    d_sex = u.sex if u else "male"
    d_workout = u.workout if u else 1.2
    d_goal = u.goal if u else 2

    col_img, col_form = st.columns([1, 2])

    # ---------- Ảnh ----------
    with col_img:
        avatar = load_avatar()
        if avatar:
            st.image(avatar, width=180)
        else:
            st.caption("Chưa có ảnh")
        photo = st.file_uploader("Đổi ảnh đại diện", type=["png", "jpg", "jpeg"])

    # ---------- Thông tin ----------
    with col_form:
        with st.form("profile_form"):
            name = st.text_input("Tên", value=d_name)
            c1, c2 = st.columns(2)
            age = c1.number_input("Tuổi", 1, 120, int(d_age))
            sex = c2.selectbox("Giới tính", ["male", "female"],
                               index=["male", "female"].index(d_sex))
            c3, c4 = st.columns(2)
            height = c3.number_input("Chiều cao (cm)", 50.0, 250.0, d_height, step=0.5)
            weight = c4.number_input("Cân nặng (kg)", 20.0, 200.0, d_weight, step=0.1)

            workout_label = st.selectbox(
                "Mức vận động", list(workout_options),
                index=list(workout_options.values()).index(d_workout))
            goal_label = st.radio(
                "Mục tiêu", list(goal_options), horizontal=True,
                index=list(goal_options.values()).index(d_goal))

            submitted = st.form_submit_button("Lưu hồ sơ")

    if submitted:
        try:
            new_user = user(name, weight, height, age, sex,
                            workout_options[workout_label],
                            goal_options[goal_label])
            save_user(new_user)
            if photo is not None:
                save_avatar(photo)
            st.session_state["profile_msg"] = "Đã lưu hồ sơ"
            st.rerun()
        except ValueError as e:
            st.error(str(e))

    # ---------- Xem trước kết quả ----------
    u = load_user()
    if u:
        st.subheader("Chỉ số của bạn")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("BMR", f"{u.bmr():.0f} kcal")
        m2.metric("TDEE", f"{u.tdee():.0f} kcal")
        m3.metric("Mục tiêu calories", f"{u.caloriesadvice():.0f} kcal")
        m4.metric("Mục tiêu protein", f"{u.proteinadvice():.0f} g")
def page_home():
    st.title("Hôm nay")

    u = load_user()
    if u is None:
        st.warning("Chưa có hồ sơ nên chưa tính được mục tiêu. Vào trang Hồ sơ để tạo.")
        return

    totals = today_totals()
    targets = macro_targets(u)
    units = {"calories": "kcal", "protein": "g", "carb": "g", "fat": "g"}
    st.subheader("Đã ăn hôm nay")
    today_logs = get_logs_by_date(date.today())
    if not today_logs:
        st.caption("Chưa có bữa nào")
    for log in today_logs:
        st.write(f"**{log['mealtype']}**: {log['name']}, {log['weight']}g")
    def card(container, key, label):
        eaten, goal = totals[key], targets[key]
        pct = eaten / goal if goal > 0 else 0
        container.metric(label, f"{eaten:.0f} / {goal:.0f} {units[key]}")
        container.progress(min(pct, 1.0), text=f"{pct * 100:.0f}%")
        if eaten > goal:
            container.error(f"Over eating {eaten - goal:.0f} {units[key]}")
        else:
            container.caption(f"Còn {goal - eaten:.0f} {units[key]}")

    if totals["calories"] == 0:
        st.info("Hôm nay bạn chưa ăn gì. Ghi bữa đầu tiên thôi!")

    card(st, "calories", "Calories")

    c1, c2, c3 = st.columns(3)
    card(c1, "protein", "Protein")
    card(c2, "carb", "Carb")
    card(c3, "fat", "Fat")
def page_database():
    st.title("Database")

    msg = st.session_state.pop("db_msg", None)   # thông báo sau khi rerun
    if msg:
        st.success(msg)

    foods = read_foods()
    tab = st.radio("Chế độ", ["Tra cứu", "Thêm món", "Xóa món"],
                    horizontal=True, key="db_tab", label_visibility="collapsed")

    # ---------- Tra cứu ----------
    if tab == "Tra cứu":
        keyword = st.text_input("Tìm món", placeholder="Gõ một phần tên món...")
        if not foods:
            st.info("Database chưa có món nào")
        else:
            df = pd.DataFrame.from_dict(foods, orient="index")
            df["kcal"] = df["protein"] * 4 + df["carb"] * 4 + df["fat"] * 9
            df.index.name = "Món"
            df = df.rename(columns={
                "protein": "Protein (g/100g)",
                "carb": "Carb (g/100g)",
                "fat": "Fat (g/100g)",
                "kcal": "Kcal/100g",
            })
            if keyword.strip():
                df = df[df.index.str.contains(keyword.strip(), case=False, regex=False)]
            if df.empty:
                st.warning("Không tìm thấy món nào")
            else:
                st.caption(f"{len(df)} món")
                st.dataframe(df.round(1))

    # ---------- Thêm ----------
    elif tab == "Thêm món":
        with st.form("add_food_form"):
            name = st.text_input("Tên món")
            c1, c2, c3 = st.columns(3)
            protein = c1.number_input("Protein (g/100g)", 0.0, 10000.0, step=0.1)
            carb = c2.number_input("Carb (g/100g)", 0.0, 10000.0, step=0.1)
            fat = c3.number_input("Fat (g/100g)", 0.0, 10000.0, step=0.1)
            overwrite = st.checkbox("Ghi đè nếu món đã tồn tại")
            submitted = st.form_submit_button("Thêm món")

        if submitted:
            clean = name.strip()
            if clean in foods and not overwrite:
                st.error(f"'{clean}' đã có trong database. Tick 'Ghi đè' nếu muốn cập nhật.")
            else:
                try:
                    add_food(clean, protein, carb, fat)
                    st.session_state["db_msg"] = f"Đã lưu món '{clean}'"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    # ---------- Xóa ----------
    elif tab == "Xóa món":
        if not foods:
            st.info("Database chưa có món nào")
        else:
            target = st.selectbox("Chọn món cần xóa", sorted(foods))
            if target in foods_in_use():
                st.warning("Món này đang có trong nhật ký ăn nên chưa xóa được.")
            confirm = st.checkbox(f"Tôi chắc chắn muốn xóa '{target}'")
            if st.button("Xóa món", disabled=not confirm):
                try:
                    delete_food(target)
                    st.session_state["db_msg"] = f"Đã xóa món '{target}'"
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
def page_add_meal():
    st.title("Thêm bữa ăn")

    msg = st.session_state.pop("meal_msg", None)
    if msg:
        st.success(msg)

    foods = read_foods()

    # Không dùng st.form để phần macro bên dưới cập nhật ngay khi đổi món/khối lượng
    if foods:
        name = st.selectbox("Chọn món (gõ để tìm nhanh)", sorted(foods))
    else:
        name = None
        st.info("Database chưa có món nào.")

    if st.button("Món không có trong danh sách? Nhập thủ công"):
        st.session_state["goto"] = "Database món ăn"
        st.session_state["db_tab"] = "Thêm món"
        st.rerun()

    if name is None:
        return

    c1, c2, c3 = st.columns(3)
    weight = c1.number_input("Khối lượng (g)", 1.0, 4999.0, 100.0, step=10.0)
    mealtype = c2.selectbox("Loại bữa", valid_types,
                            index=valid_types.index(entry.guessmealtype()))
    d = c3.date_input("Ngày", value=date.today(), max_value=date.today())

    # Macro tính ngay lập tức
    food = foods[name]
    ratio = weight / 100
    p = food["protein"] * ratio
    c = food["carb"] * ratio
    f = food["fat"] * ratio
    kcal = p * 4 + c * 4 + f * 9

    st.subheader("Dinh dưỡng của phần này")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Calories", f"{kcal:.0f} kcal")
    m2.metric("Protein", f"{p:.1f} g")
    m3.metric("Carb", f"{c:.1f} g")
    m4.metric("Fat", f"{f:.1f} g")

    if st.button("Lưu bữa ăn", type="primary"):
        try:
            save_entry(entry(name, weight, mealtype, d))
            st.session_state["meal_msg"] = f"Đã thêm {name}, {weight:.0f}g vào {mealtype}"
            st.rerun()
        except ValueError as e:
            st.error(str(e))
def page_log():
    st.title("Nhật ký ăn uống")

    msg = st.session_state.pop("log_msg", None)
    if msg:
        st.success(msg)

    d = st.date_input("Chọn ngày", value=date.today(), max_value=date.today())
    day_logs = get_logs_by_date(d)

    if not day_logs:
        st.info("Không có bữa ăn nào ngày này")
        return

    for i, log in enumerate(day_logs):
        col1, col2 = st.columns([4, 1])
        col1.write(f"**{log['mealtype']}**: {log['name']}, {log['weight']}g")
        if col2.button("Xóa", key=f"del_{i}"):
            delete_log(d, i)
            st.session_state["log_msg"] = f"Đã xóa '{log['name']}'"
            st.rerun()
def page_stats():
    st.title("Thống kê")

    data, dtb = logpandas()
    if data.empty:
        st.warning("Chưa có dữ liệu")
        return

    periods = {"7 ngày": 7, "14 ngày": 14, "30 ngày": 30,
               "90 ngày": 90, "1 năm": 365, "Tất cả": None}

    col1, col2 = st.columns(2)
    unit = col1.radio("Chất", ["protein", "carb", "fat", "calories"], horizontal=True)
    label = col2.selectbox("Khoảng thời gian", list(periods.keys()))

    udays = periods[label]
    if udays is None:   # "Tất cả": tính số ngày thật từ ngày ăn đầu tiên
        first = pd.to_datetime(data["date"]).min()
        udays = max((pd.Timestamp(date.today()) - first).days, 1)

    nt, ymean, zstd, qcv = subnutrientnumpy(udays, data, dtb)
    if nt.empty:
        st.warning("Không có dữ liệu trong khoảng này")
        return

    # Biểu đồ
    fig, ax = plt.subplots()
    ax.plot(nt.index.to_timestamp(), nt[unit], marker="o")
    ax.set_title(f"Sum of {unit}")
    ax.set_xlabel("Time")
    ax.set_ylabel(unit)
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)

    # Dữ liệu thô
    st.subheader("Dữ liệu thô")
    table = pd.DataFrame({
        "Sum": nt[unit],
        "Mean": ymean[unit],
        "Std": zstd[unit],
        "CV %": qcv[unit],
    })
    table.index = table.index.astype(str)
    st.dataframe(table)
    st.subheader("Mô tả")
    st.dataframe(nt[unit].describe())
    with st.expander("Các chỉ số này nghĩa là gì?"):
        st.write("**Sum**: tổng lượng chất trong một kỳ.")
        st.write("**Mean**: trung bình của một kỳ.")
        st.write("**Std**: độ lệch chuẩn, số càng lớn thì các bữa càng chênh nhau nhiều.")
        st.write("**CV %**: Std chia Mean nhân 100, dùng để so độ biến động giữa các chất có đơn vị lớn nhỏ khác nhau.")
st.sidebar.title("Menu")
if "goto" in st.session_state:
    st.session_state["page"] = st.session_state.pop("goto")
choice = st.sidebar.radio(
    "Chọn trang",
    ["Trang chủ", "Hồ sơ", "Thêm bữa ăn", "Nhật ký hôm nay", "Thống kê", "Database món ăn"], key = "page")

if choice == "Trang chủ":
    page_home()
elif choice == "Hồ sơ":
    page_profile()
elif choice == "Thêm bữa ăn":
    page_add_meal()
elif choice == "Nhật ký hôm nay":
    page_log()
elif choice == "Thống kê":
    page_stats()
elif choice == "Database món ăn":
    page_database()

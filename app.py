import streamlit as st
from calories_tracker import *
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
def page_database():
    st.title("Database")

    msg = st.session_state.pop("db_msg", None)   # thông báo sau khi rerun
    if msg:
        st.success(msg)

    foods = read_foods()
    tab_search, tab_add, tab_delete = st.tabs(["Tra cứu", "Thêm món", "Xóa món"])

    # ---------- Tra cứu ----------
    with tab_search:
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
    with tab_add:
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
    with tab_delete:
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

    # Mô tả
    st.subheader("Mô tả")
    st.dataframe(nt[unit].describe())
    with st.expander("Các chỉ số này nghĩa là gì?"):
        st.write("**Sum**: tổng lượng chất trong một kỳ.")
        st.write("**Mean**: trung bình của một kỳ.")
        st.write("**Std**: độ lệch chuẩn, số càng lớn thì các bữa càng chênh nhau nhiều.")
        st.write("**CV %**: Std chia Mean nhân 100, dùng để so độ biến động giữa các chất có đơn vị lớn nhỏ khác nhau.")
st.sidebar.title("Menu")
choice = st.sidebar.radio(
    "Chọn trang",
    ["Hồ sơ", "Thêm bữa ăn", "Nhật ký hôm nay", "Thống kê", "Database món ăn"]
)
if choice == "Hồ sơ":
    st.title("Hồ sơ")
    st.write("Trang hồ sơ, sẽ làm sau")
elif choice == "Thêm bữa ăn":
    st.title("Thêm bữa ăn")
    st.write("Trang thêm bữa ăn, sẽ làm sau")
elif choice == "Nhật ký hôm nay":
    st.title("Nhật ký hôm nay")
    st.write("Trang nhật ký, sẽ làm sau")
elif choice == "Thống kê":
    page_stats()
elif choice == "Database món ăn":
    page_database()

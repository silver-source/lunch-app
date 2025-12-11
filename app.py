import streamlit as st
import pandas as pd
import datetime
import os

# ------------------------------------------------------
# 1. 설정 및 데이터
# ------------------------------------------------------
YEAR = 2026
DATA_FILE = "lunch_db.csv"
ADMIN_PASSWORD = "1234"  # 관리자 비밀번호 (원하는 걸로 바꾸세요)

# 공휴일
HOLIDAYS = [
    "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18",
    "2026-03-02", "2026-05-05", "2026-05-25", "2026-06-03",
    "2026-06-06", "2026-08-17", "2026-09-24", "2026-09-25",
    "2026-09-26", "2026-09-28", "2026-10-05", "2026-10-09",
    "2026-12-25"
]

# 직원 명단
EMPLOYEES = [
    ("경지", "최정우"), ("경지", "송은경"), ("경지", "강남경"), ("경지", "안준영"), ("경지", "김대환"),
    ("경지", "장경선"), ("경지", "김민주3"), ("경지", "이소라"), ("경지", "이여린"),
    ("라오", "이재명"), ("라오", "정성주"), ("라오", "이다희"), ("라오", "김다희"), ("라오", "우희강"),
    ("라오", "임준우"), ("라오", "양해근"), ("라오", "한주연"), ("라오", "한재혁"), ("라오", "나우제"),
    ("기획", "정지윤"), ("기획", "이승희"), ("기획", "이무일"), ("기획", "김지은B"), ("기획", "조창호"), ("기획", "이다빈"),
    ("고만실", "한경호"), ("고만실", "유호영"), ("고만실", "한은비"), ("고만실", "김혜지2"), ("고만실", "이용석"),
    ("고만실", "최윤아2"), ("고만실", "전은경"),
    ("외과", "김수민"), ("외과", "홍진호"), ("외과", "김용수1"), ("외과", "안예지"), ("외과", "류승지"),
    ("외과", "최세인"), ("외과", "전혜정"), ("외과", "김지호"), ("외과", "임수연"),
    ("보철과", "송한솔"), ("보철과", "우지연"), ("보철과", "안혜빈"), ("보철과", "조현정"), ("보철과", "문수정"),
    ("보철과", "조아형"), ("보철과", "조원희"), ("보철과", "심현지"), ("보철과", "하예린"), ("보철과", "박새미"),
    ("보철과", "김민주"), ("보철과", "김기윤"), ("보철과", "김민지4"),
    ("교정과", "이승훈"), ("교정과", "김다솜"), ("교정과", "김한울"), ("교정과", "전현주"), ("교정과", "서다빈"),
    ("기공실", "박광수"), ("기공실", "고대성"), ("기공실", "송현진"), ("기공실", "김영주"), ("기공실", "김민우"),
    ("기공실", "유경민"), ("기공실", "강민주"), ("기공실", "이지은2"), ("기공실", "김윤아"), ("기공실", "김시연"),
    ("데스크", "조슬기"), ("데스크", "양지혜"), ("데스크", "이하린"),
    ("상담실", "이종훈2"), ("상담실", "박정혜"), ("상담실", "차정애"), ("상담실", "김유영"), ("상담실", "김이연"), ("상담실", "여봉하"),
    ("관리실", "김종환"), ("관리실", "정병철"), ("관리실", "차계순"),
    ("소독실", "이미선"), ("소독실", "이순심2"), ("소독실", "남윤지"), ("소독실", "정희경")
]
DEPARTMENTS = sorted(list(set([e[0] for e in EMPLOYEES])))

# ------------------------------------------------------
# 2. 로직 함수
# ------------------------------------------------------
def is_holiday_or_weekend(date_obj):
    date_str = date_obj.strftime("%Y-%m-%d")
    if date_obj.weekday() >= 5: return True
    if date_str in HOLIDAYS: return True
    return False

def find_nearest_workday(target_date):
    if not is_holiday_or_weekend(target_date): return target_date
    offset = 1
    while True:
        prev_day = target_date - datetime.timedelta(days=offset)
        if not is_holiday_or_weekend(prev_day): return prev_day
        next_day = target_date + datetime.timedelta(days=offset)
        if not is_holiday_or_weekend(next_day): return next_day
        offset += 1

def get_hamburger_days(year, month):
    target_days = [10, 25]
    burger_dates = []
    for day in target_days:
        try:
            base_date = datetime.date(year, month, day)
            actual_date = find_nearest_workday(base_date)
            burger_dates.append(actual_date.strftime("%Y-%m-%d"))
        except ValueError: pass
    return burger_dates

def load_data():
    if os.path.exists(DATA_FILE): return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Dept", "Name", "Menu"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# ------------------------------------------------------
# 3. 앱 화면
# ------------------------------------------------------
st.set_page_config(page_title="식사 메뉴 선택", layout="wide")
st.title(f"🍱 {YEAR}년 점심 식사 선택")

# [사이드바] 로그인 & 관리자 모드
st.sidebar.header("👤 내 정보 선택")
selected_dept = st.sidebar.selectbox("부서", DEPARTMENTS)
names_in_dept = [e[1] for e in EMPLOYEES if e[0] == selected_dept]
selected_name = st.sidebar.selectbox("이름", names_in_dept)

st.sidebar.markdown("---")
# 관리자 로그인 섹션 (접었다 폈다 가능)
with st.sidebar.expander("🔐 관리자 모드 (클릭)"):
    input_pw = st.text_input("관리자 비밀번호", type="password")
    is_admin = (input_pw == ADMIN_PASSWORD)
    if is_admin:
        st.success("관리자 권한 확인됨")

# [메인] 날짜 생성
current_month = datetime.datetime.now().month
selected_month = st.selectbox("월(Month) 선택", range(1, 13), index=current_month-1)

start_date = datetime.date(YEAR, selected_month, 1)
if selected_month == 12: next_month_date = datetime.date(YEAR + 1, 1, 1)
else: next_month_date = datetime.date(YEAR, selected_month + 1, 1)

burger_days = get_hamburger_days(YEAR, selected_month)
df_db = load_data()

display_data = []
curr = start_date
while curr < next_month_date:
    d_str = curr.strftime("%Y-%m-%d")
    day_kor = ["월", "화", "수", "목", "금", "토", "일"][curr.weekday()]
    status = "평일"
    menu = "선택X"
    disabled = False
    
    if is_holiday_or_weekend(curr):
        status = "🔴 휴일"
        menu = "-"
        disabled = True
    elif d_str in burger_days:
        status = "🍔 햄버거데이"
        menu = "햄버거"
        disabled = True
    
    existing = df_db[(df_db['Date']==d_str) & (df_db['Dept']==selected_dept) & (df_db['Name']==selected_name)]
    if not existing.empty and not disabled:
        menu = existing.iloc[0]['Menu']
    
    display_data.append({"날짜": d_str, "요일": day_kor, "구분": status, "메뉴": menu, "_disabled": disabled})
    curr += datetime.timedelta(days=1)

df_view = pd.DataFrame(display_data)

st.info(f"👋 **{selected_dept} {selected_name}**님, {selected_month}월 메뉴를 선택해주세요.")

edited_df = st.data_editor(
    df_view,
    column_config={
        "날짜": st.column_config.TextColumn("날짜", disabled=True),
        "요일": st.column_config.TextColumn("요일", disabled=True),
        "구분": st.column_config.TextColumn("구분", disabled=True),
        "메뉴": st.column_config.SelectboxColumn("메뉴 선택", options=["일반식", "샐러드", "선택X"], required=True),
        "_disabled": None
    },
    disabled=["날짜", "요일", "구분"],
    hide_index=True,
    use_container_width=True,
    height=600
)

if st.button("💾 저장하기", type="primary"):
    new_rows = []
    for idx, row in edited_df.iterrows():
        menu_val = row['메뉴']
        if "햄버거" in row['구분']: menu_val = "햄버거"
        if "휴일" not in row['구분']:
            new_rows.append({"Date": row['날짜'], "Dept": selected_dept, "Name": selected_name, "Menu": menu_val})
            
    month_start_str = start_date.strftime("%Y-%m-%d")
    month_end_str = (next_month_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    mask_keep = ~((df_db['Date']>=month_start_str) & (df_db['Date']<=month_end_str) & (df_db['Dept']==selected_dept) & (df_db['Name']==selected_name))
    df_final = pd.concat([df_db[mask_keep], pd.DataFrame(new_rows)], ignore_index=True)
    save_data(df_final)
    st.success("✅ 저장 완료!")

# ------------------------------------------------------
# 관리자 전용 화면 (비밀번호 맞을 때만 보임)
# ------------------------------------------------------
if is_admin:
    st.markdown("---")
    st.error("🔐 관리자 전용 구역입니다.")
    if os.path.exists(DATA_FILE):
        df_all = pd.read_csv(DATA_FILE)
        mask_m = (df_all['Date'] >= start_date.strftime("%Y-%m-%d")) & (df_all['Date'] < next_month_date.strftime("%Y-%m-%d"))
        df_m = df_all[mask_m]
        
        tab1, tab2 = st.tabs(["📊 집계표", "📋 상세 명단"])
        
        with tab1:
            if not df_m.empty:
                pivot = df_m.pivot_table(index="Date", columns="Menu", values="Name", aggfunc="count", fill_value=0)
                st.dataframe(pivot, use_container_width=True)
            else: st.write("데이터 없음")
            
        with tab2:
            st.dataframe(df_m.sort_values(["Date", "Dept"]))
            # CSV 다운로드 버튼
            csv = df_m.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 엑셀용 CSV 다운로드", csv, "lunch_data.csv", "text/csv")
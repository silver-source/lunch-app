import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------------------------------
# 1. 설정 및 데이터
# ------------------------------------------------------
YEAR = 2026
SHEET_NAME = "lunch_db"
ADMIN_PASSWORD = "1234" 

# 공휴일
HOLIDAYS = [
    "2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18",
    "2026-03-02", "2026-05-05", "2026-05-25", "2026-06-03",
    "2026-06-06", "2026-08-17", "2026-09-24", "2026-09-25",
    "2026-09-26", "2026-09-28", "2026-10-05", "2026-10-09",
    "2026-12-25"
]

# ------------------------------------------------------
# [업데이트됨] 직원 명단 (지점, 부서, 이름+직책)
# ------------------------------------------------------
EMPLOYEES = [
    # --- 강남 지점 ---
    ("강남", "경영지원실", "최정우 병원장"),
    ("강남", "경영지원실", "송은경 병원장"),
    ("강남", "경영지원실", "강남경 팀장"),
    ("강남", "경영지원실", "안준영 팀장"),
    ("강남", "경영지원실", "김대환 대리"),
    ("강남", "경영지원실", "이소라"),
    ("강남", "경영지원실", "장경선 대리"),
    ("강남", "경영지원실", "이여린"),
    ("강남", "경영지원실", "김민주 대리"),
    ("강남", "병원기획팀", "정지윤 과장"),
    ("강남", "병원기획팀", "이승희 대리"),
    ("강남", "병원기획팀", "이무일 대리"),
    ("강남", "병원기획팀", "김지은 대리"),
    ("강남", "병원기획팀", "조창호 대리"),
    ("강남", "병원기획팀", "이다빈"),
    ("강남", "의료진", "이승훈"),
    ("강남", "의료진", "이종훈"),
    ("강남", "의료진", "김수민"),
    ("강남", "의료진", "홍진호"),
    ("강남", "의료진", "우지연"),
    ("강남", "의료진", "송한솔"),
    ("강남", "의료진", "박정혜"),
    ("강남", "의료진", "이희진"),
    ("강남", "의료진", "안혜빈"),
    ("강남", "라이브오랄스", "이재명 실장"),
    ("강남", "라이브오랄스", "정성주 팀장"),
    ("강남", "라이브오랄스", "이다희 대리"),
    ("강남", "라이브오랄스", "김다희"),
    ("강남", "라이브오랄스", "우희강 과장"),
    ("강남", "라이브오랄스", "임준우"),
    ("강남", "라이브오랄스", "양해근 과장"),
    ("강남", "라이브오랄스", "한주연"),
    ("강남", "라이브오랄스", "한재혁"),
    ("강남", "라이브오랄스", "나우제 대리"),
    ("강남", "라이브오랄스", "이가은 대리"),
    ("강남", "고객만족실", "한경호 팀장"),
    ("강남", "고객만족실", "유호영"),
    ("강남", "고객만족실", "한은비"),
    ("강남", "고객만족실", "김혜지"),
    ("강남", "고객만족실", "이용석"),
    ("강남", "고객만족실", "최윤아"),
    ("강남", "고객만족실", "전은경"),
    ("강남", "데스크", "조슬기 팀장"),
    ("강남", "데스크", "양지혜"),
    ("강남", "데스크", "이하린"),
    ("강남", "상담실", "차정애 총괄실장"),
    ("강남", "상담실", "김유영"),
    ("강남", "상담실", "김이연"),
    ("강남", "상담실", "여봉하"),
    ("강남", "상담실", "오영주"),
    ("강남", "보철과", "조현정 팀장"),
    ("강남", "보철과", "문수정 부팀장"),
    ("강남", "보철과", "조아형"),
    ("강남", "보철과", "조원희"),
    ("강남", "보철과", "심현지"),
    ("강남", "보철과", "하예린"),
    ("강남", "보철과", "박새미"),
    ("강남", "보철과", "김민주"),
    ("강남", "보철과", "김기윤"),
    ("강남", "보철과", "김민지4"),
    ("강남", "교정과", "김다솜 팀장"),
    ("강남", "교정과", "김한울 부팀장"),
    ("강남", "교정과", "전현주"),
    ("강남", "교정과", "서다빈"),
    ("강남", "외과", "김용수 팀장"),
    ("강남", "외과", "안예지 부팀장"),
    ("강남", "외과", "류승지"),
    ("강남", "외과", "최세인"),
    ("강남", "외과", "전혜정"),
    ("강남", "외과", "김지호"),
    ("강남", "외과", "임수연"),
    ("강남", "기공실", "박광수 팀장"),
    ("강남", "기공실", "고대성 부팀장"),
    ("강남", "기공실", "송현진"),
    ("강남", "기공실", "김영주"),
    ("강남", "기공실", "김민우"),
    ("강남", "기공실", "유경민"),
    ("강남", "기공실", "강민주"),
    ("강남", "기공실", "이지은"),
    ("강남", "기공실", "김윤아"),
    ("강남", "기공실", "김시연"),
    ("강남", "소독실", "이미선"),
    ("강남", "소독실", "이순심"),
    ("강남", "소독실", "남윤지"),
    ("강남", "소독실", "정희경"),
    ("강남", "관리실", "김종환"),
    ("강남", "관리실", "정병철"),
    ("강남", "관리실", "차계순"),

    # --- 인천 지점 ---
    ("인천", "경영지원실", "최정우 병원장"),
    ("인천", "경영지원실", "송은경 병원장"),
    ("인천", "경영지원실", "강남경 팀장"),
    ("인천", "경영지원실", "안준영 팀장"),
    ("인천", "경영지원실", "김대환 대리"),
    ("인천", "경영지원실", "이소라"),
    ("인천", "경영지원실", "장경선 대리"),
    ("인천", "병원기획팀", "정지윤 과장"),
    ("인천", "병원기획팀", "이승희 대리"),
    ("인천", "병원기획팀", "이무일 대리"),
    ("인천", "병원기획팀", "김지은 대리"),
    ("인천", "병원기획팀", "조창호 대리"),
    ("인천", "병원기획팀", "이다빈"),
    ("인천", "의료진", "홍정표"),
    ("인천", "의료진", "송희태"),
    ("인천", "의료진", "김미나"),
    ("인천", "의료진", "이시원"),
    ("인천", "의료진", "이영훈"),
    ("인천", "의료진", "박선아"),
    ("인천", "의료진", "배상필"),
    ("인천", "의료진", "양대승"),
    ("인천", "의료진", "이희진"),
    ("인천", "의료진", "신혜영"),
    ("인천", "의료진", "안혜빈"),
    ("인천", "데스크", "김민지 팀장"),
    ("인천", "데스크", "최운희"),
    ("인천", "데스크", "손효주"),
    ("인천", "상담실", "차정애 총괄실장"),
    ("인천", "상담실", "이아람"),
    ("인천", "상담실", "조미도"),
    ("인천", "상담실", "신영주"),
    ("인천", "상담실", "김희미"),
    ("인천", "보철과", "고지영 팀장"),
    ("인천", "보철과", "김예은B 부팀장"),
    ("인천", "보철과", "임연희 부팀장"),
    ("인천", "보철과", "한지윤"),
    ("인천", "보철과", "이수경"),
    ("인천", "보철과", "박지연"),
    ("인천", "보철과", "조진영"),
    ("인천", "보철과", "박한결"),
    ("인천", "보철과", "정어진"),
    ("인천", "보철과", "천지영"),
    ("인천", "보철과", "최은희"),
    ("인천", "보철과", "정하영"),
    ("인천", "교정과", "김민정 부팀장"),
    ("인천", "교정과", "김예은(교)"),
    ("인천", "교정과", "고은설"),
    ("인천", "교정과", "김현진"),
    ("인천", "교정과", "손민정"),
    ("인천", "외과", "박찬호 팀장"),
    ("인천", "외과", "김수민 부팀장"),
    ("인천", "외과", "박현지"),
    ("인천", "외과", "이은채"),
    ("인천", "외과", "전효진"),
    ("인천", "외과", "조홍화"),
    ("인천", "외과", "김동화"),
    ("인천", "기공실", "이성한 부팀장"),
    ("인천", "기공실", "박주희"),
    ("인천", "기공실", "임혜진 부팀장"),
    ("인천", "기공실", "김정현 부팀장"),
    ("인천", "기공실", "이정민"),
    ("인천", "기공실", "최준혁"),
    ("인천", "기공실", "이유진"),
    ("인천", "기공실", "이지선"),
    ("인천", "소독실", "최복숙"),
    ("인천", "소독실", "이혜경"),
    ("인천", "소독실", "오명자"),
    ("인천", "소독실", "유이재"),
]

# ------------------------------------------------------
# 2. 구글 시트 연결 함수
# ------------------------------------------------------
def get_google_sheet():
    credentials_dict = st.secrets["gcp_service_account"]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

def load_data():
    try:
        sheet = get_google_sheet()
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["Date", "Branch", "Dept", "Name", "Menu"])
        return pd.DataFrame(data)
    except Exception:
        return pd.DataFrame(columns=["Date", "Branch", "Dept", "Name", "Menu"])

def save_data(df):
    sheet = get_google_sheet()
    sheet.clear()
    sheet.append_row(df.columns.tolist())
    sheet.update(range_name=None, values=df.values.tolist())

# ------------------------------------------------------
# 3. 로직 함수
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

# ------------------------------------------------------
# 4. 앱 화면
# ------------------------------------------------------
st.set_page_config(page_title="식사 메뉴 선택", layout="wide")
st.title(f"🍱 {YEAR}년 점심 식사 선택")

# --- 사이드바: 3단계 선택 (지점 -> 부서 -> 이름) ---
st.sidebar.header("👤 내 정보 선택")

# 1. 지점 선택
BRANCHES = sorted(list(set([e[0] for e in EMPLOYEES])))
selected_branch = st.sidebar.selectbox("지점 선택", BRANCHES)

# 2. 부서 선택 (선택된 지점에 있는 부서만 표시)
DEPTS_IN_BRANCH = sorted(list(set([e[1] for e in EMPLOYEES if e[0] == selected_branch])))
selected_dept = st.sidebar.selectbox("부서 선택", DEPTS_IN_BRANCH)

# 3. 이름 선택 (선택된 지점+부서에 있는 이름만 표시)
NAMES_IN_DEPT = sorted(list(set([e[2] for e in EMPLOYEES if e[0] == selected_branch and e[1] == selected_dept])))
selected_name = st.sidebar.selectbox("이름 선택", NAMES_IN_DEPT)

st.sidebar.markdown("---")
with st.sidebar.expander("🔐 관리자 모드"):
    input_pw = st.text_input("관리자 비밀번호", type="password")
    is_admin = (input_pw == ADMIN_PASSWORD)
    if is_admin: st.success("관리자 권한 확인됨")

# --- 메인 화면 ---
current_month = datetime.datetime.now().month
selected_month = st.selectbox("월(Month) 선택", range(1, 13), index=current_month-1)

start_date = datetime.date(YEAR, selected_month, 1)
if selected_month == 12: next_month_date = datetime.date(YEAR + 1, 1, 1)
else: next_month_date = datetime.date(YEAR, selected_month + 1, 1)

burger_days = get_hamburger_days(YEAR, selected_month)

with st.spinner("데이터를 불러오는 중..."):
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
    
    # DB 매칭 조건 (지점, 부서, 이름)
    existing = df_db[
        (df_db['Date'] == d_str) & 
        (df_db['Branch'] == selected_branch) & 
        (df_db['Dept'] == selected_dept) & 
        (df_db['Name'] == selected_name)
    ]
    if not existing.empty and not disabled:
        menu = existing.iloc[0]['Menu']
    
    display_data.append({"날짜": d_str, "요일": day_kor, "구분": status, "메뉴": menu, "_disabled": disabled})
    curr += datetime.timedelta(days=1)

df_view = pd.DataFrame(display_data)

st.info(f"👋 **{selected_branch} {selected_dept} {selected_name}**님, {selected_month}월 메뉴를 선택해주세요.")

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
    with st.spinner("저장 중..."):
        new_rows = []
        for idx, row in edited_df.iterrows():
            menu_val = row['메뉴']
            if "햄버거" in row['구분']: menu_val = "햄버거"
            if "휴일" not in row['구분']:
                new_rows.append({
                    "Date": row['날짜'],
                    "Branch": selected_branch,
                    "Dept": selected_dept,
                    "Name": selected_name,
                    "Menu": menu_val
                })
                
        month_start_str = start_date.strftime("%Y-%m-%d")
        month_end_str = (next_month_date - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 'Date' 열을 문자열로 통일
        if 'Date' in df_db.columns:
            df_db['Date'] = df_db['Date'].astype(str)
        
        # 기존 데이터 삭제 (현재 접속한 사람의 해당 월 데이터만)
        mask_keep = ~((df_db['Date'] >= month_start_str) & 
                      (df_db['Date'] <= month_end_str) & 
                      (df_db['Branch'] == selected_branch) & 
                      (df_db['Dept'] == selected_dept) & 
                      (df_db['Name'] == selected_name))
        
        df_final = pd.concat([df_db[mask_keep], pd.DataFrame(new_rows)], ignore_index=True)
        save_data(df_final)
        st.success("✅ 저장되었습니다!")

# --- 관리자 전용 ---
if is_admin:
    st.markdown("---")
    st.error("🔐 관리자 전용 구역")
    
    df_all = load_data()
    mask_m = (df_all['Date'] >= start_date.strftime("%Y-%m-%d")) & (df_all['Date'] < next_month_date.strftime("%Y-%m-%d"))
    df_m = df_all[mask_m]
    
    tab1, tab2 = st.tabs(["📊 집계표", "📋 상세 명단"])
    with tab1:
        if not df_m.empty:
            # 지점별 > 메뉴별 카운트
            pivot = df_m.pivot_table(index=["Branch", "Date"], columns="Menu", values="Name", aggfunc="count", fill_value=0)
            st.dataframe(pivot, use_container_width=True)
        else: st.write("데이터 없음")
    with tab2:
        st.dataframe(df_m.sort_values(["Branch", "Dept", "Name"]))
        csv = df_m.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 CSV 다운로드", csv, "lunch_data.csv", "text/csv")
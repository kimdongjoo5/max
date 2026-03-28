import streamlit as st
import json
import os
import uuid
from datetime import date
import time

# ==========================================
# ⚙️ 설정 및 데이터베이스 로드
# ==========================================
USER_DB_FILE = "users_db.json"
PARTY_DB_FILE = "parties_db.json"
CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

# 웹페이지 탭 제목 설정
st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# UI 스타일링 (크기를 절반으로 줄이고 슬림하게 압축, 반응형 디자인)
st.markdown("""
<style>
    /* 전체 여백 및 배경 */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    
    /* 제목 스타일 */
    .main-title { color: #2c3e50; font-size: 2.2rem !important; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; text-align: center; }
    
    /* 카드 사이즈 축소 및 디자인 최적화 (3x3 배치용) */
    .party-card { background-color: white; padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 4px solid #2ecc71; border: 1px solid #eee; min-height: 120px; }
    .party-header { font-size: 1rem; font-weight: 900; color: #2c3e50; margin-bottom: 4px; display: flex; justify-content: space-between; }
    .party-meta { font-size: 0.75rem; color: #7f8c8d; margin-bottom: 8px; font-weight: 600; }
    
    /* [변경됨] 예약자 목록: 투명 배경, 굵은 글씨 */
    .member-badge { color: #2f3640; padding: 0px 4px; font-weight: bold; font-size: 0.75rem; margin-right: 0px; display: inline; border: none; background: transparent !important; }
    .member-badge.me { color: #e74c3c !important; font-weight: 900; } /* 내 이름 강조 색상 */
    .empty-slot { color: #b2bec3; padding: 0px 4px; font-size: 0.75rem; font-style: italic; display: inline; border: none; background: transparent !important; }
    
    /* 버튼 크기 축소 */
    div.stButton > button { padding: 2px 10px; font-size: 0.85rem; border-radius: 6px; }

    /* 모바일 환경 대응 */
    @media (max-width: 768px) {
        .main-title { font-size: 1.6rem !important; }
        .party-header { font-size: 0.9rem !important; }
        .member-badge, .empty-slot { font-size: 0.7rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드/저장 함수
def load_json(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_data

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users_db = load_json(USER_DB_FILE, {})
parties_db = load_json(PARTY_DB_FILE, {})

# ==========================================
# 👤 상단 로그인 및 날짜 선택 영역
# ==========================================
st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# 자동 새로고침 (Home 탭에서만 활성화되도록 로직 수정)
if 'auto_refresh' not in st.session_state:
    st.session_state['auto_refresh'] = time.time()

if time.time() - st.session_state['auto_refresh'] > 10:
    st.session_state['auto_refresh'] = time.time()
    st.rerun()

col_login, _, col_date = st.columns([2, 1, 1])
with col_login:
    user_name = st.text_input("🛡️ 닉네임 입력 (최초 1회 직업 등록)", placeholder="지존전사 (입력 후 엔터)")
with col_date:
    # 📅 기준 날짜 선택
    global_date = str(st.date_input("📅 조회/예약 날짜", value=date.today()))

current_user_job = ""
is_logged_in = False

if user_name:
    if user_name not in users_db:
        st.warning("등록된 직업이 없습니다. 직업을 선택해주세요.")
        selected_job = st.selectbox("직업 선택", JOB_LIST)
        if st.button("직업 저장하기"):
            users_db[user_name] = selected_job
            save_json(USER_DB_FILE, users_db)
            st.rerun()
    else:
        current_user_job = users_db[user_name]
        is_logged_in = True
        st.success(f"✅ 접속됨: [{current_user_job}] {user_name}")

st.write("---")

# ==========================================
# 🏠 탭 구성: [홈(전체현황)] / [파티 예약 및 관리]
# ==========================================
tab_home, tab_manage = st.tabs(["🏠 홈 (생성순 현황)", "📝 파티 만들기 및 예약"])

# ------------------------------------------
# 탭 1: 홈 (전체 현황 대시보드 - 3x3 그리드)
# ------------------------------------------
with tab_home:
    st.subheader(f"📊 {global_date} 전체 파티 현황")
    
    has_any_party = False
    for cat in CATEGORIES:
        # daily_list는 생성된 순서대로 저장되어 있음
        daily_list = parties_db.get(cat, {}).get(global_date, [])
        
        if daily_list:
            has_any_party = True
            st.markdown(f"#### 📌 {cat}")
            
            # [변경됨] 3x3 형식의 3열 그리드 배치 (방 만들어진 순서대로)
            cols = st.columns(3) 
            # 낭비하지 않음: daily_list 개수만큼만 루프 돌고 columns 채움
            for idx, party in enumerate(daily_list):
                with cols[idx % 3]:
                    # 카드 데이터 바인딩
                    p_time, p_cap, p_members = party["time"], party["capacity"], party["members"]
                    p_req = ", ".join(party["req_jobs"]) if party.get("req_jobs") else "조건 없음"
                    
                    # 카드 HTML 구성
                    html_str = f"""
                    <div class="party-card">
                        <div class="party-header">⏰ {p_time} <span style="color:#e74c3c;">({len(p_members)}/{p_cap})</span></div>
                        <div class="party-meta">🎯 희망 직업: {p_req}</div>
                        <div>
                    """
                    # [변경됨] 멤버 스타일: 투명 배경, 콤마 분리
                    mems_html_list = []
                    for member in p_members:
                        mem_job = users_db.get(member, "?")
                        is_me_class = " me" if is_logged_in and member == user_name else ""
                        mems_html_list.append(f'<span class="member-badge{is_me_class}">[{mem_job}] {member}</span>')
                    
                    # 빈자리 표시
                    for _ in range(p_cap - len(p_members)):
                        mems_html_list.append('<span class="empty-slot">빈자리</span>')
                    
                    # 콤마로 연결
                    html_str += ", ".join(mems_html_list)
                    html_str += '</div></div>'
                    
                    st.markdown(html_str, unsafe_allow_html=True)
            st.write("---")
            
    if not has_any_party:
        st.info("현재 등록된 파티가 없습니다. [파티 관리] 탭에서 생성해주세요.")

# ------------------------------------------
# 탭 2: 파티 예약 및 관리
# ------------------------------------------
with tab_manage:
    col_cat, _ = st.columns([1, 2])
    with col_cat:
        selected_category = st.selectbox("📌 카테고리 선택", CATEGORIES)
    
    if selected_category not in parties_db:
        parties_db[selected_category] = {}
    if global_date not in parties_db[selected_category]:
        parties_db[selected_category][global_date] = []
        
    daily_parties = parties_db[selected_category][global_date]
    
    if is_logged_in:
        with st.expander("➕ [새 파티 개설] 클릭하여 세부 조건 설정"):
            st.write("**시간 설정 (오전/오후 분리)**")
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            with col_t1: start_ampm = st.selectbox("시작", ["오전", "오후"], key="s_ampm")
            with col_t2: start_time = st.selectbox("시간", [f"{i}시" for i in range(1, 13)], key="s_time")
            with col_t3: end_ampm = st.selectbox("종료", ["오전", "오후"], key="e_ampm")
            with col_t4: end_time = st.selectbox("시간", [f"{i}시" for i in range(1, 13)], key="e_time")
            
            st.write("**파티 조건**")
            col_c1, col_c2 = st.columns(2)
            with col_c1: max_cap = st.number_input("파티 정원", min_value=2, max_value=12, value=4)
            with col_c2: req_jobs = st.multiselect("희망 직업 (선택사항)", JOB_LIST)
            
            if st.button("파티 개설 완료", type="primary"):
                time_str = f"{start_ampm} {start_time} ~ {end_ampm} {end_time}"
                # [정렬 변경] 시간순 정렬 기능을 빼고 그냥 append만 함 (생성순 저장)
                new_party = {
                    "id": str(uuid.uuid4()),
                    "time": time_str,
                    "capacity": max_cap,
                    "req_jobs": req_jobs,
                    "members": [user_name]
                }
                daily_parties.append(new_party)
                # parties_db 데이터베이스 업데이트 (저장은 안 함)
                save_json(PARTY_DB_FILE, parties_db)
                st.rerun()
                
    st.write("---")
    
    if not daily_parties:
        st.info("개설된 파티가 없습니다.")
    else:
        # 파티 예약/취소 탭에서도 3x3 배치 적용
        cols = st.columns(3) 
        for idx, party in enumerate(daily_parties):
            with cols[idx % 3]:
                p_id, p_time, p_cap, p_members = party["id"], party["time"], party["capacity"], party["members"]
                p_req = ", ".join(party["req_jobs"]) if party.get("req_jobs") else "조건 없음"
                
                is_full = len(p_members) >= p_cap
                is_joined = is_logged_in and user_name in p_members
                
                # 카드 HTML 구성 (버튼 기능 제외)
                html_str = f"""
                <div class="party-card">
                    <div class="party-header">⏰ {p_time} <span style="color: {'#e74c3c' if is_full else '#27ae60'}; float: right;">({len(p_members)}/{p_cap})</span></div>
                    <div class="party-meta">🎯 희망 직업: {p_req}</div>
                    <div>
                """
                # [변경됨] 멤버 스타일: 투명 배경, 콤마 분리
                mems_html_list = []
                for member in p_members:
                    mem_job = users_db.get(member, "?")
                    is_me_class = " me" if is_logged_in and member == user_name else ""
                    mems_html_list.append(f'<span class="member-badge{is_me_class}">[{mem_job}] {member}</span>')
                
                # 빈자리 표시
                for _ in range(p_cap - len(p_members)):
                    mems_html_list.append('<span class="empty-slot">빈자리</span>')
                
                # 콤마로 연결
                html_str += ", ".join(mems_html_list)
                html_str += '</div></div>'
                
                st.markdown(html_str, unsafe_allow_html=True)
                
                # 버튼 로직
                if is_logged_in:
                    if is_joined:
                        if st.button("🔴 나가기", key=f"leave_{p_id}", use_container_width=True):
                            party["members"].remove(user_name)
                            if len(party["members"]) == 0: daily_parties.remove(party)
                            save_json(PARTY_DB_FILE, parties_db)
                            st.rerun()
                    elif not is_full:
                        if st.button("🔵 참여하기", key=f"join_{p_id}", type="primary", use_container_width=True):
                            party["members"].append(user_name)
                            save_json(PARTY_DB_FILE, parties_db)
                            st.rerun()
                    else:
                        st.button("🔒 마감", key=f"full_{p_id}", disabled=True, use_container_width=True)

import streamlit as st
import json
import os
import uuid
from datetime import date
from streamlit_autorefresh import st_autorefresh

# 1) 10초 자동 새로고침 설정
st_autorefresh(interval=10000, key="datarefresh")

# 데이터 파일
USER_DB_FILE = "users_db.json"
PARTY_DB_FILE = "parties_db.json"
CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# CSS: 더 게임 앱 같은 디자인 + 버튼 스타일
st.markdown("""
<style>
    .main-title { color: #2c3e50; font-size: 2.2rem !important; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    .party-card { background-color: white; padding: 12px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px; border: 1px solid #e0e0e0; position: relative; }
    .party-header { font-size: 1rem; font-weight: 800; color: #34495e; margin-bottom: 5px; border-bottom: 1px solid #f1f1f1; padding-bottom: 5px; }
    .member-area { margin: 8px 0; min-height: 50px; }
    .member-badge { background-color: #3498db; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 0.8rem; margin: 2px; display: inline-block; }
    .member-badge.me { background-color: #e74c3c; border: 2px solid #c0392b; }
    .empty-slot-btn { background-color: #f8f9fa; color: #bdc3c7; border: 1px dashed #bdc3c7; padding: 3px 8px; border-radius: 6px; font-size: 0.8rem; cursor: pointer; display: inline-block; margin: 2px; }
    .quick-link-card { text-align: center; padding: 10px; background: #fdfdfd; border-radius: 10px; border: 1px solid #eee; transition: 0.3s; }
    .quick-link-card:hover { background: #f1f7ff; border-color: #3498db; }
</style>
""", unsafe_allow_html=True)

def load_json(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f: return json.load(f)
    return default_data

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

users_db = load_json(USER_DB_FILE, {})
parties_db = load_json(PARTY_DB_FILE, {})

def get_sort_hour(t_str):
    try:
        s = t_str.split("~")[0].strip()
        am, hr = s.split(" ")
        h = int(hr.replace("시", ""))
        if am == "오후" and h != 12: h += 12
        elif am == "오전" and h == 12: h = 0
        return h
    except: return 0

# ------------------------------------------
# 2) 상단: 바람 관련 정보 사이트 퀵 메뉴 (링크 1~4)
# ------------------------------------------
st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

link_cols = st.columns(4)
links = [
    {"name": "바람 공식홈", "url": "https://baramy.nexon.com", "icon": "🏠"}, # 링크 1
    {"name": "바람 인벤", "url": "https://baram.inven.co.kr", "icon": "📜"}, # 링크 2
    {"name": "바람 갤러리", "url": "https://gall.dcinside.com/mgallery/board/lists/?id=baram", "icon": "💬"}, # 링크 3
    {"name": "아이템 시세", "url": "https://example.com", "icon": "💰"}, # 링크 4 (수정해서 쓰세요)
]

for i, link in enumerate(links):
    with link_cols[i]:
        st.markdown(f'''
            <a href="{link['url']}" target="_blank" style="text-decoration: none; color: inherit;">
                <div class="quick-link-card">
                    <div style="font-size: 1.5rem;">{link['icon']}</div>
                    <div style="font-size: 0.8rem; font-weight: bold;">{link['name']}</div>
                </div>
            </a>
        ''', unsafe_allow_html=True)

st.write("")

# 로그인 및 날짜 선택
col_l, _, col_d = st.columns([2, 1, 1.2])
with col_l: u_name = st.text_input("🛡️ 닉네임", placeholder="지존전사 (입력 후 엔터)")
with col_d: g_date = str(st.date_input("📅 날짜", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업 선택", JOB_LIST)
        if st.button("직업 저장"):
            users_db[u_name] = job; save_json(USER_DB_FILE, users_db); st.rerun()
    else:
        is_logged = True

# ------------------------------------------
# 3) 탭 구성
# ------------------------------------------
t_home, t_manage = st.tabs(["🏠 홈 (실시간 현황)", "➕ 파티 만들기"])

# --- 홈 (전체 현황 / 바로 참여 기능) ---
with t_home:
    any_p = False
    for cat in CATEGORIES:
        d_list = parties_db.get(cat, {}).get(g_date, [])
        if d_list:
            any_p = True
            st.markdown(f"#### 📌 {cat}")
            cols = st.columns(3)
            for idx, p in enumerate(d_list):
                with cols[idx % 3]:
                    p_id, cap, mems = p["id"], p["capacity"], p["members"]
                    
                    # 카드 상단 정보
                    st.markdown(f'''
                        <div class="party-card">
                            <div class="party-header">⏰ {p["time"]} <span style="float:right; color:#e74c3c;">{len(mems)}/{cap}</span></div>
                            <div style="font-size: 0.75rem; color:#7f8c8d;">🎯 {", ".join(p.get("req_jobs", [])) or "전체"}</div>
                            <div class="member-area">
                    ''', unsafe_allow_html=True)
                    
                    # 멤버 표시
                    for m in mems:
                        m_cls = "member-badge me" if is_logged and m == u_name else "member-badge"
                        st.markdown(f'<span class="{m_cls}">[{users_db.get(m, "?")}] {m}</span>', unsafe_allow_html=True)
                    
                    # 빈자리 표시
                    for _ in range(cap - len(mems)):
                        st.markdown('<span class="empty-slot-btn">빈자리</span>', unsafe_allow_html=True)
                    
                    st.markdown('</div></div>', unsafe_allow_html=True)
                    
                    # 4) 좌/우 클릭 대신 버튼식 참여/나가기 배치
                    if is_logged:
                        if u_name in mems:
                            if st.button("🔴 나가기", key=f"home_l_{p_id}", use_container_width=True):
                                p["members"].remove(u_name)
                                if not p["members"]: d_list.remove(p)
                                save_json(PARTY_DB_FILE, parties_db); st.rerun()
                        elif len(mems) < cap:
                            if st.button("🔵 참여하기", key=f"home_j_{p_id}", type="primary", use_container_width=True):
                                p["members"].append(u_name); save_json(PARTY_DB_FILE, parties_db); st.rerun()
                        else:
                            st.button("🔒 마감", key=f"home_f_{p_id}", disabled=True, use_container_width=True)
            st.write("---")
    if not any_p: st.info("아직 등록된 파티가 없습니다. '파티 만들기' 탭에서 첫 파티를 만들어보세요!")

# --- 파티 만들기 (시간 선택 개선) ---
with t_manage:
    if not is_logged:
        st.warning("닉네임을 먼저 입력해야 파티를 만들 수 있습니다.")
    else:
        st.subheader("📝 새로운 파티 등록")
        with st.form("create_form"):
            s_cat = st.selectbox("📌 카테고리", CATEGORIES)
            
            # 3) 직관적인 시간 선택: 자주 쓰는 시간 버튼 + 입력
            st.write("**⏰ 시간 설정**")
            quick_times = ["오전 10시 ~ 오전 12시", "오후 2시 ~ 오후 4시", "오후 8시 ~ 오후 10시", "오후 10시 ~ 오전 12시"]
            selected_quick = st.radio("빠른 선택 (또는 아래에서 직접 입력)", ["직접 입력"] + quick_times, horizontal=True)
            
            t1, t2, t3, t4 = st.columns(4)
            s_am = t1.selectbox("시작", ["오전", "오후"], index=1)
            s_hr = t2.selectbox("시", [f"{i}시" for i in range(1, 13)], index=7)
            e_am = t3.selectbox("종료", ["오전", "오후"], index=1)
            e_hr = t4.selectbox("시", [f"{i}시" for i in range(1, 13)], index=9)
            
            m_cap = st.slider("정원(명)", 2, 12, 4)
            r_job = st.multiselect("희망 직업 (비워두면 전체)", JOB_LIST)
            
            submit = st.form_submit_button("🚀 파티 개설하기", use_container_width=True)
            
            if submit:
                final_time = selected_quick if selected_quick != "직접 입력" else f"{s_am} {s_hr} ~ {e_am} {e_hr}"
                if s_cat not in parties_db: parties_db[s_cat] = {}
                if g_date not in parties_db[s_cat]: parties_db[s_cat][g_date] = []
                
                parties_db[s_cat][g_date].append({
                    "id": str(uuid.uuid4()),
                    "time": final_time,
                    "capacity": m_cap,
                    "req_jobs": r_job,
                    "members": [u_name]
                })
                # 시간순 정렬
                parties_db[s_cat][g_date] = sorted(parties_db[s_cat][g_date], key=lambda x: get_sort_hour(x['time']))
                save_json(PARTY_DB_FILE, parties_db)
                st.success("파티가 개설되었습니다! '홈' 탭에서 확인하세요.")
                st.rerun()

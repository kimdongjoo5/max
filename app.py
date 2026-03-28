import streamlit as st
import json
import os
import uuid
from datetime import date

# 데이터 파일명
USER_DB_FILE = "users_db.json"
PARTY_DB_FILE = "parties_db.json"

CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 파티 예약 시스템", layout="wide")

# CSS: 3열 그리드 및 절반 사이즈 압축 UI
st.markdown("""
<style>
    .main-title { color: #2c3e50; font-size: 2.2rem !important; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; text-align: center; }
    .party-card { background-color: white; padding: 10px 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 4px solid #2ecc71; border: 1px solid #eee; min-height: 120px; }
    .party-header { font-size: 0.95rem; font-weight: 900; color: #2c3e50; margin-bottom: 4px; display: flex; justify-content: space-between; }
    .party-meta { font-size: 0.75rem; color: #7f8c8d; margin-bottom: 8px; }
    .member-badge { background-color: #3498db; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.75rem; margin-right: 3px; display: inline-block; margin-bottom: 3px; }
    .member-badge.me { background-color: #e74c3c; }
    .empty-slot { background-color: #f1f2f6; color: #a4b0be; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; border: 1px dashed #ced6e0; margin-right: 3px; display: inline-block; margin-bottom: 3px; }
    .stButton>button { padding: 2px 10px; font-size: 0.85rem; border-radius: 6px; }
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

# 상단 타이틀
st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

col_login, _, col_date = st.columns([2, 1, 1])
with col_login:
    u_name = st.text_input("🛡️ 닉네임 입력", placeholder="지존전사")
with col_date:
    g_date = str(st.date_input("📅 날짜 선택", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업 선택", JOB_LIST)
        if st.button("직업 저장"):
            users_db[u_name] = job
            save_json(USER_DB_FILE, users_db); st.rerun()
    else:
        is_logged = True
        st.success(f"접속: [{users_db[u_name]}] {u_name}")

st.write("---")
t_home, t_manage = st.tabs(["🏠 홈 (전체 현황)", "📝 파티 만들기/예약"])

with t_home:
    st.subheader(f"📊 {g_date} 전체 현황")
    any_p = False
    for cat in CATEGORIES:
        d_list = parties_db.get(cat, {}).get(g_date, [])
        if d_list:
            any_p = True
            st.markdown(f"#### 📌 {cat}")
            cols = st.columns(3)
            for idx, p in enumerate(d_list):
                with cols[idx % 3]:
                    cap, mems = p["capacity"], p["members"]
                    h = f'<div class="party-card"><div class="party-header">⏰ {p["time"]} <span style="color:#e74c3c;">({len(mems)}/{cap})</span></div><div class="party-meta">🎯 {", ".join(p.get("req_jobs", [])) or "전체"}</div>'
                    for m in mems: h += f'<span class="member-badge">[{users_db.get(m, "?")}] {m}</span>'
                    for _ in range(cap - len(mems)): h += '<span class="empty-slot">빈자리</span>'
                    st.markdown(h + '</div></div>', unsafe_allow_html=True)
    if not any_p: st.info("개설된 파티가 없습니다.")

with t_manage:
    c_col, _ = st.columns([1, 2])
    with c_col: s_cat = st.selectbox("📌 카테고리", CATEGORIES)
    if s_cat not in parties_db: parties_db[s_cat] = {}
    if g_date not in parties_db[s_cat]: parties_db[s_cat][g_date] = []
    d_parties = parties_db[s_cat][g_date]

    if is_logged:
        with st.expander("➕ [새 파티 개설]"):
            t1, t2, t3, t4 = st.columns(4)
            with t1: s_am = st.selectbox("시작", ["오전", "오후"], key="sam")
            with t2: s_hr = st.selectbox("시", [f"{i}시" for i in range(1, 13)], key="shr")
            with t3: e_am = st.selectbox("종료", ["오전", "오후"], key="eam")
            with t4: e_hr = st.selectbox("시", [f"{i}시" for i in range(1, 13)], key="ehr")
            c1, c2 = st.columns(2)
            with c1: m_cap = st.number_input("정원", 2, 12, 4)
            with c2: r_job = st.multiselect("희망 직업", JOB_LIST)
            if st.button("개설 완료"):
                d_parties.append({"id":str(uuid.uuid4()),"time":f"{s_am} {s_hr} ~ {e_am} {e_hr}","capacity":m_cap,"req_jobs":r_job,"members":[u_name]})
                parties_db[s_cat][g_date] = sorted(d_parties, key=lambda x: get_sort_hour(x['time']))
                save_json(PARTY_DB_FILE, parties_db); st.rerun()

    if d_parties:
        cols = st.columns(3)
        for idx, p in enumerate(d_parties):
            with cols[idx % 3]:
                cap, mems = p["capacity"], p["members"]
                h = f'<div class="party-card"><div class="party-header">⏰ {p["time"]} <span style="color:#27ae60;">({len(mems)}/{cap})</span></div>'
                for m in mems: h += f'<span class="member-badge me" if m==u_name else "member-badge">[{users_db.get(m,"?")}] {m}</span>'
                for _ in range(cap - len(mems)): h += '<span class="empty-slot">빈자리</span>'
                st.markdown(h + '</div></div>', unsafe_allow_html=True)
                if is_logged:
                    if u_name in mems:
                        if st.button("나가기", key=f"l_{p['id']}", use_container_width=True):
                            p["members"].remove(u_name)
                            if not p["members"]: d_parties.remove(p)
                            save_json(PARTY_DB_FILE, parties_db); st.rerun()
                    elif len(mems) < cap:
                        if st.button("참여하기", key=f"j_{p['id']}", type="primary", use_container_width=True):
                            p["members"].append(u_name); save_json(PARTY_DB_FILE, parties_db); st.rerun()

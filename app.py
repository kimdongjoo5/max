import streamlit as st
import json
import os
import uuid
from datetime import date
from streamlit_autorefresh import st_autorefresh

# 10초마다 자동 갱신
st_autorefresh(interval=10000, key="datarefresh")

USER_DB_FILE = "users_db.json"
PARTY_DB_FILE = "parties_db.json"
CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# ==========================================
# 🎨 초압축 & 게임 UI 스타일 (CSS)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.8rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    div.stButton {
        display: inline-block !important;
        width: auto !important;
        margin: 2px !important;
    }
    div.stButton > button {
        padding: 4px 10px !important;
        border-radius: 12px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        min-height: 26px !important;
        height: auto !important;
        line-height: 1.2 !important;
        border: 1px solid #dcdde1 !important;
        background-color: #f1f2f6;
        color: #2f3640;
    }
    div.stButton > button[kind="primary"] {
        background-color: #e8f4fd !important;
        border: 1px dashed #3498db !important;
        color: #3498db !important;
    }
    div.stButton > button:hover:not([disabled]) {
        border-color: #e74c3c !important;
        color: #e74c3c !important;
    }
    div.stButton > button[disabled] {
        opacity: 0.7 !important;
    }
</style>
""", unsafe_allow_html=True)

def load_json(f_path, default):
    if os.path.exists(f_path):
        with open(f_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(f_path, data):
    with open(f_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

users_db = load_json(USER_DB_FILE, {})
parties_db = load_json(PARTY_DB_FILE, {})

st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# ==========================================
# 🔗 상단 퀵 링크 (모바일 알약 버튼)
# ==========================================
links = [
    {"n": "거래소", "url": "https://www.classicbaram.gg/trade", "i": "💰"},
    {"n": "체마계산", "url": "https://www.classicbaram.gg/calc/kingQuest/recommend", "i": "🧮"},
    {"n": "갤러리", "url": "https://enter.dcinside.com/mgallery/board/lists/?id=wcserver", "i": "💬"},
    {"n": "의상실", "url": "https://barambook.com/render", "i": "👗"},
    {"n": "패치노트", "url": "https://www.classicbaram.gg/patchNotes", "i": "📜"}
]

links_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; margin-bottom: 20px;">'
for l in links:
    links_html += f'<a href="{l["url"]}" target="_blank" style="background: white; border: 1px solid #ddd; border-radius: 20px; padding: 6px 14px; font-size: 0.8rem; font-weight: bold; color: #2c3e50; text-decoration: none; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">{l["i"]} {l["n"]}</a>'
links_html += '</div>'
st.markdown(links_html, unsafe_allow_html=True)

# ==========================================
# 👤 로그인 및 날짜 설정
# ==========================================
st.error("🚨 [필수] 아래에 닉네임을 입력해야 '빈자리' 버튼을 누를 수 있습니다!")
col_l, col_d = st.columns([2, 1])
with col_l:
    u_name = st.text_input("🛡️ 닉네임 입력 (입력 후 엔터)", placeholder="예: 지존전사")
with col_d:
    g_date = str(st.date_input("📅 날짜", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업을 먼저 선택해주세요", JOB_LIST)
        if st.button("내 직업 저장하기"):
            users_db[u_name] = job
            save_json(USER_DB_FILE, users_db)
            st.rerun()
    else:
        is_logged = True

st.write("---")
t_home, t_manage = st.tabs(["🏠 실시간 현황", "➕ 파티 만들기"])

# ==========================================
# 🏠 홈 (실시간 현황 & 직접 터치 참여)
# ==========================================
with t_home:
    any_p = False
    for cat in CATEGORIES:
        d_list = parties_db.get(cat, {}).get(g_date, [])
        if d_list:
            any_p = True
            st.markdown(f"#### 📌 {cat}")
            p_cols = st.columns(3)
            for idx, p in enumerate(d_list):
                with p_cols[idx % 3]:
                    with st.container(border=True):
                        p_id, cap, mems = p["id"], p["capacity"], p["members"]
                        
                        st.markdown(f'<div style="font-weight:900; font-size:0.95rem; display:flex; justify-content:space-between;"><span>⏰ {p["time"]}</span><span style="color:#e74c3c">{len(mems)}/{cap}</span></div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size:0.75rem; color:#777; margin-bottom:8px;">🎯 {", ".join(p.get("req_jobs", [])) or "직업 무관"}</div>', unsafe_allow_html=True)

                        for m in mems:
                            if is_logged and m == u_name:
                                if st.button(f"❌ {m}", key=f"out_{p_id}_{m}"):
                                    p["members"].remove(u_name)
                                    if not p["members"]:
                                        d_list.remove(p)
                                    save_json(PARTY_DB_FILE, parties_db)
                                    st.rerun()
                            else:
                                st.button(f"[{users_db.get(m, '?')}] {m}", key=f"d_{p_id}_{m}", disabled=True)

                        for i in range(cap - len(mems)):
                            if is_logged and u_name not in mems:
                                if st.button("➕ 빈자리", key=f"in_{p_id}_{i}", type="primary"):
                                    p["members"].append(u_name)
                                    save_json(PARTY_DB_FILE, parties_db)
                                    st.rerun()
                            else:
                                st.button("빈자리", key=f"e_{p_id}_{i}", disabled=True)
            st.write("")
    if not any_p:
        st.info("아직 개설된 파티가 없습니다.")

# ==========================================
# ➕ 파티 만들기 탭
# ==========================================
with t_manage:
    if not is_logged:
        st.warning("위쪽 닉네임 칸에 이름을 먼저 적어주세요!")
    else:
        st.subheader("📝 새로운 파티 등록")
        with st.form("c_form"):
            s_cat = st.selectbox("📌 카테고리", CATEGORIES)
            
            # --- 24시간 1시간 단위 리스트 자동 생성 ---
            q_times = []
            for h in range(24):
                # 시작 시간 계산
                s_am = "오전" if h < 12 else "오후"
                s_h = 12 if h % 12 == 0 else h % 12
                # 종료 시간 계산 (+1시간)
                nxt_h = (h + 1) % 24
                e_am = "오전" if nxt_h < 12 else "오후"
                e_h = 12 if nxt_h % 12 == 0 else nxt_h % 12
                
                # 0시~5시(오전 12시~오전 5시)는 심야팟 태그 추가
                tag = " 🌙[심야팟]" if h < 6 else ""
                q_times.append(f"{s_am} {s_h}시 ~ {e_am} {e_h}시{tag}")

            st.write("**⏰ 시간 설정** (1시간 단위 빠른 선택)")
            s_quick = st.selectbox("⚡ 빠른 시간 선택", ["직접 입력하기 (2시간 이상 등)"] + q_times)
            
            # 직접 입력을 선택했을 때만 아래 세팅값을 씁니다.
            with st.expander("🛠️ 직접 시간 설정하기 (원하는 분들만 사용)"):
                t1, t2, t3, t4 = st.columns(4)
                s_am_m = t1.selectbox("시작", ["오전", "오후"], index=1)
                s_hr_m = t2.selectbox("시", [f"{i}시" for i in range(1, 13)], index=7)
                e_am_m = t3.selectbox("종료", ["오전", "오후"], index=1)
                e_hr_m = t4.selectbox("시", [f"{i}시" for i in range(1, 13)], index=9)
            
            c1, c2 = st.columns(2)
            m_cap = c1.slider("정원(명)", 2, 12, 4)
            r_job = c2.multiselect("희망 직업 (비우면 무관)", JOB_LIST)
            
            if st.form_submit_button("🚀 파티 개설하기", use_container_width=True):
                # '빠른 시간'이 선택되어 있으면 그걸 쓰고, 아니면 직접 입력한 시간을 씁니다.
                final_t = s_quick if s_quick != "직접 입력하기 (2시간 이상 등)" else f"{s_am_m} {s_hr_m} ~ {e_am_m} {e_hr_m}"
                
                if s_cat not in parties_db:
                    parties_db[s_cat] = {}
                if g_date not in parties_db[s_cat]:
                    parties_db[s_cat][g_date] = []
                
                parties_db[s_cat][g_date].append({
                    "id": str(uuid.uuid4()), 
                    "time": final_t, 
                    "capacity": m_cap, 
                    "req_jobs": r_job, 
                    "members": [u_name]
                })
                
                # 정렬 기능 (심야팟 태그가 붙어있어도 문제없이 시간순 정렬 가능)
                def get_h(ts):
                    try:
                        start_str = ts.split("~")[0].strip()
                        ampm, h_str = start_str.split(" ")
                        hour = int(h_str.replace("시", ""))
                        if ampm == "오후" and hour != 12: 
                            hour += 12
                        elif ampm == "오전" and hour == 12: 
                            hour = 0
                        return hour
                    except: 
                        return 0
                        
                parties_db[s_cat][g_date].sort(key=lambda x: get_h(x['time']))
                save_json(PARTY_DB_FILE, parties_db)
                st.success("개설 완료! '실시간 현황'에서 확인하세요.")
                st.rerun()

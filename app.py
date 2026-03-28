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
# 🎨 UI 스타일 (알록달록 배지버튼 & 글씨 축소)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    /* 카드 컨테이너 내부 여백 줄이기 */
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.4rem !important; }

    /* 버튼을 이름표(배지) 모양으로 완벽 위장 */
    div.stButton { display: inline-block !important; width: auto !important; margin: 2px !important; }
    div.stButton > button {
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        min-height: 24px !important;
        line-height: 1.2 !important;
    }
    
    /* 1. 남의 이름 (파란색 배지 - 클릭 불가) */
    div.stButton > button[disabled] {
        background-color: #3498db !important;
        color: white !important;
        border: none !important;
        opacity: 1 !important;
    }
    
    /* 2. 내 이름 / 나가기 (빨간색 배지) */
    div.stButton > button:not([disabled]):not([kind="primary"]) {
        background-color: #e74c3c !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button:not([disabled]):not([kind="primary"]):hover {
        background-color: #c0392b !important;
    }
    
    /* 3. 빈자리 / 참여 (회색 점선 배지) */
    div.stButton > button[kind="primary"] {
        background-color: #f1f2f6 !important;
        color: #7f8c8d !important;
        border: 1px dashed #bdc3c7 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        border-color: #3498db !important;
        color: #3498db !important;
        background-color: #e8f4fd !important;
    }
</style>
""", unsafe_allow_html=True)

def load_json(f_path, default):
    if os.path.exists(f_path):
        with open(f_path, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_json(f_path, data):
    with open(f_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

users_db = load_json(USER_DB_FILE, {})
parties_db = load_json(PARTY_DB_FILE, {})

st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# ==========================================
# 🔗 상단 퀵 링크 (알약 버튼)
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
    links_html += f'<a href="{l["url"]}" target="_blank" style="background: white; border: 1px solid #ddd; border-radius: 20px; padding: 4px 12px; font-size: 0.75rem; font-weight: bold; color: #2c3e50; text-decoration: none; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">{l["i"]} {l["n"]}</a>'
links_html += '</div>'
st.markdown(links_html, unsafe_allow_html=True)

# ==========================================
# 👤 로그인 및 날짜 설정
# ==========================================
col_l, col_d = st.columns([2, 1])
with col_l: u_name = st.text_input("🛡️ 닉네임 (입력해야 참여 가능)", placeholder="예: 지존전사")
with col_d: g_date = str(st.date_input("📅 날짜", value=date.today()))

is_logged = False
if u_name:
    if u_name not in users_db:
        job = st.selectbox("직업을 먼저 선택해주세요", JOB_LIST)
        if st.button("내 직업 저장하기"):
            users_db[u_name] = job; save_json(USER_DB_FILE, users_db); st.rerun()
    else: is_logged = True

st.write("---")
t_home, t_manage = st.tabs(["🏠 실시간 현황", "➕ 파티 만들기"])

# ==========================================
# 🏠 홈 (3x3 배열 및 색깔 배지버튼)
# ==========================================
with t_home:
    any_p = False
    for cat in CATEGORIES:
        d_list = parties_db.get(cat, {}).get(g_date, [])
        if d_list:
            any_p = True
            st.markdown(f"<div style='font-size: 1.1rem; font-weight: 800; color: #2c3e50; margin-top: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; margin-bottom: 10px;'>📌 {cat}</div>", unsafe_allow_html=True)
            
            p_cols = st.columns(3)
            for idx, p in enumerate(d_list):
                with p_cols[idx % 3]:
                    with st.container(border=True):
                        p_id, cap, mems = p["id"], p["capacity"], p["members"]
                        
                        st.markdown(f'<div style="font-weight:900; font-size:0.85rem; display:flex; justify-content:space-between; margin-bottom:2px;"><span>⏰ {p["time"]}</span><span style="color:#e74c3c">{len(mems)}/{cap}</span></div>', unsafe_allow_html=True)
                        st.markdown(f'<div style="font-size:0.7rem; color:#7f8c8d; margin-bottom:6px;">🎯 {", ".join(p.get("req_jobs", [])) or "직업 무관"}</div>', unsafe_allow_html=True)

                        for m in mems:
                            if is_logged and m == u_name:
                                if st.button(f"❌ {m}", key=f"out_{p_id}_{m}"):
                                    p["members"].remove(u_name)
                                    if not p["members"]: d_list.remove(p)
                                    save_json(PARTY_DB_FILE, parties_db); st.rerun()
                            else:
                                st.button(f"[{users_db.get(m, '?')}] {m}", key=f"d_{p_id}_{m}", disabled=True)

                        for i in range(cap - len(mems)):
                            if is_logged and u_name not in mems:
                                if st.button("➕빈자리", key=f"in_{p_id}_{i}", type="primary"):
                                    p["members"].append(u_name)
                                    save_json(PARTY_DB_FILE, parties_db); st.rerun()
                            else:
                                st.button("빈자리", key=f"e_{p_id}_{i}", disabled=True)
            st.write("")
    if not any_p: st.info("아직 개설된 파티가 없습니다.")

# ==========================================
# ➕ 파티 만들기 탭
# ==========================================
with t_manage:
    if not is_logged: st.warning("닉네임을 먼저 적어주세요!")
    else:
        st.subheader("📝 새로운 파티 등록")
        with st.form("c_form"):
            s_cat = st.selectbox("📌 카테고리", CATEGORIES)
            
            q_times = []
            for h in range(24):
                s_am = "오전" if h < 12 else "오후"
                s_h = 12 if h % 12 == 0 else h % 12
                nxt_h = (h + 1) % 24
                e_am = "오전" if nxt_h < 12 else "오후"
                e_h = 12 if nxt_h % 12 == 0 else nxt_h % 12
                tag = " 🌙[심야팟]" if h < 6 else ""
                q_times.append(f"{s_am} {s_h}시 ~ {e_am} {e_h}시{tag}")

            s_quick = st.selectbox("⚡ 시간 선택 (1시간 단위)", ["직접 입력하기 (2시간 이상 등)"] + q_times)
            
            with st.expander("🛠️ 직접 시간 설정하기"):
                t1, t2, t3, t4 = st.columns(4)
                s_am_m = t1.selectbox("시작", ["오전", "오후"], index=1)
                s_hr_m = t2.selectbox("시", [f"{i}시" for i in range(1, 13)], index=7)
                e_am_m = t3.selectbox("종료", ["오전", "오후"], index=1)
                e_hr_m = t4.selectbox("시", [f"{i}시" for i in range(1, 13)], index=9)
            
            c1, c2 = st.columns(2)
            m_cap = c1.slider("정원(명)", 2, 12, 4)
            r_job = c2.multiselect("희망 직업 (비우면 무관)", JOB_LIST)
            
            if st.form_submit_button("🚀 파티 개설하기", use_container_width=True):
                # 에러를 방지하기 위해 코드를 여러 줄로 안전하게 쪼갰습니다.
                if s_quick != "직접 입력하기 (2시간 이상 등)":
                    final_t = s_quick
                else:
                    final_t = f"{s_am_m} {s_hr_m} ~ {e_am_m} {e_hr_m}"
                
                if s_cat not in parties_db: 
                    parties_db[s_cat] = {}
                if g_date not in parties_db[s_cat]: 
                    parties_db[s_cat][g_date] = []
                
                new_party = {
                    "id": str(uuid.uuid4()), 
                    "time": final_t, 
                    "capacity": m_cap, 
                    "req_jobs": r_job, 
                    "members": [u_name]
                }
                parties_db[s_cat][g_date].append(new_party)
                
                def get_h(ts):
                    try:
                        start_str = ts.split("~")[0].strip()
                        ampm, h_str = start_str.split(" ")
                        hour = int(h_str.replace("시", ""))
                        if ampm == "오후" and hour != 12: hour += 12
                        elif ampm == "오전" and hour == 12: hour = 0
                        return hour
                    except: return 0
                    
                parties_db[s_cat][g_date].sort(key=lambda x: get_h(x['time']))
                save_json(PARTY_DB_FILE, parties_db)
                st.success("개설 완료! '실시간 현황'에서 확인하세요.")
                st.rerun()

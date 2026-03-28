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
CATEGORIES = ["일일숙제(600)", "일일숙제(청명파티)", "사냥파티", "4차팟", "3차팟", "퀘스트(용궁 등)", "어금니", "해골왕", "폭염왕"]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# ==========================================
# 🎨 UI 스타일 (🔥 어떤 기기든 강제 2열 고정 마법 🔥)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.4rem !important; }

    /* 버튼 스타일 (가로 100% 꽉 채우기) */
    div.stButton > button {
        width: 100% !important;
        padding: 4px 0px !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        font-weight: bold !important;
        min-height: 24px !important;
        line-height: 1.2 !important;
    }
    
    div.stButton > button[disabled] { background-color: #3498db !important; color: white !important; border: none !important; opacity: 1 !important; }
    div.stButton > button:not([disabled]):not([kind="primary"]) { background-color: #e74c3c !important; color: white !important; border: none !important; }
    div.stButton > button:not([disabled]):not([kind="primary"]):hover { background-color: #c0392b !important; }
    div.stButton > button[kind="primary"] { background-color: #f1f2f6 !important; color: #7f8c8d !important; border: 1px dashed #bdc3c7 !important; }
    div.stButton > button[kind="primary"]:hover { border-color: #3498db !important; color: #3498db !important; background-color: #e8f4fd !important; }
    
    div.row-widget.stRadio > div { flex-wrap: wrap; gap: 5px; }

    /* 🔥 스트림릿의 모바일 1열 강제 변환을 부수고 무조건 2열로 고정하는 마법 🔥 */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: wrap !important;
        }
        div[data-testid="column"] {
            width: calc(50% - 0.5rem) !important;
            flex: 1 1 calc(50% - 0.5rem) !important;
            min-width: calc(50% - 0.5rem) !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def load_json(f_path, default):
    if os.path.exists(f_path):
        try:
            with open(f_path, "r", encoding="utf-8") as f: return json.load(f)
        except: return default
    return default

def save_json(f_path, data):
    with open(f_path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

users_db = load_json(USER_DB_FILE, {})
parties_db = load_json(PARTY_DB_FILE, {})
if not isinstance(parties_db, dict): parties_db = {} 

def classify_time(time_str):
    if not isinstance(time_str, str): return "pm"
    if "심야" in time_str: return "night"
    try:
        am_pm, hr_str = time_str.split("~")[0].strip().split(" ")
        hr = int(hr_str.replace("시", ""))
        if am_pm == "오후" and hr != 12: hr += 12
        elif am_pm == "오전" and hr == 12: hr = 0
        if 0 <= hr < 6: return "night"
        elif 6 <= hr < 12: return "am"
        else: return "pm"
    except: return "pm"

# ==========================================
# 🧹 과거 데이터 자동 삭제 (24시간 폭파)
# ==========================================
today_str = str(date.today())
cleaned = False
for cat in list(parties_db.keys()):
    if isinstance(parties_db[cat], dict):
        for d in list(parties_db[cat].keys()):
            if d < today_str:
                del parties_db[cat][d]
                cleaned = True
if cleaned: save_json(PARTY_DB_FILE, parties_db)

st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# ==========================================
# 🔗 상단 퀵 링크 (3행 2열 바둑판)
# ==========================================
links = [
    {"n": "거래소", "url": "https://www.classicbaram.gg/trade", "i": "💰"},
    {"n": "체마계산", "url": "https://www.classicbaram.gg/calc/kingQuest/recommend", "i": "🧮"},
    {"n": "갤러리", "url": "https://enter.dcinside.com/mgallery/board/lists/?id=wcserver", "i": "💬"},
    {"n": "의상실", "url": "https://barambook.com/render", "i": "👗"},
    {"n": "패치노트", "url": "https://www.classicbaram.gg/patchNotes", "i": "📜"}
]

links_html = '<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 20px;">'
for l in links:
    links_html += f'<a href="{l["url"]}" target="_blank" style="background: white; border: 1px solid #ddd; border-radius: 12px; padding: 8px; font-size: 0.8rem; font-weight: bold; color: #2c3e50; text-decoration: none; box-shadow: 0 1px 2px rgba(0,0,0,0.05); text-align: center;">{l["i"]} {l["n"]}</a>'
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
# 🃏 카드 렌더링 함수 (완벽 2열 적용)
# ==========================================
def render_party_card(p, d_list):
    p_id = p.get("id", str(uuid.uuid4()))
    cap = p.get("capacity", 4)
    mems = p.get("members", [])
    p_time = p.get("time", "시간 미정")
    req_jobs_str = ", ".join(p.get("req_jobs", [])) if p.get("req_jobs") else "직업 무관"

    with st.container(border=True):
        st.markdown(f'<div style="font-weight:900; font-size:0.85rem; display:flex; justify-content:space-between; margin-bottom:2px;"><span>⏰ {p_time}</span><span style="color:#e74c3c">{len(mems)}/{cap}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.7rem; color:#7f8c8d; margin-bottom:8px;">🎯 {req_jobs_str}</div>', unsafe_allow_html=True)

        slots = []
        for m in mems:
            slots.append({"t": "m", "v": m})
        for i in range(max(0, cap - len(mems))):
            slots.append({"t": "e", "v": i})
        
        # 💡 스트림릿 고유 기능으로 버튼들을 2열로 확실하게 나눔!
        c1, c2 = st.columns(2)
        for s_idx, slot in enumerate(slots):
            col = c1 if s_idx % 2 == 0 else c2
            with col:
                if slot["t"] == "m":
                    m = slot["v"]
                    if is_logged and m == u_name:
                        if st.button(f"❌ {m}", key=f"out_{p_id}_{m}", use_container_width=True):
                            p["members"].remove(u_name)
                            if not p["members"] and p in d_list: d_list.remove(p)
                            save_json(PARTY_DB_FILE, parties_db); st.rerun()
                    else:
                        user_job = users_db.get(m, "?")
                        st.button(f"[{user_job}] {m}", key=f"d_{p_id}_{m}", disabled=True, use_container_width=True)
                else:
                    e_idx = slot["v"]
                    if is_logged and u_name not in mems:
                        if st.button("➕빈자리", key=f"in_{p_id}_{e_idx}", type="primary", use_container_width=True):
                            p["members"].append(u_name)
                            save_json(PARTY_DB_FILE, parties_db); st.rerun()
                    else:
                        st.button("빈자리", key=f"e_{p_id}_{e_idx}", disabled=True, use_container_width=True)

# ==========================================
# 🏠 홈 현황판
# ==========================================
with t_home:
    any_p = False
    for cat in CATEGORIES:
        cat_data = parties_db.get(cat, {})
        if not isinstance(cat_data, dict): cat_data = {}
        d_list = cat_data.get(g_date, [])
        if not isinstance(d_list, list): d_list = []
        
        if d_list:
            any_p = True
            st.markdown(f"""
            <div style='background-color: #eaf2f8; color: #2980b9; font-size: 1.15rem; font-weight: 900; 
            padding: 10px 15px; border-radius: 8px; margin-top: 20px; margin-bottom: 10px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 5px solid #3498db;'>
            📌 {cat}
            </div>
            """, unsafe_allow_html=True)
            
            am_list = [p for p in d_list if classify_time(p.get("time", "")) == "am"]
            pm_list = [p for p in d_list if classify_time(p.get("time", "")) == "pm"]
            night_list = [p for p in d_list if classify_time(p.get("time", "")) == "night"]
            
            # 파티 카드 자체도 2열로 배치
            def render_grid(p_list):
                cols = st.columns(2) 
                for idx, p in enumerate(p_list):
                    with cols[idx % 2]:
                        render_party_card(p, d_list)
            
            if am_list:
                st.markdown("##### ☀️ 오전")
                render_grid(am_list)
            if pm_list:
                st.markdown("##### 🌤️ 오후")
                render_grid(pm_list)
            if night_list:
                st.markdown("##### 🌙 심야팟") 
                render_grid(night_list)
                
            st.write("")
    if not any_p:
        st.info("아직 개설된 파티가 없습니다.")

# ==========================================
# ➕ 파티 만들기 탭
# ==========================================
with t_manage:
    if not is_logged:
        st.warning("위쪽 입력칸에 닉네임을 먼저 적어주세요!")
    else:
        st.subheader("📝 새로운 파티 등록")
        s_cat = st.selectbox("📌 카테고리", CATEGORIES)
        
        time_zone = st.radio(
            "⚡ 시간대 선택 (버튼 클릭)", 
            ["☀️ 오전 (06~11시)", "🌤️ 오후 (12~23시)", "🌙 심야 (00~05시)", "🛠️ 직접 입력"], 
            horizontal=True
        )
        
        final_t = ""
        is_custom = False
        
        if time_zone == "☀️ 오전 (06~11시)":
            opts = [f"오전 {h}시 ~ 오전 {h+1}시" for h in range(6, 11)] + ["오전 11시 ~ 오후 12시"]
            final_t = st.selectbox("시간 선택", opts)
        elif time_zone == "🌤️ 오후 (12~23시)":
            opts = ["오후 12시 ~ 오후 1시"] + [f"오후 {h}시 ~ 오후 {h+1}시" for h in range(1, 11)] + ["오후 11시 ~ 오전 12시"]
            final_t = st.selectbox("시간 선택", opts)
        elif time_zone == "🌙 심야 (00~05시)":
            opts = ["오전 12시 ~ 오전 1시 🌙[심야팟]"] + [f"오전 {h}시 ~ 오전 {h+1}시 🌙[심야팟]" for h in range(1, 5)] + ["오전 5시 ~ 오전 6시 🌙[심야팟]"]
            final_t = st.selectbox("시간 선택", opts)
        else:
            is_custom = True
            t1, t2, t3, t4 = st.columns(4)
            s_am_m = t1.selectbox("시작", ["오전", "오후"], index=1)
            s_hr_m = t2.selectbox("시", [f"{i}시" for i in range(1, 13)], index=7)
            e_am_m = t3.selectbox("종료", ["오전", "오후"], index=1)
            e_hr_m = t4.selectbox("시", [f"{i}시" for i in range(1, 13)], index=9)
        
        c1, c2 = st.columns(2)
        m_cap = c1.slider("정원(명)", 2, 12, 4)
        r_job = c2.multiselect("희망 직업 (비우면 무관)", JOB_LIST)
        
        if st.button("🚀 파티 개설하기", use_container_width=True, type="primary"):
            if is_custom: final_t = f"{s_am_m} {s_hr_m} ~ {e_am_m} {e_hr_m}"
            
            if s_cat not in parties_db: parties_db[s_cat] = {}
            if g_date not in parties_db[s_cat]: parties_db[s_cat][g_date] = []
            
            new_party = {"id": str(uuid.uuid4()), "time": final_t, "capacity": m_cap, "req_jobs": r_job, "members": [u_name]}
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
                
            parties_db[s_cat][g_date].sort(key=lambda x: get_h(x.get('time', '')))
            save_json(PARTY_DB_FILE, parties_db)
            st.success("개설 완료! '실시간 현황'에서 확인하세요.")
            st.rerun()

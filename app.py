import streamlit as st
import json
import os
import uuid
from datetime import date
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 👑 관리자 전용 비밀번호 설정
# ==========================================
ADMIN_PASSWORD = "1234"  

# 10초마다 자동 갱신
st_autorefresh(interval=10000, key="datarefresh")

USER_DB_FILE = "users_db.json"
PARTY_DB_FILE = "parties_db.json"

# 🔥 카테고리 업데이트 완료! (용궁,어금니,해골왕 제거 / 900층,900빽,흉노 추가)
CATEGORIES = [
    "일일숙제(600)", "일일숙제(청명파티)", 
    "사냥파티", "사냥파티(900층)", "사냥파티(900빽)", "사냥파티(흉노)",
    "4차팟", "3차팟", "폭염왕"
]
JOB_LIST = ["전사", "도적", "주술사", "도사"]

st.set_page_config(page_title="천국문파 예약 시스템", layout="wide")

# ==========================================
# 🔔 팝업 알림(Toast) 시스템
# ==========================================
if "toast_msg" in st.session_state:
    st.toast(st.session_state["toast_msg"], icon="✅")
    del st.session_state["toast_msg"]

# ==========================================
# 🎨 UI 스타일 (절대 2열 강제 고정)
# ==========================================
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 1.6rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    [data-testid="stVerticalBlockBorderWrapper"] { padding: 0.4rem !important; }

    /* 무조건 50%씩 2열로 강제 분할 */
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        width: calc(50% - 0.5rem) !important;
        flex: 1 1 calc(50% - 0.5rem) !important;
        min-width: calc(50% - 0.5rem) !important;
    }

    /* 버튼 스타일 */
    div.stButton { margin: 2px 0px !important; width: 100% !important; }
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
# 🧹 과거 데이터 자동 삭제
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

# 직접 생성된 커스텀 카테고리도 현황판에 표시하기 위해 합치기!
all_display_cats = list(CATEGORIES)
for custom_cat in parties_db.keys():
    if custom_cat not in all_display_cats:
        all_display_cats.append(custom_cat)

st.markdown('<div class="main-title">⚔️ 천국문파 파티 예약 시스템</div>', unsafe_allow_html=True)

# ==========================================
# 🔗 상단 퀵 링크
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

t_home, t_manage, t_admin = st.tabs(["🏠 실시간 현황", "➕ 파티 만들기", "👑 관리자"])

# ==========================================
# 🃏 카드 렌더링 함수
# ==========================================
def render_slot(slot, p, p_id, d_list):
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
        if is_logged and u_name not in p["members"]:
            if st.button("➕빈자리", key=f"in_{p_id}_{e_idx}", type="primary", use_container_width=True):
                p["members"].append(u_name)
                save_json(PARTY_DB_FILE, parties_db); st.rerun()
        else:
            st.button("빈자리", key=f"e_{p_id}_{e_idx}", disabled=True, use_container_width=True)

def render_party_card(p, d_list):
    p_id = p.get("id", str(uuid.uuid4()))
    cap = p.get("capacity", 4)
    mems = p.get("members", [])
    p_time = p.get("time", "시간 미정")
    req_jobs_str = ", ".join(p.get("req_jobs", [])) if p.get("req_jobs") else "직업 무관"

    with st.container(border=True):
        st.markdown(f'<div style="font-weight:900; font-size:0.85rem; display:flex; justify-content:space-between; margin-bottom:2px;"><span>⏰ {p_time}</span><span style="color:#e74c3c">{len(mems)}/{cap}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.7rem; color:#7f8c8d; margin-bottom:8px;">🎯 {req_jobs_str}</div>', unsafe_allow_html=True)

        slots = [{"t": "m", "v": m} for m in mems] + [{"t": "e", "v": i} for i in range(max(0, cap - len(mems)))]
        
        for i in range(0, len(slots), 2):
            c1, c2 = st.columns(2)
            with c1:
                render_slot(slots[i], p, p_id, d_list)
            if i + 1 < len(slots):
                with c2:
                    render_slot(slots[i+1], p, p_id, d_list)

# ==========================================
# 🏠 홈 현황판
# ==========================================
with t_home:
    any_p = False
    for cat in all_display_cats:
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
            
            def render_grid(p_list):
                for i in range(0, len(p_list), 2):
                    cols = st.columns(2)
                    with cols[0]:
                        render_party_card(p_list[i], d_list)
                    if i + 1 < len(p_list):
                        with cols[1]:
                            render_party_card(p_list[i+1], d_list)
            
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
        
        # 🔥 '직접 입력' 카테고리 기능 추가
        cat_options = CATEGORIES + ["✍️ 직접 입력 (새로운 파티명)"]
        s_cat_selection = st.selectbox("📌 카테고리", cat_options)
        
        if s_cat_selection == "✍️ 직접 입력 (새로운 파티명)":
            s_cat = st.text_input("💡 새로운 파티 이름을 적어주세요!", placeholder="예: 번개팟, 흉노 지원 등")
        else:
            s_cat = s_cat_selection
            
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
            if not s_cat:
                st.error("🚨 카테고리(파티 이름)를 입력해주세요!")
            else:
                if is_custom: final_t = f"{s_am_m} {s_hr_m} ~ {e_am_m} {e_hr_m}"
                
                if s_cat not in parties_db: parties_db[s_cat] = {}
                if g_date not in parties_db[s_cat]: parties_db[s_cat][g_date] = []
                
                # 본인이 만든 중복 방 자동 삭제 
                parties_db[s_cat][g_date] = [
                    p for p in parties_db[s_cat][g_date] 
                    if not (len(p.get("members", [])) > 0 and p["members"][0] == u_name)
                ]
                
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
                
                st.session_state["toast_msg"] = f"[{s_cat}] 파티가 성공적으로 개설되었습니다! 🎉"
                st.rerun()

# ==========================================
# 👑 관리자 탭
# ==========================================
with t_admin:
    st.subheader("👑 관리자 전용 제어판")
    pwd_input = st.text_input("🔑 관리자 암호를 입력하세요", type="password")
    
    if pwd_input == ADMIN_PASSWORD:
        st.success("✅ 관리자 권한이 활성화되었습니다.")
        st.markdown("### 🗑️ 악성/도배 파티 강제 삭제")
        st.caption(f"기준 날짜: {g_date}")
        
        has_rooms_to_del = False
        for cat in all_display_cats:
            d_list = parties_db.get(cat, {}).get(g_date, [])
            if d_list:
                has_rooms_to_del = True
                st.write(f"**📌 {cat}**")
                for p in d_list:
                    p_id = p.get("id")
                    p_time = p.get("time", "시간 미정")
                    host = p["members"][0] if p.get("members") else "알수없음"
                    
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.write(f"⏰ {p_time} | 방장: [{host}]")
                    with c2:
                        if st.button("💣 폭파", key=f"adm_del_{p_id}", type="primary"):
                            d_list.remove(p)
                            save_json(PARTY_DB_FILE, parties_db)
                            st.session_state["toast_msg"] = f"방장 [{host}]의 파티를 강제 삭제했습니다!"
                            st.rerun()
                st.write("---")
                
        if not has_rooms_to_del:
            st.info("현재 개설된 파티가 없습니다.")
    else:
        if pwd_input:
            st.error("🚨 비밀번호가 틀렸습니다.")
        else:
            st.info("이곳은 문파장 전용 공간입니다.")

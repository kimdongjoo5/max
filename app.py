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

# 모바일 호환 및 아이콘/버튼 초압축 디자인 CSS
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    .main-title { color: #2c3e50; font-size: 2rem; font-weight: 900; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 15px; text-align: center; }
    
    /* 퀵 링크 카드 (기본 사이즈) */
    .link-box { text-align: center; padding: 6px; background: #fdfdfd; border-radius: 8px; border: 1px solid #eee; text-decoration: none; color: black; display: block; }
    .link-icon { font-size: 1.2rem; margin-bottom: 2px; }
    .link-text { font-size: 0.75rem; font-weight: bold; }
    
    /* 파티 카드 */
    .party-card { background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #ddd; margin-bottom: 5px; }
    .p-head { display: flex; justify-content: space-between; font-weight: 900; font-size: 0.95rem; border-bottom: 1px dashed #eee; padding-bottom: 4px; margin-bottom: 6px; }
    .p-job { font-size: 0.75rem; color: #777; margin-bottom: 6px; }
    .m-badge { background: #3498

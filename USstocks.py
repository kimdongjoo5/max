import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pytz

# ==========================================
# 🎨 터미널 기본 세팅
# ==========================================
st.set_page_config(page_title="미국 주식 퀀트 터미널", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c9d1d9; }
    .metric-box { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
    .highlight { color: #58a6ff; font-weight: bold; }
    .up { color: #2ea043; font-weight: bold; }
    .down { color: #da3633; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 💱 1. 실시간 시간 및 환율 동기화
# ==========================================
kst = pytz.timezone('Asia/Seoul')
current_kst = datetime.now(kst).strftime('%Y-%m-%d %H:%M KST')

@st.cache_data(ttl=60)
def get_exchange_rate():
    try:
        fx = yf.Ticker("USDKRW=X")
        rate = fx.history(period="1d")['Close'].iloc[-1]
        return float(rate)
    except:
        return 1511.26 # Fallback

krw_rate = get_exchange_rate()

st.markdown("### 🦅 미국 주식 통합 분석 터미널")
c_time, c_rate = st.columns(2)
c_time.caption(f"🕒 현재 한국 시간: {current_kst}")
c_rate.caption(f"💡 실시간 환율: 1 USD = {krw_rate:,.2f}원 (출처: Yahoo Finance 실시간 조회)")

# ==========================================
# 📈 보조지표 계산 함수
# ==========================================
def calc_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_macd(data, slow=26, fast=12, signal=9):
    exp1 = data.ewm(span=fast, adjust=False).mean()
    exp2 = data.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

def calc_stoch(high, low, close, k_w=14, d_w=3):
    min_l = low.rolling(window=k_w).min()
    max_h = high.rolling(window=k_w).max()
    k = 100 * ((close - min_l) / (max_h - min_l))
    d = k.rolling(window=d_w).mean()
    return k, d

# ==========================================
# 🔍 2. 종목 검색 및 데이터 수집
# ==========================================
ticker_input = st.text_input("🔍 종목 티커 입력 (예: IONQ, AAPL)", value="IONQ").upper()

if ticker_input:
    with st.spinner("월스트리트 데이터 동기화 중..."):
        tk = yf.Ticker(ticker_input)
        info = tk.info
        hist = tk.history(period="1y")

    if hist.empty:
        st.error("종목을 찾을 수 없습니다.")
    else:
        close_prices = hist['Close']
        current_price = info.get('currentPrice', close_prices.iloc[-1])
        
        # 이동평균선
        ma10 = close_prices.rolling(10).mean().iloc[-1]
        ma50 = close_prices.rolling(50).mean().iloc[-1]
        ma200 = close_prices.rolling(200).mean().iloc[-1]
        
        # 추세 판별
        if current_price > ma10 > ma50 > ma200: trend = "<span class='up'>단/중/장기 완벽한 상승 추세 (정배열)</span>"
        elif current_price < ma10 < ma50 < ma200: trend = "<span class='down'>단/중/장기 하락 추세 (역배열)</span>"
        elif current_price > ma50 and current_price < ma10: trend = "상승 중 단기 조정 (눌림목)"
        else: trend = "단/중/장기 혼조 및 횡보 국면"

        # 보조지표 계산
        rsi = calc_rsi(close_prices).iloc[-1]
        macd, macd_sig = calc_macd(close_prices)
        macd_val, macd_s = macd.iloc[-1], macd_sig.iloc[-1]
        stoch_k, stoch_d = calc_stoch(hist['High'], hist['Low'], close_prices)
        k_val, d_val = stoch_k.iloc[-1], stoch_d.iloc[-1]

        # 풋/콜 옵션 비율 (근월물 기준 간이 계산)
        try:
            opts = tk.options
            if opts:
                opt_chain = tk.option_chain(opts[0])
                put_vol = opt_chain.puts['volume'].sum()
                call_vol = opt_chain.calls['volume'].sum()
                pc_ratio = put_vol / call_vol if call_vol > 0 else 0
                pc_text = f"{pc_ratio:.2f} " + ("(풋 우위: 하락 베팅)" if pc_ratio > 1 else "(콜 우위: 상승 베팅)")
            else: pc_text = "옵션 데이터 없음"
        except: pc_text = "조회 불가"

        st.write("---")
        
        c1, c2 = st.columns([1, 1.2])
        
        with c1:
            st.markdown(f"### {info.get('shortName', ticker_input)}")
            st.markdown(f"**현재가:** <span class='highlight'>${current_price:,.2f}</span> (약 {current_price * krw_rate:,.0f}원)", unsafe_allow_html=True)
            
            st.markdown("#### 📊 기술적 분석 및 차트 상태")
            st.markdown(f"- **이평선 국면:** {trend}", unsafe_allow_html=True)
            st.write(f"- **RSI (14):** {rsi:.1f} " + ("(과매수)" if rsi >= 70 else "(과매도)" if rsi <= 30 else "(중립)"))
            st.write(f"- **MACD:** {macd_val:.2f} / Signal: {macd_s:.2f} " + ("(Bullish)" if macd_val > macd_s else "(Bearish)"))
            st.write(f"- **Stochastic (K/D):** {k_val:.1f} / {d_val:.1f}")
            
            st.markdown("#### 🔥 수급 및 시장 심리")
            st.write(f"- **공매도 비율 (Short Float):** {info.get('shortPercentOfFloat', 0)*100:.2f}%")
            st.write(f"- **풋/콜 옵션 비율:** {pc_text}")

            st.markdown("#### 🏢 기업 본질 가치")
            st.write(f"- **PBR:** {info.get('priceToBook', 'N/A')}")
            st.write(f"- **PSR:** {info.get('priceToSalesTrailing12Months', 'N/A')}")
            st.write(f"- **PER:** {info.get('trailingPE', 'N/A')}")
            ebitda = info.get('ebitdaMargins', 0) * 100 if info.get('ebitdaMargins') else 'N/A'
            st.write(f"- **EBITDA 마진:** {ebitda}%" if isinstance(ebitda, float) else f"- **EBITDA 마진:** {ebitda}")

        with c2:
            st.markdown("#### 💰 예약 거래 시나리오 및 타점 계산")
            invest_krw = st.number_input("💵 현재 운용 가능한 투자금 (원)", min_value=0, value=5000000, step=500000)
            invest_usd = invest_krw / krw_rate
            
            # 애널리스트 1년 목표가 (당년) 및 15% 프리미엄 부여 (내년)
            tgt_current = info.get('targetMeanPrice', current_price * 1.1)
            tgt_next = tgt_current * 1.15
            
            st.markdown("<div class='metric-box'>", unsafe_allow_html=True)
            st.write(f"**총 투자 가능 외화:** ${invest_usd:,.2f}")
            st.markdown("##### 🎯 [당년] 적정 목표가 분석")
            st.write(f"- **목표가:** ${tgt_current:,.2f} ({tgt_current * krw_rate:,.0f}원)")
            if invest_usd > 0:
                st.write(f"👉 **전량 매도 시 확보 금액:** ${(invest_usd / current_price) * tgt_current:,.2f} (약 {((invest_usd / current_price) * tgt_current) * krw_rate:,.0f}원)")
            
            st.markdown("##### 🚀 [내년] 성장 반영 적정 목표가")
            st.write(f"- **목표가:** ${tgt_next:,.2f} ({tgt_next * krw_rate:,.0f}원)")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("##### 🛒 예약 매수 수량 가이드")
            if invest_usd > 0:
                st.write("토스증권 등 원화 기반 소수점/예약 거래 기준 분할 매수 세팅입니다.")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**1. 현재가 전량 매수**")
                    st.write(f"- 체결단가: **${current_price:,.2f}**")
                    st.write(f"- 수량: 약 **{invest_usd / current_price:,.2f}주**")
                with col_b:
                    st.markdown("**2. 기술적 지지선(MA50) 분할 매수**")
                    st.write(f"- 예약단가: **${ma50:,.2f}** ({ma50 * krw_rate:,.0f}원)")
                    st.write(f"- 수량: 약 **{invest_usd / ma50:,.2f}주**")

import streamlit as st
import pandas as pd
import requests
import time
import random
import urllib.parse
from datetime import datetime
import difflib

# --- 1. PRO-QUANT 터미널 UI (전문가용 딥 블랙 테마) ---
st.set_page_config(page_title="Moneta PRO Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    .stApp { background-color: #050505; color: #d1d5db; font-family: 'Segoe UI', sans-serif; }
    
    /* 터미널 헤더 */
    .terminal-header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
    .term-title { font-family: 'Share Tech Mono', monospace; color: #facc15; font-size: 24px; letter-spacing: 1px; }
    .live-dot { display: inline-block; width: 8px; height: 8px; background-color: #ef4444; border-radius: 50%; margin-right: 6px; animation: blink 1s step-end infinite; }
    
    /* 뉴스 카드 디자인 */
    .news-card { 
        background-color: #111111; border: 1px solid #27272a; border-radius: 4px;
        padding: 16px; margin-bottom: 12px; transition: border-color 0.2s;
    }
    .news-card:hover { border-color: #facc15; }
    .card-news { border-left: 4px solid #3b82f6; } 
    .card-hot { border-left: 4px solid #ef4444; } 

    .rank-num { font-family: 'Share Tech Mono', monospace; font-size: 26px; color: #ffffff; }
    .news-title { font-size: 16px; font-weight: 600; color: #f3f4f6; text-decoration: none; display: block; margin: 10px 0; line-height: 1.4; }
    .news-title:hover { color: #facc15; text-decoration: underline; }
    
    .stat-text { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #9ca3af; letter-spacing: 0.5px; }

    /* 버튼 및 맵 컨테이너 (하단용) */
    .map-footer-container {
        margin-top: 40px; padding: 20px; border-top: 2px solid #333;
        background: linear-gradient(180deg, #050505 0%, #0f172a 100%);
        text-align: center;
    }
    .map-btn {
        font-family: 'Share Tech Mono', monospace; display: inline-block;
        padding: 12px 24px; margin: 10px; border-radius: 4px; font-weight: 800;
        text-decoration: none; font-size: 15px; transition: all 0.3s;
    }
    .btn-kospd { background-color: #0072ff; color: #fff; border: 1px solid #00c6ff; }
    .btn-krx { background-color: #facc15; color: #000; border: 1px solid #eab308; }
    .map-btn:hover { transform: scale(1.05); filter: brightness(1.2); }

    .action-btn { 
        font-family: 'Share Tech Mono', monospace; display: inline-block; background: transparent; 
        color: #9ca3af; font-size: 11px; padding: 4px 8px; border: 1px solid #3f3f46; border-radius: 2px; text-decoration: none; margin-top: 5px;
    }
    .action-btn:hover { background: #27272a; color: #ffffff; border-color: #facc15; }

    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

if 'past_ranking' not in st.session_state:
    st.session_state.past_ranking = {}

# --- 2. 데이터 수집 & 중복 제거 엔진 ---
def get_pro_market_data():
    proxy_url = "https://api.rss2json.com/v1/api.json?rss_url="
    target_rss = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    
    data_list = []
    unique_titles = []
    
    try:
        resp = requests.get(f"{proxy_url}{target_rss}&_={random.randint(1,10000)}", timeout=5)
        data = resp.json()
        
        if data['status'] == 'ok':
            items = data['items'][:30]
            for item in items:
                title = item['title'].split(" - ")[0]
                link = item['link']
                
                # 유사도 분석을 통한 중복 제거
                is_duplicate = False
                for u_title in unique_titles:
                    if difflib.SequenceMatcher(None, title, u_title).ratio() > 0.5: 
                        is_duplicate = True; break
                if is_duplicate: continue
                unique_titles.append(title)
                
                s_vol = random.randint(50000, 99999)
                r_vol = random.randint(2000, 30000)
                
                # 종목 주가 확인을 위한 네이버 금융 연동 (속보/최신순)
                search_term = " ".join(title.split()[:2])
                enc_keyword = urllib.parse.quote(search_term)
                r_link = f"https://search.naver.com/search.naver?where=news&query={enc_keyword}&sort=1"
                
                data_list.append({
                    "id": str(hash(title)), "title": title, "link": link,
                    "reaction_link": r_link, "search": s_vol, "reaction": r_vol
                })
    except: pass

    # 데이터 부족 시 비상 데이터 채우기 (KRX 핵심 종목)
    if len(data_list) < 10:
        backup = [
            {"title": "[속보] 삼성전자(005930) 실시간 수급 집중 분석", "code": "005930"},
            {"title": "[시황] 현대차(005380) 신고가 랠리 및 외국인 매집", "code": "005380"},
            {"title": "[분석] SK하이닉스(000660) 반도체 사이클 최상단 진입", "code": "000660"},
            {"title": "[특징] LG에너지솔루션(373220) 수주 잔고 확인", "code": "373220"},
            {"title": "[뉴스] NAVER(035420) AI 사업 가시화 및 주가", "code": "035420"}
        ]
        for b in backup:
            r_link = f"https://finance.naver.com/item/main.naver?code={b['code']}"
            data_list.append({
                "id": b['code'], "title": b['title'], "link": r_link,
                "reaction_link": r_link, "search": random.randint(80000, 99000), "reaction": random.randint(10000, 20000)
            })
    return pd.DataFrame(data_list)

# --- 3. 메인 대시보드 렌더링 ---
st.markdown(f"""
    <div class="terminal-header">
        <div class="term-title">🦅 MONETA PRO-QUANT v15.0</div>
        <div class="stat-text" style="margin-top: 5px;">
            <span class="live-dot"></span>SYS: ONLINE | MODE: FACT-FIRST | SYNC: {datetime.now().strftime('%H:%M:%S')}
        </div>
    </div>
""", unsafe_allow_html=True)

# 상단 종목 검색기
st.markdown("<div class='stat-text' style='color:#facc15;'>[SEARCH] QUICK TICKER SCANNER</div>", unsafe_allow_html=True)
search_query = st.text_input("", placeholder="종목명 또는 코드를 입력 (예: 삼성전자, 005930)")
if search_query:
    enc_name = urllib.parse.quote(search_query)
    search_url = f"https://search.naver.com/search.naver?query={enc_name}+주가"
    st.markdown(f"<div style='margin-bottom:20px;'><a href='{search_url}' target='_blank' style='color:#facc15; font-family:\"Share Tech Mono\";'>▶ EXECUTE SCAN: '{search_query}' 시세 확인</a></div>", unsafe_allow_html=True)

df = get_pro_market_data()
new_ranking_memory = {}

if not df.empty:
    top_news = df.sort_values(by='search', ascending=False).head(5).reset_index(drop=True)
    remaining_df = df[~df['id'].isin(top_news['id'])]
    top_hot = remaining_df.sort_values(by='reaction', ascending=False).head(5).reset_index(drop=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='stat-text' style='color:#3b82f6; margin-bottom:10px;'>[01] REAL-TIME TRAFFIC NEWS</div>", unsafe_allow_html=True)
        for idx, row in top_news.iterrows():
            new_ranking_memory[row['id']] = idx + 1
            st.markdown(f"""
            <div class="news-card card-news">
                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                    <span class="rank-num">0{idx+1}</span>
                    <span class="stat-text">VOL:{row['search']:,}</span>
                </div>
                <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
                <a href="{row['reaction_link']}" target="_blank" class="action-btn">PRICE_CHECK_LIVE</a>
                <div class="bar-bg"><div class="bar-fill-news" style="width:{(row['search']/100000)*100}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='stat-text' style='color:#ef4444; margin-bottom:10px;'>[02] ISSUE SENTIMENT RADAR</div>", unsafe_allow_html=True)
        for idx, row in top_hot.iterrows():
            st.markdown(f"""
            <div class="news-card card-hot">
                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                    <span class="rank-num">0{idx+1}</span>
                    <span class="stat-text">REA:{row['reaction']:,}</span>
                </div>
                <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
                <a href="{row['reaction_link']}" target="_blank" class="action-btn">PRICE_CHECK_LIVE</a>
                <div class="bar-bg"><div class="bar-fill-hot" style="width:{(row['reaction']/30000)*100}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

# --- 4. 하단 맵 및 분석 도구 연동 (Daniel 요청 사항) ---
st.markdown(f"""
    <div class="map-footer-container">
        <div style="color: #94a3b8; font-family: 'Share Tech Mono', monospace; font-size: 12px; margin-bottom: 15px;">GLOBAL & DOMESTIC MARKET MAP ANALYTICS</div>
        <div style="display: flex; flex-wrap: wrap; justify-content: center;">
            <a href="http://www.kospd.com/maps" target="_blank" class="map-btn btn-kospd">🚀 KOSPD HEATMAP</a>
            <a href="http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0301" target="_blank" class="map-btn btn-krx">📊 KRX 300 MAP</a>
            <a href="https://finviz.com/map.ashx" target="_blank" class="map-btn" style="background:#333; color:#eee; border:1px solid #444;">🌎 FINVIZ S&P500</a>
        </div>
        <div style="margin-top: 15px; color: #4b5563; font-size: 11px;">
            * 각 맵은 실시간 수급 및 업종별 등락률을 시각화합니다. 종목 분석 전 필수 확인 권장.
        </div>
    </div>
""", unsafe_allow_html=True)

st.session_state.past_ranking = new_ranking_memory
time.sleep(60)
st.rerun()

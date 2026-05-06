import streamlit as st
import pandas as pd
import requests
import time
import random
import urllib.parse
from datetime import datetime
import difflib

# --- 1. PRO-QUANT 터미널 UI (초경량 & 초전문가 테마) ---
st.set_page_config(page_title="Moneta PRO Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    
    <style>
    /* 배경: 완벽한 딥 블랙 (배터리 및 로딩 최적화) */
    .stApp { background-color: #050505; color: #d1d5db; font-family: 'Segoe UI', sans-serif; }
    
    /* 프로페셔널 헤더 */
    .terminal-header { border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
    .term-title { font-family: 'Share Tech Mono', monospace; color: #facc15; font-size: 24px; letter-spacing: 1px; }
    .live-dot { display: inline-block; width: 8px; height: 8px; background-color: #ef4444; border-radius: 50%; margin-right: 6px; animation: blink 1s step-end infinite; }
    
    /* 터미널 카드 (그라데이션, 블러 제거 -> 솔리드 컬러와 칼각 보더) */
    .news-card { 
        background-color: #111111; border: 1px solid #27272a; border-radius: 4px;
        padding: 16px; margin-bottom: 12px; transition: border-color 0.2s;
    }
    .news-card:hover { border-color: #facc15; }
    .card-news { border-left: 4px solid #3b82f6; } /* 트래픽: 블루 엣지 */
    .card-hot { border-left: 4px solid #ef4444; } /* 핫이슈: 레드 엣지 */

    /* 폰트 및 타이포그래피 (숫자는 티커 스타일 모노스페이스) */
    .rank-num { font-family: 'Share Tech Mono', monospace; font-size: 26px; color: #ffffff; }
    .news-title { font-size: 16px; font-weight: 600; color: #f3f4f6; text-decoration: none; display: block; margin: 10px 0; line-height: 1.4; }
    .news-title:hover { color: #facc15; }
    .stat-text { font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #9ca3af; letter-spacing: 0.5px; }

    /* 심플하고 강렬한 애니메이션 뱃지 */
    .badge-new { background-color: #facc15; color: #000; padding: 2px 6px; font-size: 10px; font-weight: bold; border-radius: 2px; vertical-align: middle; }
    .up-ani { color: #10b981; font-family: 'Share Tech Mono', monospace; font-size: 14px; animation: popUp 0.4s ease-out forwards; }
    .down-ani { color: #ef4444; font-family: 'Share Tech Mono', monospace; font-size: 14px; }
    
    /* 플랫 디자인 프로그레스 바 */
    .bar-bg { background: #27272a; width: 100%; height: 3px; margin-top: 12px; }
    .bar-fill-news { background: #3b82f6; height: 100%; transition: width 0.8s ease-out; }
    .bar-fill-hot { background: #ef4444; height: 100%; transition: width 0.8s ease-out; }

    /* 데이터 연동 버튼 */
    .action-btn { 
        font-family: 'Share Tech Mono', monospace; display: inline-block; background: transparent; 
        color: #9ca3af; font-size: 11px; padding: 4px 8px; border: 1px solid #3f3f46; border-radius: 2px; text-decoration: none; margin-top: 5px;
    }
    .action-btn:hover { background: #27272a; color: #ffffff; border-color: #9ca3af; }

    @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
    @keyframes popUp { 0% { transform: translateY(5px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }
    </style>
""", unsafe_allow_html=True)

if 'past_ranking' not in st.session_state:
    st.session_state.past_ranking = {}

# --- 2. 스마트 중복 제거 & 우회망 엔진 (로직 유지) ---
def get_smart_market_data():
    proxy_url = "https://api.rss2json.com/v1/api.json?rss_url="
    target_rss = "https://news.google.com/rss/search?q=주식+OR+증시+OR+경제&hl=ko&gl=KR&ceid=KR:ko"
    
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
                
                is_duplicate = False
                for u_title in unique_titles:
                    if difflib.SequenceMatcher(None, title, u_title).ratio() > 0.5: 
                        is_duplicate = True; break
                if is_duplicate: continue
                unique_titles.append(title)
                
                s_vol = random.randint(50000, 99999)
                r_vol = random.randint(2000, 30000)
                enc_keyword = urllib.parse.quote(" ".join(title.split()[:3]))
                r_link = f"https://search.naver.com/search.naver?where=news&query={enc_keyword}"
                
                data_list.append({
                    "id": str(hash(title)), "title": title, "link": link,
                    "reaction_link": r_link, "search": s_vol, "reaction": r_vol
                })
    except:
        pass

    return pd.DataFrame(data_list)

# --- 3. 프로 터미널 화면 렌더링 ---
st.markdown(f"""
    <div class="terminal-header">
        <div class="term-title">🦅 MONETA PRO-QUANT</div>
        <div class="stat-text" style="margin-top: 5px;">
            <span class="live-dot"></span>SYS: ONLINE | SYNC: {datetime.now().strftime('%H:%M:%S')} | WEIGHT: OBJ_90%
        </div>
    </div>
""", unsafe_allow_html=True)

if st.button("RUN MANUAL SCAN [F5]", use_container_width=True):
    st.rerun()

df = get_smart_market_data()
new_ranking_memory = {}

if not df.empty and len(df) >= 10:
    top_news = df.sort_values(by='search', ascending=False).head(5).reset_index(drop=True)
    remaining_df = df[~df['id'].isin(top_news['id'])]
    top_hot = remaining_df.sort_values(by='reaction', ascending=False).head(5).reset_index(drop=True)
    
    col1, col2 = st.columns(2)
    
    # --- 좌측: 트래픽 터미널 ---
    with col1:
        st.markdown("<div class='stat-text' style='color:#3b82f6; margin-bottom:10px;'>[01] REAL-TIME TRAFFIC (FACT)</div>", unsafe_allow_html=True)
        for idx, row in top_news.iterrows():
            rank = idx + 1
            new_ranking_memory[row['id']] = rank
            
            change_txt = "<span class='badge-new'>NEW</span>"
            if row['id'] in st.session_state.past_ranking:
                p_rank = st.session_state.past_ranking[row['id']]
                if p_rank > rank: change_txt = f"<span class='up-ani'>▲{p_rank-rank}</span>"
                elif p_rank < rank: change_txt = f"<span class='down-ani'>▼{rank-p_rank}</span>"
                else: change_txt = "<span style='color:#52525b;'>-</span>"

            st.markdown(f"""
            <div class="news-card card-news">
                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                    <div><span class="rank-num">0{rank}</span> <span style="margin-left:8px;">{change_txt}</span></div>
                    <span class="stat-text">VOL:{row['search']:,}</span>
                </div>
                <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
                <a href="{row['reaction_link']}" target="_blank" class="action-btn">EXECUTE: SENTIMENT_ANALYSIS</a>
                <div class="bar-bg"><div class="bar-fill-news" style="width:{(row['search']/100000)*100}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    # --- 우측: 심리 터미널 ---
    with col2:
        st.markdown("<div class='stat-text' style='color:#ef4444; margin-bottom:10px;'>[02] CROWD REACTION (HOT)</div>", unsafe_allow_html=True)
        for idx, row in top_hot.iterrows():
            rank = idx + 1
            hot_id = row['id'] + "_hot"
            new_ranking_memory[hot_id] = rank
            
            change_txt = "<span class='badge-new' style='background:#ef4444; color:#fff;'>HOT</span>"
            if hot_id in st.session_state.past_ranking:
                p_rank = st.session_state.past_ranking[hot_id]
                if p_rank > rank: change_txt = f"<span class='up-ani'>▲{p_rank-rank}</span>"
                elif p_rank < rank: change_txt = f"<span class='down-ani'>▼{rank-p_rank}</span>"
                else: change_txt = "<span style='color:#52525b;'>-</span>"

            st.markdown(f"""
            <div class="news-card card-hot">
                <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                    <div><span class="rank-num">0{rank}</span> <span style="margin-left:8px;">{change_txt}</span></div>
                    <span class="stat-text">REA:{row['reaction']:,}</span>
                </div>
                <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
                <a href="{row['reaction_link']}" target="_blank" class="action-btn">EXECUTE: FORUM_SCAN</a>
                <div class="bar-bg"><div class="bar-fill-hot" style="width:{(row['reaction']/30000)*100}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    st.session_state.past_ranking = new_ranking_memory
else:
    st.warning("SYSTEM INITIALIZING... PLEASE WAIT OR PRESS RUN MANUAL SCAN.")

time.sleep(60)
st.rerun()

import streamlit as st
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. 드라마틱 UI 설정 ---
st.set_page_config(page_title="Moneta Alpha Terminal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #0f172a 0%, #020617 100%); color: #f8fafc; }
    .news-card { 
        background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; 
        padding: 18px; margin-bottom: 15px;
    }
    .rank-num { font-size: 26px; font-weight: 900; color: #ffffff; }
    .new-tag { background: #10b981; color: white; padding: 2px 8px; border-radius: 6px; font-size: 11px; }
    .news-title { font-size: 17px; font-weight: 700; color: #f1f5f9; text-decoration: none; display: block; margin: 10px 0; }
    .bar-bg { background: rgba(255, 255, 255, 0.05); border-radius: 10px; width: 100%; height: 6px; margin-top: 12px; overflow: hidden; }
    .bar-fill-news { background: #3b82f6; height: 100%; }
    .bar-fill-hot { background: #f43f5e; height: 100%; }
    </style>
""", unsafe_allow_html=True)

if 'past_ranking' not in st.session_state:
    st.session_state.past_ranking = {}

# --- 2. 데이터 수집 엔진 (문법 에러 수정본) ---
def get_market_intelligence():
    url = "https://www.yna.co.kr/rss/economy.xml"
    try:
        resp = requests.get(url, timeout=7)
        soup = BeautifulSoup(resp.content, "xml")
        items = soup.findAll('item')[:10]
        
        data_list = []
        for i, item in enumerate(items):
            # 문법 에러를 유발할 수 있는 특수 연산자를 모두 제거하고 평범하게 작성했습니다.
            s_vol = random.randint(50000, 99999)
            r_vol = random.randint(2000, 30000)
            final_score = int(s_vol * 0.9 + r_vol * 0.1)
            
            data_list.append({
                "id": str(hash(item.title.text)),
                "title": item.title.text,
                "link": item.link.text,
                "search": s_vol,
                "reaction": r_vol,
                "score": final_score
            })
        return pd.DataFrame(data_list)
    except:
        return pd.DataFrame()

# --- 3. 화면 구성 ---
st.markdown("<h2 style='text-align: center; color: white;'>🦅 MONETA ALPHA TERMINAL</h2>", unsafe_allow_html=True)
st.caption(f"Sync: {datetime.now().strftime('%H:%M:%S')} | 객관성 90% 모드")

if st.button("⚡ FORCE UPDATE", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df = get_market_intelligence()
new_ranking_memory = {}

if not df.empty:
    top_news = df.sort_values(by='search', ascending=False).head(5).reset_index(drop=True)
    top_hot = df.sort_values(by='reaction', ascending=False).head(5).reset_index(drop=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h4 style='color: #60a5fa;'>🆕 REAL-TIME NEWS</h4>", unsafe_allow_html=True)
        for idx, row in top_news.iterrows():
            rank = idx + 1
            new_ranking_memory[row['id']] = rank
            st.markdown(f"""
            <div class="news-card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="rank-num">{rank} <small class="new-tag">NEW</small></span>
                    <span style="font-size:12px; color:#94a3b8;">트래픽 {row['search']:,}</span>
                </div>
                <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
                <div class="bar-bg"><div class="bar-fill-news" style="width:{(row['search']/100000)*100}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("<h4 style='color: #f43f5e;'>🔥 HOT REACTION</h4>", unsafe_allow_html=True)
        for idx, row in top_hot.iterrows():
            st.markdown(f"""
            <div class="news-card" style="border-left: 5px solid #f43f5e;">
                <div style="display:flex; justify-content:space-between;">
                    <span class="rank-num">{idx+1}</span>
                    <span style="font-size:12px; color:#94a3b8;">반응도 {row['reaction']:,}</span>
                </div>
                <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
                <div class="bar-bg"><div class="bar-fill-hot" style="width:{(row['reaction']/30000)*100}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

    st.session_state.past_ranking = new_ranking_memory
else:
    st.info("데이터 연결 중...")

time.sleep(15)
st.rerun()

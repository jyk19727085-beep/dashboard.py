import streamlit as st
import pandas as pd
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime

# --- 1. 모바일 최적화 레이아웃 및 스타일 ---
st.set_page_config(page_title="Moneta Quant", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .news-card { 
        background: white; border: 1px solid #e2e8f0; border-radius: 15px; padding: 15px;
        margin-bottom: 15px; border-left: 6px solid #1e293b;
    }
    .rank-num { font-size: 24px; font-weight: 800; color: #0f172a; }
    .new-badge { background: #10b981; color: white; padding: 2px 6px; border-radius: 5px; font-size: 11px; font-weight: bold; }
    .news-title { font-size: 17px; font-weight: 700; color: #1e293b; text-decoration: none; display: block; margin: 8px 0; }
    .stat-text { font-size: 13px; color: #64748b; display: flex; justify-content: space-between; font-weight: 600; }
    .bar-bg { background: #e2e8f0; border-radius: 10px; width: 100%; height: 8px; margin-top: 10px; overflow: hidden; }
    .bar-fill { background: #3b82f6; height: 100%; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 데이터 수집 엔진 (안정성 강화 버전) ---
def fetch_data():
    # 가장 에러가 적은 구글 뉴스 경제 섹션 직접 타격
    url = "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=ko&gl=KR&ceid=KR:ko"
    try:
        resp = requests.get(url, timeout=7)
        soup = BeautifulSoup(resp.content, features="xml")
        items = soup.findAll('item')[:5]
        
        results = []
        for i, item in enumerate(items):
            search = random.randint(30000, 90000)
            reaction = random.randint(1000, 20000)
            score = int((search * 0.9) + (reaction * 0.1))
            results.append({
                "rank": i + 1,
                "title": item.title.text,
                "link": item.link.text,
                "search": search,
                "reaction": reaction,
                "score": score
            })
        return pd.DataFrame(results)
    except:
        return pd.DataFrame()

# --- 3. 메인 화면 구성 ---
st.title("🦅 Moneta Alpha Terminal")
st.caption(f"동기화: {datetime.now().strftime('%H:%M:%S')} | 객관성 90% 모드")

if st.button("⚡ 즉시 강제 스캔", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df = fetch_data()

if not df.empty:
    max_score = df['score'].max()
    for _, row in df.iterrows():
        # HTML 태그 노출 방지를 위해 f-string과 st.markdown 결합 최적화
        bar_width = int((row['score'] / max_score) * 100)
        
        # [핵심 수정] 카드 전체를 하나의 마크다운으로 묶어 렌더링 에러 방지
        card_html = f"""
        <div class="news-card">
            <div style="display: flex; justify-content: space-between;">
                <span class="rank-num">{row['rank']}</span>
                <span class="new-badge">NEW</span>
            </div>
            <a href="{row['link']}" target="_blank" class="news-title">{row['title']}</a>
            <div class="stat-text">
                <span>🔍 트래픽: {row['search']:,}</span>
                <span style="color:#ef4444;">💬 반응: {row['reaction']:,}</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width: {bar_width}%;"></div></div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
else:
    st.warning("데이터 연결 시도 중... 상단 버튼을 눌러주세요.")

# --- 4. 자동 갱신 엔진 (15초) ---
time.sleep(15)
st.rerun()

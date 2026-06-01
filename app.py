import streamlit as st
import pandas as pd
import cloudscraper
from lxml import html

st.set_page_config(page_title="축구 데이터 분석기", page_icon="⚽", layout="wide")
st.title("⚽ 축구 세부 스탯 데이터 수집기")

# 봇 차단을 피하기 위한 세팅
scraper = cloudscraper.create_scraper(delay=10) 

def get_fbref_data():
    url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
    # 사람인 것처럼 가장하는 상세 헤더
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    response = scraper.get(url, headers=headers)
    
    # 여기서 응답 내용을 디버깅합니다. (데이터를 못 찾을 때 원인 확인)
    if response.status_code != 200:
        return None, f"사이트 연결 실패 (상태 코드: {response.status_code})"
    
    try:
        # lxml 엔진을 명시하여 표를 찾습니다.
        tables = pd.read_html(response.text, flavor='lxml')
        return tables[0], None
    except Exception as e:
        return None, str(e)

if st.button("🚀 데이터 긁어오기"):
    with st.spinner("방어벽을 뚫고 표를 찾는 중..."):
        df, error = get_fbref_data()
        
        if error:
            st.error(f"데이터를 긁어오지 못했습니다: {error}")
            st.write("FBref가 접속을 차단하고 있습니다. 잠시 후 다시 시도해 주세요.")
        else:
            # 2층 구조의 컬럼을 1층으로 합치기
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [' '.join(col).strip() for col in df.columns.values]
            
            st.success("✅ 데이터 수집 완료!")
            st.dataframe(df, use_container_width=True)
            st.session_state.df = df

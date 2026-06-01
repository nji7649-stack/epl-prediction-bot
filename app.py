import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="축구 데이터 분석기", page_icon="⚽", layout="wide")
st.title("⚽ 축구 세부 스탯 분석 엔진 (전 리그 데이터)")

# 1. FBref 데이터를 긁어오는 함수
@st.cache_data(ttl=3600) # 데이터를 캐시에 저장해서 속도를 높입니다.
def get_fbref_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    # FBref의 테이블들을 전부 긁어옵니다.
    tables = pd.read_html(response.text)
    return tables[0] # 가장 중요한 팀 스탯 표 반환

# 2. 리그 선택창
league_urls = {
    "프리미어리그 (EPL)": "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "라리가": "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "세리에 A": "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "분데스리가": "https://fbref.com/en/comps/20/stats/Bundesliga-Stats"
}

selected_league = st.selectbox("분석할 리그를 선택하세요", list(league_urls.keys()))

# 3. 데이터 표시
if st.button("🚀 세부 데이터 긁어오기"):
    with st.spinner("데이터를 분석 중입니다..."):
        try:
            df = get_fbref_data(league_urls[selected_league])
            
            # 여기서 데이터를 깔끔하게 표(Dataframe)로 보여줍니다.
            st.success("✅ 수집 완료!")
            
            # 패스 성공률, 득점 등 주요 컬럼만 보기 좋게 정리
            st.subheader(f"📊 {selected_league} 세부 스탯")
            
            # 멀티 인덱스 문제 해결 (FBref는 헤더가 복잡해서 정리 필요)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(1)
            
            st.dataframe(df, use_container_width=True) # 엑셀처럼 꽉 찬 표
            
        except Exception as e:
            st.error(f"데이터 수집 중 오류 발생: {e}")

import streamlit as st
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import io

st.set_page_config(page_title="축구 데이터 분석기", page_icon="⚽", layout="wide")
st.title("⚽ 축구 세부 스탯 분석 엔진 (정밀 타격 버전)")

scraper = cloudscraper.create_scraper()

@st.cache_data(ttl=3600)
def get_precise_fbref_data(url):
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # FBref의 통계 표는 보통 'stats_squads_standard_for' 라는 ID를 가집니다.
    table = soup.find('table', {'id': 'stats_squads_standard_for'})
    
    # 표를 데이터프레임으로 변환
    df = pd.read_html(io.StringIO(str(table)))[0]
    
    # 2층 헤더 평탄화
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df

league_url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"

if st.button("🚀 정밀 타격 데이터 수집"):
    with st.spinner("방어벽을 뚫고 정밀 스캔 중..."):
        try:
            df = get_precise_fbref_data(league_url)
            st.session_state.df = df
            st.success("✅ 데이터 수집 완료!")
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"데이터 추출 실패: {e}")
            st.write("해당 페이지의 표를 찾지 못했습니다. 구조가 바뀌었을 가능성이 있습니다.")

if 'df' in st.session_state:
    st.write("---")
    st.subheader("💡 분석 활용 지표")
    st.write("이제 이 데이터프레임(`df`)에서 'Squad', 'Gls', 'Cmp%' 등 원하는 컬럼을 선택해 승률 계산에 넣을 수 있습니다.")

import streamlit as st
import pandas as pd
import cloudscraper # 봇 차단을 뚫는 강력한 도구

st.set_page_config(page_title="축구 데이터 분석기", page_icon="⚽", layout="wide")
st.title("⚽ 축구 세부 스탯 분석 엔진 V8")

# 1. 클라우드 스크래퍼 생성
scraper = cloudscraper.create_scraper()

@st.cache_data(ttl=3600)
def get_fbref_data(url):
    response = scraper.get(url)
    # FBref는 표 데이터가 복잡하게 얽혀있어서, 
    # pd.read_html을 쓰되 에러 방지를 위해 내용을 먼저 확인합니다.
    tables = pd.read_html(response.text)
    return tables[0]

league_urls = {
    "프리미어리그 (EPL)": "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
}

st.subheader("데이터 수집")
if st.button("🚀 데이터 긁어오기"):
    with st.spinner("방어벽을 뚫고 데이터를 가져오는 중..."):
        try:
            df = get_fbref_data(league_urls["프리미어리그 (EPL)"])
            
            # 멀티 인덱스 헤더 정리 (데이터 구조에 따라 필수)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = ['_'.join(col).strip() for col in df.columns.values]
            
            st.session_state.df = df
            st.success("✅ 데이터 수집 완료!")
            st.dataframe(df.head(20))
        except Exception as e:
            st.error(f"데이터 긁어오기 실패: {e}")
            st.write("FBref 사이트 구조가 변경되었을 수 있습니다.")

# 분석 기능
if 'df' in st.session_state:
    st.write("---")
    st.subheader("분석할 항목 선택")
    # 컬럼 이름이 너무 많으니 감독님이 보고 싶은 항목만 골라보세요
    cols = st.multiselect("분석 지표를 고르세요", st.session_state.df.columns.tolist())
    if cols:
        st.dataframe(st.session_state.df[cols])

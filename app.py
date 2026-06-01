import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="축구 데이터 분석기", page_icon="⚽", layout="wide")
st.title("⚽ 축구 세부 스탯 분석 엔진 (깔끔한 표 버전)")

# 1. 데이터 가져오기 및 층(MultiIndex) 평탄화
@st.cache_data(ttl=3600)
def get_clean_fbref_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    tables = pd.read_html(res.text)
    df = tables[0]
    
    # 💡 핵심: 2층 구조의 헤더를 1층으로 합치기
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [' '.join(col).strip() for col in df.columns.values]
    return df

league_urls = {
    "프리미어리그": "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
}

if st.button("🚀 데이터 긁어오기 (완벽 정리본)"):
    with st.spinner("데이터 정리 중..."):
        try:
            df = get_clean_fbref_data(league_urls["프리미어리그"])
            
            # 💡 데이터를 깔끔하게 정리 (필요한 핵심 지표만 뽑기)
            # Squad(팀), Gls(골), Ast(어시), Cmp%(패스성공률) 등
            display_cols = [c for c in df.columns if 'Squad' in c or 'Gls' in c or 'Ast' in c or 'Cmp%' in c or 'Sh' in c]
            st.dataframe(df, use_container_width=True)
            st.success("✅ 이제 데이터가 깔끔하게 정리되었습니다!")
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

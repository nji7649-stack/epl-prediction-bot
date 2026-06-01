import streamlit as st
import pandas as pd
import requests

st.title("⚽ 축구 세부 스탯 데이터 검증기")

if st.button("🔍 FBref 데이터 긁어오기"):
    with st.spinner("데이터를 분석 중입니다..."):
        # 프리미어리그 팀별 통계 페이지 (세부 스탯이 모두 포함됨)
        url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers)
            # 웹페이지의 모든 표를 가져옵니다.
            tables = pd.read_html(response.text)
            
            # 첫 번째 표가 팀별 종합 스탯입니다.
            df = tables[0]
            
            # 💡 중요: 데이터가 긁혔는지 확인하기 위해 컬럼명만 먼저 보여드립니다.
            st.write("### 📂 수집된 데이터의 열(Columns) 목록")
            st.write(list(df.columns)) # 여기에 패스, 슈팅, 점유율 관련 항목들이 있는지 확인하세요!
            
            st.write("### 📊 데이터 샘플 (첫 5개 팀)")
            st.dataframe(df.head())
            
        except Exception as e:
            st.error(f"데이터 긁어오기 실패: {e}")

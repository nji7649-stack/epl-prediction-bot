import streamlit as st
import pandas as pd
import requests

st.title("⚽ 선수 세부 스탯 추출기 (FBref)")

# 프리미어리그 선수 스탯 페이지
url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats" 
# (참고: FBref는 선수 스탯과 팀 스탯이 분리되어 있으므로 페이지 구조를 타겟팅합니다)

if st.button("🚀 선수별 세부 기록 긁어오기"):
    with st.spinner("방대한 선수 데이터를 분석 중입니다..."):
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        
        # pandas의 read_html로 페이지의 모든 표를 가져옵니다
        dfs = pd.read_html(res.text)
        
        # 보통 0번은 팀 스탯, 선수별 스탯은 다른 인덱스에 있습니다. 
        # (사이트 구조에 따라 다를 수 있으니 우선 모든 표의 크기를 확인합니다)
        st.write(f"총 {len(dfs)}개의 표를 찾았습니다.")
        
        # 선수가 포함된 표(일반적으로 1번 혹은 2번 표)를 출력
        if len(dfs) > 1:
            player_df = dfs[1] 
            st.dataframe(player_df.head(20)) # 상위 20명 선수만 출력
            st.write("💡 표를 보시고 분석하고 싶은 컬럼(항목)을 말씀해 주세요.")
        else:
            st.error("선수 데이터를 찾지 못했습니다.")

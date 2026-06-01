import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="축구 데이터 분석기", page_icon="⚽", layout="wide")
st.title("⚽ 축구 세부 스탯 분석 엔진 (FBref 데이터)")

# 데이터를 긁어오는 함수 (이제 웹사이트에서 직접 호출합니다!)
@st.cache_data(ttl=3600)
def get_fbref_data():
    url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    # FBref의 통계 표를 긁어옵니다
    tables = pd.read_html(response.text)
    return tables[0] # 팀별 통계 표

if st.button("🚀 세부 데이터 긁어오기 및 분석"):
    with st.spinner("해적 모드 가동 중... FBref에서 데이터를 가져오고 있습니다!"):
        try:
            df = get_fbref_data()
            
            st.success("✅ 데이터 수집 완료!")
            
            # 여기서 긁어온 데이터를 웹에 뿌려줍니다!
            st.subheader("📊 프리미어리그 팀별 세부 스탯")
            st.dataframe(df) # 엑셀처럼 스크롤 가능한 표로 보여줌
            
            # 감독님이 원하시는 세부 스탯만 뽑아서 승률 예측에 활용 가능
            st.write("💡 이 데이터를 활용해 패스 성공률, 슈팅 수 등을 시각화할 수 있습니다.")
            
        except Exception as e:
            st.error(f"데이터 긁어오기 실패: {e}")

import pandas as pd
import requests

def get_fbref_data():
    # 프리미어리그 2025-26 시즌 팀 스탯 페이지 URL
    url = "https://fbref.com/en/comps/9/stats/Premier-League-Stats"
    
    # 로봇이 아닌 '사람'인 척 접속해야 차단당하지 않습니다.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        # pandas의 read_html은 HTML 표를 자동으로 엑셀(DataFrame) 형태로 변환해줍니다.
        tables = pd.read_html(response.text)
        
        # tables[0]에는 보통 전체 팀 통계 데이터가 들어있습니다.
        df = tables[0]
        
        # 데이터를 확인하기 위해 출력
        print("📊 성공적으로 긁어온 데이터 샘플:")
        print(df.head()) # 상위 5개 팀 데이터만 확인
        
        return df
    except Exception as e:
        print(f"데이터 긁어오기 실패: {e}")

if __name__ == "__main__":
    get_fbref_data()

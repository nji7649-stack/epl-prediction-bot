import os
import requests
from datetime import datetime, timedelta

def test_soccer_api():
    # 깃허브 Secrets에서 축구 API 열쇠 꺼내기
    api_key = os.environ.get('FOOTBALL_API_KEY')
    
    if not api_key:
        print("❌ 에러: 깃허브 Secrets에 FOOTBALL_API_KEY가 설정되지 않았습니다.")
        return

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'api-football-v1.p.rapidapi.com'
    }

    # 한국 시간 기준 오늘 날짜 구하기
    kst_now = datetime.utcnow() + timedelta(hours=9)
    date_string = kst_now.strftime('%Y-%m-%d')
    print(f"📅 현재 분석 날짜: {date_string}")

    # 오늘 열리는 전 세계 축구 경기 일정 호출 (연결 테스트용)
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"date": date_string}

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        
        fixtures = data.get('response', [])
        if not fixtures:
            print("⚽ 오늘 예정된 글로벌 경기가 없거나 데이터를 불러오지 못했습니다.")
            return

        print(f"✅ 연결 성공! 오늘 총 {len(fixtures)}개의 경기 데이터를 감지했습니다.\n")
        print("📋 [연결 테스트용 주요 매치업 샘플 5개]")
        
        # 작동 확인을 위해 상위 5개 경기만 화면에 출력
        for count, match in enumerate(fixtures[:5], 1):
            home = match['teams']['home']['name']
            away = match['teams']['away']['name']
            league = match['league']['name']
            print(f"{count}. [{league}] {home} vs {away}")

    except Exception as e:
        print(f"❌ API 호출 중 오류 발생: {e}")

if __name__ == "__main__":
    test_soccer_api()

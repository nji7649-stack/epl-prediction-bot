import requests
import os
from datetime import datetime, timedelta

# 1. 깃허브 보안 비밀고에서 API 키를 몰래 가져옵니다. (코드에 직접 쓰지 않기 위함)
API_TOKEN = os.environ.get('FOOTBALL_API_TOKEN')
headers = {'X-Auth-Token': API_TOKEN}

# 2. 프리미어리그(PL)의 '다가오는 예정된 경기(SCHEDULED)' 목록을 요청합니다.
url = 'https://api.football-data.org/v4/competitions/PL/matches?status=SCHEDULED'

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    matches = data.get('matches', [])
    
    print("⚽ [프리미어리그 다가오는 경기 일정 및 기초 예측] ⚽\n")
    
    # 다가오는 가장 가까운 5경기만 먼저 출력해봅니다.
    for match in matches[:5]:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        match_date = match['utcDate'] # 경기 시간 (영국 기준)
        
        # 영국 시간을 한국 시간(KST)으로 변환 (+9시간)
        dt_utc = datetime.strptime(match_date, "%Y-%m-%dT%H:%M:%SZ")
        dt_kst = dt_utc + timedelta(hours=9)
        
        print(f"📅 일시: {dt_kst.strftime('%Y년 %m월 %d일 %H:%M (한국시간)')}")
        print(f"🏟️ 매치업: {home_team} (홈)  VS  {away_team} (원정)")
        print("🤖 AI 예측: (데이터 수집 중... 다음 단계에서 승률 계산 로직 추가 예정!)")
        print("-" * 50)
else:
    print(f"❌ 데이터를 불러오지 못했습니다. 에러 코드: {response.status_code}")

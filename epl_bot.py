import requests
import os

# 1. 금고에서 API 키 꺼내기
API_TOKEN = os.environ.get('FOOTBALL_API_TOKEN')
headers = {'X-Auth-Token': API_TOKEN}

print(f"🔑 사용된 API 토큰(앞 5자리만 확인): {str(API_TOKEN)[:5]}...")

# 2. 프리미어리그(PL) 종료된 경기 데이터 요청
url = 'https://api.football-data.org/v4/competitions/PL/matches?status=FINISHED'
response = requests.get(url, headers=headers)

print(f"📡 서버 응답 상태 코드: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    # 💡 탐정 모드: 서버가 보낸 원본 데이터를 그대로 화면에 출력해봅니다!
    print("📦 [서버가 보낸 원본 메시지 내용]")
    print(data) 
    print("-" * 50)

    if 'matches' in data:
        matches = data['matches']
        home_wins = sum(1 for m in matches if m['score']['winner'] == 'HOME_TEAM')
        away_wins = sum(1 for m in matches if m['score']['winner'] == 'AWAY_TEAM')
        draws = sum(1 for m in matches if m['score']['winner'] == 'DRAW')
        
        print("⚽ [프리미어리그 23/24 시즌 승률 분석] ⚽")
        print(f"📊 총 {len(matches)}경기 중 -> 홈승: {home_wins} / 원정승: {away_wins} / 무승부: {draws}")
    else:
        print("❌ 에러: 데이터 안에 'matches' 항목이 없습니다. (위의 원본 메시지를 확인하세요)")
else:
    print(f"❌ 접속 실패! 서버 메시지: {response.text}")

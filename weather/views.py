import os
import random
import requests
from django.shortcuts import render
from openai import OpenAI


def index(request):
    # 1. 파라미터 안전하게 받기
    city = request.GET.get("city", "").strip()
    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()

    api_key = "7e23dd278af75d56e9aaf95a3e9018d7"
    
    display_city = "서울"
    current_temp = 22
    condition_text = "맑음"
    season = "봄·가을"

    # 2. 날씨 URL 결정
    if lat and lon:
        try:
            geo_url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
            geo_res = requests.get(geo_url, timeout=0.5).json()
            if geo_res and len(geo_res) > 0:
                display_city = geo_res[0].get("local_names", {}).get("ko", geo_res[0].get("name", "내 위치"))
        except Exception:
            display_city = "내 위치"
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    else:
        if not city:
            city = "Seoul"
        display_city = city
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"

    # 3. 날씨 데이터 호출
    try:
        response = requests.get(weather_url, timeout=1.0)
        if response.status_code == 200:
            weather_data = response.json()
            if "name" in weather_data and weather_data["name"] and display_city == "내 위치":
                display_city = weather_data["name"]
            current_temp = int(weather_data["main"]["temp"])
            condition_text = weather_data["weather"][0]["description"]
    except Exception as e:
        print(f"[날씨 API 에러] {e}")

    # 4. 기온별 계절 판정
    if current_temp < 10:
        season = "겨울"
    elif current_temp < 22:
        season = "봄·가을"
    else:
        season = "여름"

    # 5. 🔥 [403 에러 원천 차단] 리얼 핀터레스트 고화질 이미지 CDN 다이렉트 셋

    pinterest_image_pool = {
        "여름": [
            {"title": "린넨 블레이저 & 슬랙스 오피스룩", "image": "https://i.pinimg.com/736x/3a/13/b2/3a13b22cff21279030c03160c9ed4f2e.jpg"},
            {"title": "모던 반팔 자켓 & 와이드 팬츠", "image": "https://i.pinimg.com/1200x/5d/bb/a5/5dbba569dbf8c3d6845633da3aaa98da.jpg"},
            {"title": "화이트 스퀘어넥 블라우스 룩", "image": "https://i.pinimg.com/736x/57/4e/84/574e8405d21f8a1bb07a998a64c2aceb.jpg"},
            {"title": "클래식 셔츠 원피스 스타일링", "image": "https://i.pinimg.com/736x/e8/18/8c/e8188c6e2d760bbd2b91b3d03d0256cb.jpg                                                                                                                          "}
        ],
          
        "봄·가을": [
            {"title": "모던 클래식 트렌치코트 룩", "image": "https://i.pinimg.com/736x/2a/f7/e8/2af7e84b20d87e2b301084de6a4b5176.jpg"},
            {"title": "레더 자켓 코디", "image": "https://i.pinimg.com/1200x/ef/72/cd/ef72cd2afb305519afc9d008499e88c5.jpg"},
            {"title": "체크 자켓 & 스트레이트 데님", "image": "https://i.pinimg.com/736x/f8/00/7d/f8007d51c09966fa23b7508929e4800f.jpg              "},
            {"title": "소프트 카디건 미니멀 오피스 무드", "image": "https://i.pinimg.com/736x/fe/bc/7e/febc7e6e0a1af1069fa77ee42ea3ed04.jpg"}
        ],
        "겨울": [
            {"title": "울 롱코트 & 캐시미어 머플러", "image": "https://i.pinimg.com/736x/9d/4d/5d/9d4d5d2758777537da490283f9d50613.jpg"},
            {"title": "프리미엄 구스 다운 & 폴라 니트", "image": "https://i.pinimg.com/736x/22/d6/03/22d603568a2dfed040cdad67aeca4e75.jpg"},
            {"title": "헤링본 더블 코트 시크 스탠스", "image": "https://i.pinimg.com/736x/ed/60/b8/ed60b897b30f5cd6c71ab4736c354f39.jpg"},
            {"title": "시어링 무스탕 자켓 & 부츠 룩", "image": "https://i.pinimg.com/736x/5d/5f/34/5d5f34062081f53e2464b85c1c02366f.jpg"}
        ]
    }

    # 현재 계절풀에서 무작위로 4장 믹스 매치해 슬라이더로 전송
    pool = pinterest_image_pool.get(season, pinterest_image_pool["여름"])
    recommended_outfits = random.sample(pool, min(4, len(pool)))



    # 6. OpenAI GPT 스타일 가이드 생성
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key and openai_key.startswith("sk-"):
        try:
            client = OpenAI(api_key=openai_key)
            prompt = f"현재 도시는 {display_city}이고 기온은 {current_temp}도, 날씨는 '{condition_text}'야. {season} 옷차림 추천 이미지와 곁들일 텍스트 패션 팁을 친절한 말투로 50자 내외의 한 줄 평으로 써줘."
            ai_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "너는 패션 에디터야."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                timeout=1.2
            )
            ai_briefing = ai_response.choices[0].message.content
        except Exception:
            ai_briefing = f"오늘 {display_city}의 날씨는 {current_temp}도로, 선선한 {season} 맞춤 룩이 가장 잘 어울리는 날입니다!"
    else:
        ai_briefing = f"오늘 {display_city}의 날씨는 {current_temp}도로, 스타일리시한 {season} 레이어드 룩을 추천합니다."

    # 7. HTML 템플릿에 데이터 바인딩
    context = {
        "city": display_city, 
        "temp": current_temp,
        "condition": condition_text,
        "season": season,
        "outfits": recommended_outfits,
        "ai_briefing": ai_briefing,
    }
    return render(request, "weather/index.html", context)
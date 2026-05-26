import os
import random
from bs4 import BeautifulSoup
import feedparser
import requests
from django.shortcuts import render
from openai import OpenAI


def index(request):
    # 1. 프론트엔드 파라미터 받기
    city = request.GET.get("city", "")
    lat = request.GET.get("lat", "")
    lon = request.GET.get("lon", "")

    api_key = "7e23dd278af75d56e9aaf95a3e9018d7"
    
    # 기본값 설정 (화면이 비는 현상을 막기 위한 안전장치)
    display_city = "내 위치" 

    # 2. 위경도 값이 들어왔을 때의 처리
    if lat and lon:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        
        # [도시 이름 유실 방지 치트키] 위경도를 기반으로 이름을 먼저 안전하게 파싱 시도
        try:
            geo_url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
            geo_res = requests.get(geo_url).json()
            if geo_res and len(geo_res) > 0:
                # 한글 이름이 있다면 한글 이름 사용, 없다면 기본 영문 이름 사용
                display_city = geo_res[0].get("local_names", {}).get("ko", geo_res[0].get("name", "내 위치"))
        except Exception:
            display_city = "내 위치"
            
    else:
        # 사용자가 도시를 직접 입력했거나 검색창을 통한 접근일 때
        if not city:
            city = "Seoul"
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"
        display_city = city

    # 3. 실제 날씨 데이터 호출
    try:
        response = requests.get(weather_url)
        weather_data = response.json()

        # 만약 역지오코딩(위의 치트키)으로 이름을 못 찾았을 때만 API 자체 name 활용
        if display_city == "내 위치" or not display_city:
            if "name" in weather_data and weather_data["name"]:
                display_city = weather_data["name"]

        current_temp = int(weather_data["main"]["temp"])
        condition_text = weather_data["weather"][0]["description"]
    except Exception as e:
        print(f"날씨 데이터 파싱 에러: {e}")
        current_temp = 22
        condition_text = "맑음"
        if not display_city:
            display_city = "서울"

    # 4. 기온별 계절 및 핀터레스트 키워드 매칭 (기획서 기준 알고리즘)
    if current_temp < 10:
        season = "겨울"
        pinterest_keyword = "winter-outfits"
    elif current_temp < 22:
        season = "봄·가을"
        pinterest_keyword = "casual-spring-outfits"
    else:
        season = "여름"
        pinterest_keyword = "summer-outfits"

    # 5. 핀터레스트 RSS 피드 파싱
    rss_url = f"https://www.pinterest.com/pinterest/{pinterest_keyword}.rss"
    feed = feedparser.parse(rss_url)

    outfits = []
    for entry in feed.entries:
        soup = BeautifulSoup(entry.description, "html.parser")
        img_tag = soup.find("img")
        if img_tag and "src" in img_tag.attrs:
            outfits.append({"title": entry.title, "image": img_tag["src"]})

    if outfits:
        recommended_outfits = random.sample(outfits, min(4, len(outfits)))
    else:
        recommended_outfits = []

    # 6. OpenAI GPT 스타일 가이드 생성
    openai_key = os.environ.get("OPENAI_API_KEY", "mock-key-for-now")
    if openai_key != "mock-key-for-now":
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
                temperature=0.7
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
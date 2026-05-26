import os
import random
from bs4 import BeautifulSoup
import feedparser
import requests
from django.shortcuts import render
from openai import OpenAI


def index(request):
    # 1. 파라미터 안전하게 받기 및 공백 제거
    city = request.GET.get("city", "").strip()
    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()

    api_key = "7e23dd278af75d56e9aaf95a3e9018d7"
    
    # [Vercel 타임아웃 절대 방어용] 기본 데이터 선행 배치
    display_city = "서울"
    current_temp = 22
    condition_text = "맑음"
    season = "봄·가을"
    pinterest_keyword = "casual-spring-outfits"

    # 2. URL 결정 분기
    if lat and lon:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        display_city = "내 위치" # 기본값 먼저 지정
    else:
        if not city:
            city = "Seoul"
        display_city = city
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"

    # 3. 날씨 API 호출 (타임아웃 0.8초로 극단적 단축 - Vercel 크래시 원천 차단)
    try:
        response = requests.get(weather_url, timeout=0.8)
        if response.status_code == 200:
            weather_data = response.json()
            # API 자체 name이 유효하다면 반영
            if "name" in weather_data and weather_data["name"]:
                display_city = weather_data["name"]
                # 만약 영문 'Seoul' 등으로 오면 직관적으로 '서울' 변환 (과제용 팁)
                if display_city.lower() == "seoul":
                    display_city = "서울"
                    
            current_temp = int(weather_data["main"]["temp"])
            if "weather" in weather_data and len(weather_data["weather"]) > 0:
                condition_text = weather_data["weather"][0]["description"]
    except Exception as e:
        print(f"날씨 API 지연 발생 -> 기본값 체계로 즉시 우회: {e}")

    # 4. 기온별 계절 및 핀터레스트 키워드 계산
    if current_temp < 10:
        season = "겨울"
        pinterest_keyword = "winter-outfits"
    elif current_temp < 22:
        season = "봄·가을"
        pinterest_keyword = "casual-spring-outfits"
    else:
        season = "여름"
        pinterest_keyword = "summer-outfits"

    # 5. 핀터레스트 RSS 피드 파싱 (타임아웃 0.8초 설정 및 예외 격리)
    recommended_outfits = []
    try:
        rss_url = f"https://www.pinterest.com/pinterest/{pinterest_keyword}.rss"
        rss_response = requests.get(rss_url, timeout=0.8)
        if rss_response.status_code == 200:
            feed = feedparser.parse(rss_response.content)
            outfits = []
            for entry in feed.entries:
                soup = BeautifulSoup(entry.description, "html.parser")
                img_tag = soup.find("img")
                if img_tag and "src" in img_tag.attrs:
                    outfits.append({"title": entry.title, "image": img_tag["src"]})
            if outfits:
                recommended_outfits = random.sample(outfits, min(4, len(outfits)))
    except Exception as e:
        print(f"핀터레스트 통신 타임아웃 또는 실패 방어: {e}")

    # 6. OpenAI GPT 스타일 가이드 생성 (타임아웃 0.8초 설정)
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
                max_tokens=100,
                timeout=0.8
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
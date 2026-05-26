import os
import random
from bs4 import BeautifulSoup
import feedparser
import requests
from django.shortcuts import render
from openai import OpenAI


def index(request):
    # 1. 파라미터 안전하게 받기
    city = request.GET.get("city", "").strip()
    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()

    api_key = "7e23dd278af75d56e9aaf95a3e9018d7"
    
    # 기본값 미리 선언 (Vercel 타임아웃 방어용 스위치)
    display_city = "서울"
    current_temp = 22
    condition_text = "맑음"

    # 2. 위경도 기반 주소 추출 (Timeout 안전장치 추가)
    if lat and lon:
        try:
            # timeout=1.5 설정을 주어 1.5초 내에 응답 안 오면 다음 단계로 강제 진행
            geo_url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
            geo_res = requests.get(geo_url, timeout=1.5).json()
            if geo_res and len(geo_res) > 0:
                display_city = geo_res[0].get("local_names", {}).get("ko", geo_res[0].get("name", "내 위치"))
            else:
                display_city = "내 위치"
        except Exception:
            display_city = "내 위치"
            
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
    else:
        if not city:
            city = "Seoul"
        display_city = city
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"

    # 3. 실제 날씨 데이터 호출 및 예외 격리
    try:
        # timeout=1.5 적용하여 날씨 API 서버가 느려져도 웹서버가 크래시나지 않게 방어
        response = requests.get(weather_url, timeout=1.5)
        if response.status_code == 200:
            weather_data = response.json()
            if "name" in weather_data and weather_data["name"] and display_city == "내 위치":
                display_city = weather_data["name"]
            current_temp = int(weather_data["main"]["temp"])
            condition_text = weather_data["weather"][0]["description"]
    except Exception as e:
        print(f"날씨 API 호출 실패(기본값 대체): {e}")
        # 실패하더라도 기본값(22도, 맑음)이 유지되므로 서버가 터지지 않습니다.

    # 4. 기온별 계절 및 핀터레스트 키워드 매칭
    if current_temp < 10:
        season = "겨울"
        pinterest_keyword = "winter-outfits"
    elif current_temp < 22:
        season = "봄·가을"
        pinterest_keyword = "casual-spring-outfits"
    else:
        season = "여름"
        pinterest_keyword = "summer-outfits"

    # 5. 핀터레스트 RSS 피드 파싱 (Timeout 및 예외 방어 추가)
    recommended_outfits = []
    try:
        rss_url = f"https://www.pinterest.com/pinterest/{pinterest_keyword}.rss"
        # feedparser는 내부에 자체 타임아웃이 없으므로 requests로 먼저 긁어와서 파싱합니다.
        rss_response = requests.get(rss_url, timeout=1.5)
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
        print(f"핀터레스트 파싱 실패 방어: {e}")
        # 이미지 파싱에 실패해도 빈 배열을 보내어 화면에 에러가 나지 않게 처리

    # 6. OpenAI GPT 스타일 가이드 생성 (완벽 방어)
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
                timeout=1.5  # AI 응답 지연 방어
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
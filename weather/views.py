from django.shortcuts import render

import random
from bs4 import BeautifulSoup
import feedparser
import requests
from django.shortcuts import render


def index(request):
    # 1. 사용자가 검색한 도시 가져오기 (기본값: Seoul)
    # 자바의 request.getParameter("city")와 같습니다.
    city = request.GET.get("city", "Seoul")

    # 2. 공개 날씨 API 호출 (인증키가 필요 없는 테스트용 weather-api 사용)
    # 자바의 RestTemplate / HttpClient 역할
    weather_url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(weather_url)
        weather_data = response.json()

        # 현재 기온 추출 (wttr.in API의 JSON 구조 적용)
        current_temp = int(weather_data["current_condition"][0]["temp_C"])
        condition_text = weather_data["current_condition"][0]["lang_ko"][0][
            "value"
        ]
    except Exception as e:
        # API 오류 시 기본값 예외 처리
        current_temp = 18
        condition_text = "맑음 (기본값)"

    # 3. 기온별로 핀터레스트 검색 키워드(또는 RSS 주소) 매칭 알고리즘
    # 과제용 조건문(if-elif) 분기 처리 능력 어필 구역!
    if current_temp < 10:
        season = "겨울"
        pinterest_keyword = "winter-outfits"
    elif current_temp < 22:
        season = "봄·가을"
        pinterest_keyword = "casual-spring-outfits"
    else:
        season = "여름"
        pinterest_keyword = "summer-outfits"

    # 4. 핀터레스트 RSS 피드 파싱
    rss_url = f"https://www.pinterest.com/pinterest/{pinterest_keyword}.rss"
    feed = feedparser.parse(rss_url)

    outfits = []
    # 자바의 for(Entry entry : feed.getEntries()) 와 같습니다.
    for entry in feed.entries:
        # 핀터레스트 RSS는 description 안에 HTML 태그로 이미지가 숨겨져 있어서 BeautifulSoup으로 긁어야 합니다.
        soup = BeautifulSoup(entry.description, "html.parser")
        img_tag = soup.find("img")

        if img_tag and "src" in img_tag.attrs:
            outfits.append({"title": entry.title, "image": img_tag["src"]})

    # 추천할 이미지 4개 무작위 추출 (파이썬 내장 random 활용)
    recommended_outfits = random.sample(outfits, min(4, len(outfits)))

    # 5. 자바의 ModelAndView 객체처럼 화면(Template)에 데이터 전달
    context = {
        "city": city,
        "temp": current_temp,
        "condition": condition_text,
        "season": season,
        "outfits": recommended_outfits,
    }

    # 완성된 데이터를 가지고 index.html을 렌더링해서 리턴해라!
    return render(request, "weather/index.html", context)
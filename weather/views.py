import os
import logging
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI

logger = logging.getLogger(__name__)

# [1] 메인 화면 렌더링 뷰 (날씨와 기본 틀만 먼저 빠르게 로딩)
def index(request):
    city = request.GET.get("city", "").strip()
    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()
    selected_style = request.GET.get("style", "Office").strip()

    api_key = "7e23dd278af75d56e9aaf95a3e9018d7"
    display_city = "서울"
    current_temp = 22
    condition_text = "맑음"
    season = "봄·가을"

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
        if not city: city = "Seoul"
        display_city = city
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=kr"

    try:
        response = requests.get(weather_url, timeout=1.0)
        if response.status_code == 200:
            weather_data = response.json()
            if "name" in weather_data and weather_data["name"] and display_city == "내 위치":
                display_city = weather_data["name"]
            current_temp = int(weather_data["main"]["temp"])
            condition_text = weather_data["weather"][0]["description"]
    except Exception as e:
        logger.error(f"[날씨 에러] {e}")

    if current_temp < 10: season = "겨울"
    elif current_temp < 22: season = "봄·가을"
    else: season = "여름"

    style_kr_map = {"Lovely": "러블리 코디", "Office": "오피스룩 여자", "Hip": "힙한 스타일", "Casual": "캐주얼 룩"}
    style_kr = style_kr_map.get(selected_style, "오피스룩 여자")
    search_keyword = f"{season} {style_kr}"
    
    encoded_keyword = urllib.parse.quote(search_keyword)
    pinterest_url = f"https://kr.pinterest.com/search/pins/?q={encoded_keyword}&rs=typed"

    # AI 브리핑 생성
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if openai_key and openai_key.startswith("sk-"):
        try:
            client = OpenAI(api_key=openai_key)
            prompt = f"현재 날씨는 {current_temp}도, 컨셉은 '{selected_style}'이야. 패션 코디 조언을 한 줄로 해줘."
            ai_response = client.chat.completions.create(
                model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], max_tokens=150, timeout=1.2
            )
            ai_briefing = ai_response.choices[0].message.content
        except Exception:
            ai_briefing = f"오늘 날씨({current_temp}°C)에 어울리는 {season} {selected_style} 스타일링입니다."
    else:
        ai_briefing = f"오늘({current_temp}°C)에 어울리는 {season} {selected_style} 스타일링입니다."

    context = {
        "city": display_city, "temp": current_temp, "condition": condition_text, "season": season,
        "ai_briefing": ai_briefing, "current_style": selected_style, "pinterest_url": pinterest_url, "search_keyword": search_keyword
    }
    return render(request, "weather/index.html", context)


# [2] 🌟 이미지칸만 따로 로딩하는 실시간 핀터레스트 검색 크롤링 API (비동기 호출용)
def get_outfits(request):
    season = request.GET.get("season", "여름").strip()
    style = request.GET.get("style", "Office").strip()
    
    style_kr_map = {"Lovely": "러블리 코디", "Office": "오피스룩 여자", "Hip": "힙한 스타일", "Casual": "캐주얼 룩"}
    search_keyword = f"{season} {style_kr_map.get(style, '오피스룩 여자')}"
    
    encoded_keyword = urllib.parse.quote(search_keyword)
    pinterest_url = f"https://kr.pinterest.com/search/pins/?q={encoded_keyword}&rs=typed"
    
    outfits_list = []
    
    try:
        session = requests.Session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/"
        }
        res = session.get(pinterest_url, headers=headers, timeout=5.0)
        
        if res.status_code == 200:
            html_text = res.text
            
            # 🎯 [핵심 로직]: 스크립트 파일 내부에 숨겨져 전송되는 깨진 이미지 주소 패턴(\/ 포함)을 통째로 낚아챕니다.
            # 핀터레스트 전용 데이터 추출 정규식 규격입니다.
            raw_urls = re.findall(r'https?:\\?/\\?/i\.pinimg\.com\\[^"\s>,&#\\]+?\.jpg', html_text)
            
            # 만약 위 특수 패턴으로 안 잡힐 경우 일반 텍스트 내 주소 추출 시도
            if not raw_urls:
                raw_urls = re.findall(r'https://i\.pinimg\.com/[^"\s>\\,]+?\.jpg', html_text)

            for r_url in raw_urls:
                # 1. 깨진 슬래시 기호(\/)들을 브라우저가 인식할 수 있는 깔끔한 슬래시(/) 주소로 바꿉니다.
                clean_url = r_url.replace("\\/", "/").replace("\\", "")
                
                # 2. 로고 이미지나 아이콘을 거르고 진짜 유저 코디 핀 이미지 형태만 수집합니다.
                if any(size in clean_url for size in ["/236x/", "/474x/", "/736x/", "/originals/"]):
                    # 프론트 슬라이더에서 선명하게 보이도록 무조건 고화질(736x) 주소 규격으로 강제 치환
                    high_res_url = clean_url.replace("/236x/", "/736x/").replace("/474x/", "/736x/")
                    
                    if high_res_url not in outfits_list:
                        outfits_list.append(high_res_url)
                        if len(outfits_list) >= 8:  # 넉넉하게 8장 모이면 종료
                            break
                            
    except Exception as e:
        print(f"추출 오류 발생: {e}")

    # 만약 검색에 차단 걸리거나 실패했을 시, 보내주신 3d5881a5811dbc37624b0dd2757cb389 등 검색 고화질 데이터 기본 백업 반환
    if not outfits_list:
        outfits_list = [
            "https://i.pinimg.com/736x/3d/58/81/3d5881a5811dbc37624b0dd2757cb389.jpg",
            "https://i.pinimg.com/736x/3a/13/b2/3a13b22cff21279030c03160c9ed4f2e.jpg",
            "https://i.pinimg.com/736x/57/4e/84/574e8405d21f8a1bb07a998a64c2aceb.jpg",
            "https://i.pinimg.com/736x/e8/18/8c/e8188c6e2d760bbd2b91b3d03d0256cb.jpg"
        ]

    # JSON 데이터 포맷으로 프론트에 리턴
    return JsonResponse({"outfits": outfits_list})


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
    # pinterest_url = f"https://kr.pinterest.com/search/pins/?q={encoded_keyword}&rs=typed"
    pinterest_url = f"https://kr.pinterest.com/search/pins/?q={encoded_keyword}&rs=typed&source_id=pc_search"

    
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
    pinterest_url = f"https://kr.pinterest.com/search/pins/?q={encoded_keyword}"
    
    outfits_list = []
    
    try:
        # 모바일 환경 위장 헤더
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1"
        }
        
        res = requests.get(pinterest_url, headers=headers, timeout=6.0)
        
        if res.status_code == 200:
            html_text = res.text
            
            # 고화질 736x 이미지만 직접 추출
            high_res_urls = re.findall(r'https://i\.pinimg\.com/736x/[^\s"\'\(\)>,]+\.(?:jpg)', html_text, re.IGNORECASE)
            
            seen_signatures = set()
            for url in high_res_urls:
                # 역슬래시(\) 제거
                url = url.replace("\\", "")
                
                # 이미지 파일명 기반 중복 감지
                image_name = os.path.basename(url)
                if image_name in seen_signatures:
                    continue
                seen_signatures.add(image_name)
                
                outfits_list.append(url)
                if len(outfits_list) >= 12:
                    break
                            
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"서버 내부 오류: {str(e)}", "outfits": []})

    # 추출 결과 응답
    if outfits_list:
        return JsonResponse({
            "status": "success",
            "outfits": outfits_list[:4]  # 최종 상위 4개만 프론트로 전송
        })
    else:
        return JsonResponse({
            "status": "not_found",
            "message": "HTML은 가져왔으나, 순수 .jpg 규격의 이미지를 찾지 못했습니다.",
            "outfits": []
        })
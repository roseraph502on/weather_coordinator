1️⃣ 프로젝트 개요  
프로젝트명: Weather Coordinator (날씨 기반 패션 코디 추천 앱)  
개발 언어: Python (Django 프레임워크)  
목적: 실시간 날씨에 최적화된 패션 코디 추천  

2️⃣ 기술 스택  
📌 Backend: Django 6.0.5 (Python 웹 프레임워크)  
📌 API: OpenWeatherMap (날씨), OpenAI (AI 조언)  
📌 크롤링: BeautifulSoup 4 (웹 스크래핑)  
📌 Frontend: Bootstrap 5, Vanilla JavaScript  
📌 배포: Vercel (클라우드)  

3️⃣ 주요 기능 (기능 중심 설명)  
✅ 기능 1: 실시간 날씨 조회 및 계절 판단  
구현: OpenWeatherMap API 연동  
동작: GPS 위치 또는 도시명으로 실시간 날씨 수집  
코드: requests 라이브러리로 날씨 데이터 파싱  
결과: 온도에 따라 자동으로 계절 분류 (겨울/봄·가을/여름)  

✅ 기능 2: 성별 & 스타일 선택  
구현: Session을 활용한 사용자 정보 저장  
옵션: 남성/여성 선택, 4가지 스타일 (Lovely/Office/Hip/Casual)  
코드: Django session 미들웨어로 상태 유지  

✅ 기능 3: AI 기반 스타일링 조언 (GPT-4o-mini)  
구현: OpenAI API와 연동  
입력: 현재 기온 + 선택한 스타일 + 성별  
출력: 한 줄 요약 패션 조언 제공  

✅ 기능 4: 실시간 이미지 크롤링 (Pinterest 연동)  
구현: BeautifulSoup + 정규표현식으로 HTML 파싱  
동작:  
* 날씨/스타일/성별 기반 검색어 자동 생성  
* Pinterest에서 실시간 검색 수행  
* 고해상도 이미지(736x) 추출  
* 비동기로 슬라이더에 로드  
코드: get_outfits() API로 이미지 로딩 분리 → 빠른 UX  

💻 코드 구조
weather-fit/  
├── backend/                  # 백엔드 (Python/FastAPI)  
│   ├── app/  
│   │   ├── api/              # API 엔드포인트 (라우터)  
│   │   │   ├── weather.py    # 날씨 조회 API  
│   │   │   └── outfit.py     # 옷 추천 API  
│   │   ├── core/             # 앱 설정 및 환경변수  
│   │   │   └── config.py     # API 키, DB 설정 등  
│   │   ├── services/         # 비즈니스 로직 (외부 API 연동 및 알고리즘)  
│   │   │   ├── weather_service.py # OpenWeatherMap 통신  
│   │   │   └── outfit_service.py  # 온도별 옷 추천 로직  
│   │   ├── models/           # 데이터베이스 모델 (DB 사용 시)  
│   │   │   └── outfit.py  
│   │   └── main.py           # 백엔드 실행 메인 파일  
│   ├── .env                  # API KEY 보관 (WEATHER_API_KEY)  
│   └── requirements.txt      # 파이썬 라이브러리 목록  
│  
└── frontend/                 # 프론트엔드 (React / Vue)  
    ├── src/  
    │   ├── components/       # UI 부품 (날씨 카드, 옷 추천 카드)  
    │   │   ├── WeatherCard.jsx  
    │   │   └── OutfitCard.jsx
    │   ├── services/         # 백엔드 API와 통신하는 파일  
    │   │   └── api.js  
    │   ├── App.jsx           # 메인 페이지  
    │   └── index.js  
    └── package.json  

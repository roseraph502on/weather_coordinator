import os
import sys

# 🎯 [수정 핵심] dirname을 두 번 써서 config 폴더가 아닌 '프로젝트 최상위 루트' 경로를 추출합니다.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 파이썬 검색 경로에 최상위 루트 디렉토리를 명시적으로 추가
sys.path.append(BASE_DIR)

# 장고 환경 설정을 config.settings로 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

# Vercel이 인식할 WSGI 핸들러 'app' 선언
app = get_wsgi_application()
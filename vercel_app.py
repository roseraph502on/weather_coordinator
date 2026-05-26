# import os
# import sys
# from django.core.wsgi import get_wsgi_application

# # 1. Vercel 서버 환경에 현재 최상위 경로를 강제로 인식시킴
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # 2. 장고 환경설정 연결
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# # 3. WSGI 애플리케이션 생성
# app = get_wsgi_application()
import os
import sys

# 현재 프로젝트 디렉토리를 파이썬 경로에 명시적으로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 장고 환경 설정을 config.settings로 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

# Vercel이 인식할 WSGI 핸들러 'app' 선언
app = get_wsgi_application()
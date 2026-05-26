# vercel_app.py
import os
import sys
from django.core.wsgi import get_wsgi_application

# 1. Vercel 서버 환경에 현재 최상위 경로를 강제로 인식시킴
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2. 장고 환경설정 연결
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 3. WSGI 애플리케이션 생성
app = get_wsgi_application()
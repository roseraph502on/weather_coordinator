import os
from django.core.wsgi import get_wsgi_application

# 장고 설정 파일 연결 (자바의 메인 클래스 지정과 유사)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Vercel이 인식할 수 있도록 'app' 변수에 WSGI 애플리케이션 할당
app = get_wsgi_application()
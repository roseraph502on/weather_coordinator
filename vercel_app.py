import os
import sys

# vercel_app.py는 프로젝트 루트 바로 아래에 있으므로 dirname 한 번만 사용합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 파이썬 검색 경로에 프로젝트 루트 디렉토리를 명시적으로 추가합니다.
sys.path.append(BASE_DIR)

# 장고 환경 설정을 config.settings로 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application
if os.environ.get('VERCEL'):
	try:
		import django
		django.setup()
		from django.core.management import call_command
		call_command('collectstatic', '--noinput')
	except Exception as e:
		print('collectstatic error:', e, file=sys.stderr)

app = get_wsgi_application()
application = app
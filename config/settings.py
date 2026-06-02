from pathlib import Path
import os

# 1. 기본 디렉토리 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 보안 및 디버그 설정
SECRET_KEY = 'django-insecure-nl4m^!)36-@70h0b+6=ra%qp%wscn%9w$a6=phv@%n+zn$w(o('
DEBUG = True

# 3. 허용할 호스트 (로컬 및 Vercel 배포용)
ALLOWED_HOSTS = [
    'weather-coordinator.vercel.app', 
    '.vercel.app', 
    'localhost', 
    '127.0.0.1',
    '*'
]

# 4. 앱 등록
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weather', # 제작하신 날씨 앱
]

# 5. 미들웨어 설정
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# 6. 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# 7. 데이터베이스 (Vercel 배포 환경과 로컬 환경 자동 분기)
if os.environ.get('VERCEL'):
    # Vercel 배포 환경: 읽기 전용이므로 메모리 DB 사용
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  
        }
    }
else:
    # 로컬 개발 환경: 테이블이 깨지지 않도록 실제 파일 DB 사용
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 8. 비밀번호 검증기
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' },
]

# 9. 언어 및 시간대 설정
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# 10. 정적 파일 경로
STATIC_URL = 'static/'
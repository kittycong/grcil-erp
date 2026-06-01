# 구로ERP 배포 가이드

> 로컬 개발에서 프로덕션까지 배포하는 완전한 가이드

---

## 🌍 배포 옵션 비교

| 플랫폼 | 용도 | 비용 | 장점 | 단점 |
|--------|------|------|------|------|
| **GitHub Pages** | 정적 페이지 (프론트엔드) | 무료 | 셋업 간단, 빠름 | 백엔드 불가 |
| **Netlify** | 풀스택 (프론트 + 서버함수) | 무료/유료 | 매우 쉬움, CI/CD 내장 | 함수 시간 제한 |
| **Heroku** | 백엔드 (Flask API) | 유료 | 포괄적, 신뢰도 높음 | 유료화 (2023-11) |
| **Vercel** | Next.js/정적 사이트 | 무료/유료 | 성능 최적화 | Python 미지원 |
| **AWS/Azure** | 엔터프라이즈 | 유료 | 확장성 최고 | 복잡함 |

**추천**: GitHub Pages (프론트) + Heroku/PythonAnywhere (백엔드) 조합

---

## 📋 사전 준비

### 1단계: 깃허브 계정 & 저장소

```bash
# 1. GitHub에서 새 저장소 생성
# https://github.com/new
# 저장소명: grcil-erp
# Public (배포용)
# Add .gitignore: Python
# Add license: MIT

# 2. 로컬에서 저장소 설정
cd grcil-erp
git config user.name "Your Name"
git config user.email "your@email.com"

# 3. 첫 커밋
git add .
git commit -m "Initial commit: GRCIL ERP v0.9.0"
git branch -M main
git remote add origin https://github.com/username/grcil-erp.git
git push -u origin main
```

---

## 🚀 배포 방법 1: GitHub Pages (프론트엔드만)

### 프로덕션 빌드

```bash
# 1. 배포 파일 준비
mkdir -p public
cp grcil_erp_dashboard.html public/index.html
cp *.py public/  # (선택) 파이썬 파일도 포함

# 2. Git 커밋
git add public/
git commit -m "Build: production frontend"
git push origin main

# 3. GitHub 설정
# 저장소 → Settings → Pages
# Source: Deploy from a branch
# Branch: main, folder: /root
```

### 자동 배포 (GitHub Actions)

`.github/workflows/deploy.yml` 파일 사용:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

**결과**: `https://username.github.io/grcil-erp/`

---

## 🚀 배포 방법 2: Netlify (풀스택)

### A. GitHub 연동 배포

#### 1단계: Netlify 계정 생성

```
1. https://www.netlify.com/ 접속
2. "Sign up" → GitHub로 로그인
3. 권한 허용
```

#### 2단계: 새 사이트 생성

```
1. "Add new site" → "Import an existing project"
2. GitHub 저장소 선택 (grcil-erp)
3. 배포 설정 입력:
   - Build command: (비워두기 - 정적 파일만)
   - Publish directory: public
4. "Deploy site" 클릭
```

#### 3단계: 환경 변수 설정

```
1. Site settings → Environment
2. Add variable:
   - FLASK_ENV: production
   - DATABASE_URL: (선택)
```

### B. 수동 배포

```bash
# 1. Netlify CLI 설치
npm install -g netlify-cli

# 2. 로그인
netlify login

# 3. 배포
netlify deploy --prod --dir=public

# 결과: https://grcil-erp.netlify.app/
```

### C. 백엔드 함수 추가 (Netlify Functions)

```bash
# 1. Functions 폴더 생성
mkdir -p netlify/functions

# 2. 함수 작성: netlify/functions/parse-hwpx.js
```

```javascript
// netlify/functions/parse-hwpx.js
const formidable = require('formidable');

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const form = formidable();
    const [fields, files] = await form.parse(event.body);
    
    // Python 스크립트 호출 또는 직접 처리
    
    return {
      statusCode: 200,
      body: JSON.stringify({
        status: 'success',
        message: 'File parsed successfully'
      })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
```

```bash
# 3. netlify.toml 수정
[build]
  command = "npm install"
  functions = "netlify/functions"
  publish = "public"

# 4. 재배포
git push origin main
```

---

## 🚀 배포 방법 3: PythonAnywhere (Python 호스팅)

### 1단계: 계정 생성

```
1. https://www.pythonanywhere.com/ 접속
2. "Pricing" → Free 플랜 선택
3. 계정 생성
```

### 2단계: 웹 앱 설정

```
1. "Web" → "Add a new web app"
2. Framework: Flask
3. Python version: 3.9
```

### 3단계: 코드 업로드

```bash
# PythonAnywhere 콘솔에서
$ git clone https://github.com/username/grcil-erp.git
$ cd grcil-erp
$ pip install -r requirements.txt
```

### 4단계: Flask 앱 설정

```bash
# 편집: /var/www/username_pythonanywhere_com_wsgi.py
import sys
path = '/home/username/grcil-erp'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

### 5단계: 웹 앱 재로드

```
1. "Web" → "Your web apps"
2. 앱 선택 → "Reload"
3. https://username.pythonanywhere.com 접속
```

---

## 🚀 배포 방법 4: Heroku (권장 - 백엔드용)

### ⚠️ 주의: Heroku는 2024년 11월 부터 유료화됨

### 1단계: Heroku 계정 생성

```
https://www.heroku.com/
```

### 2단계: Heroku CLI 설치

```bash
# macOS
brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# https://cli-assets.heroku.com/heroku-x64.exe 다운로드
```

### 3단계: 로그인

```bash
heroku login
```

### 4단계: Procfile 작성

```bash
# grcil-erp/Procfile
web: gunicorn app:app
release: python grcil_database.py
```

### 5단계: 배포

```bash
# 1. Heroku 앱 생성
heroku create grcil-erp

# 2. 환경 변수 설정
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')

# 3. 배포
git push heroku main

# 4. DB 초기화
heroku run python grcil_database.py

# 5. 로그 확인
heroku logs --tail

# 결과: https://grcil-erp.herokuapp.com/
```

---

## 🚀 배포 방법 5: Docker + AWS/Google Cloud

### Dockerfile 작성

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

### Docker 이미지 빌드

```bash
# 1. 이미지 빌드
docker build -t grcil-erp:latest .

# 2. 로컬 테스트
docker run -p 5000:5000 grcil-erp:latest

# 3. Docker Hub에 푸시
docker tag grcil-erp:latest username/grcil-erp:latest
docker push username/grcil-erp:latest
```

### Google Cloud Run 배포

```bash
# 1. gcloud CLI 설치 및 로그인
gcloud auth login
gcloud config set project PROJECT_ID

# 2. 배포
gcloud run deploy grcil-erp \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated

# 결과: https://grcil-erp-xxxxx-an.a.run.app/
```

---

## 📊 배포 체크리스트

### 프로덕션 전 확인사항

- [ ] 코드 정리 (주석, 불필요한 파일 제거)
- [ ] 환경 변수 설정 (.env 파일)
- [ ] DB 마이그레이션 테스트
- [ ] 에러 처리 확인 (500 페이지)
- [ ] HTTPS 활성화
- [ ] CORS 설정 확인
- [ ] 로그 레벨 설정 (DEBUG → INFO)
- [ ] 보안 헤더 추가
- [ ] 백업 정책 수립
- [ ] 모니터링 설정

### 배포 후 확인사항

- [ ] 사이트 접속 가능 확인
- [ ] API 엔드포인트 테스트
- [ ] HWPX 파일 업로드 테스트
- [ ] Excel 파일 업로드 테스트
- [ ] 데이터베이스 쿼리 성능 확인
- [ ] 로그 모니터링
- [ ] 에러 트래킹 (Sentry 등)
- [ ] 성능 모니터링 (New Relic 등)

---

## 🔄 CI/CD 파이프라인

### GitHub Actions 자동 배포

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: |
          pip install -r requirements.txt
          pip install pytest
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.13.15
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: "grcil-erp"
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
      
      - name: Deploy to Netlify
        uses: nwtgck/actions-netlify@v2.0
        with:
          publish-dir: './public'
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

---

## 🔐 보안 체크리스트

- [ ] 민감한 정보 제거 (.env 파일화)
- [ ] HTTPS 활성화
- [ ] CSRF 토큰 추가
- [ ] SQL Injection 방어 (prepared statements)
- [ ] XSS 방어 (input sanitization)
- [ ] CORS 화이트리스트 설정
- [ ] 비밀번호 해싱 (bcrypt 또는 argon2)
- [ ] Rate limiting 구현
- [ ] 접근 로그 기록
- [ ] 정기적 보안 감시

---

## 📊 모니터링 & 로깅

### Sentry (에러 트래킹)

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### CloudFlare (CDN & 보안)

```
1. https://www.cloudflare.com/
2. 도메인 추가
3. Nameserver 변경
4. 캐싱 & DDoS 보호 활성화
```

---

## 📱 도메인 설정

### 커스텀 도메인

```bash
# Netlify/Heroku/GitHub Pages에서 커스텀 도메인 설정
# 예: grcil-erp.kr

# DNS 레코드 추가:
# A Record: @ → your-server-ip
# CNAME Record: www → your-app.netlify.app
```

---

## 🆘 배포 문제 해결

### 문제: "Module not found" 에러

```bash
# 해결
pip install -r requirements.txt
heroku ps:restart
```

### 문제: 포트 접속 불가

```bash
# 확인
heroku logs --tail
lsof -i :5000

# 해결
kill -9 PID
```

### 문제: 데이터베이스 연결 실패

```bash
# 확인
heroku config
heroku run python -c "from grcil_database import GroCILDatabase; db = GroCILDatabase(); print('OK')"
```

---

## 📞 배포 지원

- **Netlify 지원**: support@netlify.com
- **Heroku 지원**: support@heroku.com
- **GitHub Pages 가이드**: https://pages.github.com/
- **우리 지원**: grcil@daum.net

---

**작성일**: 2026-05-28  
**마지막 업데이트**: 2026-05-28  
**버전**: 0.9.0

```
배포 완료 체크리스트:
☐ GitHub 저장소 생성
☐ Netlify 연동
☐ 자동 배포 확인
☐ 커스텀 도메인 설정
☐ SSL/TLS 활성화
☐ 모니터링 설정
☐ 백업 정책 수립
```

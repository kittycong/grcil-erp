# 🚀 구로ERP 깃허브 연동 & 배포 가이드

> **5단계로 완성하는 GitHub 배포**

---

## 📌 현재 상태

✅ **로컬 개발 환경**: 완성  
✅ **Python 파싱 엔진**: 완성  
✅ **Flask API**: 완성  
✅ **대시보드 UI**: 완성  
✅ **Git 저장소**: 초기화 완료 (로컬)  
⏳ **GitHub 원격**: 다음 단계  
⏳ **배포**: 다음 단계  

---

## 🎯 5단계 배포 계획

### Step 1️⃣: GitHub 저장소 생성 (5분)

```bash
# 1. GitHub 웹사이트에서 신규 저장소 생성
# https://github.com/new
#
# 저장소 이름: grcil-erp
# 설명: GRCIL ERP - 장애인자립생활센터 전자결재&HR시스템
# 공개: Public (배포 필요시)
# .gitignore: Python (자동 생성)
# License: MIT

# 2. 터미널에서 연동
cd /home/claude/grcil-erp
git remote add origin https://github.com/YOUR_USERNAME/grcil-erp.git
git branch -M main
git push -u origin main
```

### Step 2️⃣: 로컬 테스트 (10분)

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 데이터베이스 초기화
python grcil_database.py

# 3. 백엔드 서버 실행
python app.py
# 출력: * Running on http://0.0.0.0:5000

# 4. 다른 터미널에서 프론트엔드
python -m http.server 8091

# 5. 브라우저 테스트
# http://127.0.0.1:8091/grcil_erp_dashboard.html
```

### Step 3️⃣: Docker 로컬 테스트 (5분)

```bash
# 1. Docker 설치 확인
docker --version
docker-compose --version

# 2. Docker로 실행
docker-compose up

# 3. 접속
# http://localhost:5000/health  # API 헬스 체크
# http://localhost:8091/...      # 대시보드

# 4. 중지
docker-compose down
```

### Step 4️⃣: Netlify 자동 배포 (15분)

```bash
# 1. Netlify 가입
# https://www.netlify.com/ → "Sign up with GitHub"

# 2. 저장소 선택
# "Add new site" → "Import an existing project" → GitHub 선택

# 3. 빌드 설정
# Build command: (비워두기)
# Publish directory: ./
# Environment variables 추가:
#   - FLASK_ENV: production
#   - SECRET_KEY: (자동 생성)

# 4. 배포 클릭
# Netlify가 자동으로 GitHub 저장소 감시 → 커밋 시 자동 배포

# 결과: https://grcil-erp.netlify.app/
```

### Step 5️⃣: 커스텀 도메인 설정 (10분)

```bash
# Netlify 대시보드에서:
# 1. Site settings → Domain management
# 2. "Custom domain" → grcil-erp.kr 입력
# 3. DNS 레코드 추가 (도메인 제공자):
#    A Record: @ → Netlify IP
#    또는 CNAME: www → grcil-erp.netlify.app
# 4. SSL/TLS 자동 활성화

# 또는 GitHub Pages 사용:
# Settings → Pages → Deploy from branch (main)
# 결과: https://username.github.io/grcil-erp/
```

---

## 📋 Step-by-Step 명령어

### 옵션 A: 자동 설정 스크립트 (권장)

```bash
cd /home/claude/grcil-erp

# 스크립트 실행 (대화형)
bash setup-github.sh YOUR_USERNAME grcil-erp

# 스크립트가 다음을 자동으로 처리:
# ✅ Git 원격 설정
# ✅ 브랜치명 변경 (master → main)
# ✅ SSH 키 설정 (선택)
# ✅ 환경 변수 파일 생성
# ✅ GitHub 푸시 (선택)
```

### 옵션 B: 수동 설정

```bash
cd /home/claude/grcil-erp

# 1. 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/grcil-erp.git

# 2. 브랜치명 변경
git branch -M main

# 3. 첫 푸시
git push -u origin main

# 4. 확인
git remote -v
# 출력:
# origin  https://github.com/YOUR_USERNAME/grcil-erp.git (fetch)
# origin  https://github.com/YOUR_USERNAME/grcil-erp.git (push)
```

---

## 🚀 배포 플랫폼 선택 가이드

### 프론트엔드만 배포 → GitHub Pages ⭐⭐⭐
```bash
# 1. public/ 폴더에 파일 복사
mkdir -p public
cp grcil_erp_dashboard.html public/index.html

# 2. GitHub 설정: Settings → Pages → Deploy from branch (main)
# 3. 결과: https://username.github.io/grcil-erp/
```

### 풀스택 배포 → Netlify ⭐⭐⭐⭐ (권장)
```bash
# 1. https://www.netlify.com/ 가입 (GitHub 연동)
# 2. "Add new site" → GitHub 저장소 선택
# 3. 자동 배포 완료
# 4. 결과: https://grcil-erp.netlify.app/
```

### 백엔드만 배포 → Heroku (유료) ⭐⭐⭐
```bash
# 1. Heroku 가입: https://www.heroku.com/
# 2. heroku login
# 3. heroku create grcil-erp
# 4. git push heroku main
# 5. 결과: https://grcil-erp.herokuapp.com/
```

### Docker 배포 → Google Cloud Run ⭐⭐⭐⭐
```bash
# 1. Google Cloud 계정
# 2. gcloud run deploy grcil-erp --source .
# 3. 결과: https://grcil-erp-xxxxx.a.run.app/
```

---

## 📊 배포 후 확인 사항

```bash
# 1. 헬스 체크
curl https://grcil-erp.netlify.app/health

# 2. API 테스트
curl -X GET https://grcil-erp.netlify.app/api/system/info

# 3. 대시보드 접속
# https://grcil-erp.netlify.app/grcil_erp_dashboard.html

# 4. HWPX 파일 테스트
curl -X POST https://grcil-erp.netlify.app/api/parse/hwpx \
  -F "file=@test.hwpx"

# 5. Excel 파일 테스트
curl -X POST https://grcil-erp.netlify.app/api/parse/excel \
  -F "file=@test.xlsx"
```

---

## 📁 생성된 배포 파일 목록

| 파일 | 목적 | 사용처 |
|------|------|--------|
| `.github/workflows/deploy.yml` | CI/CD 자동 배포 | GitHub Actions |
| `netlify.toml` | Netlify 배포 설정 | Netlify |
| `Procfile` | Heroku 실행 명령어 | Heroku |
| `Dockerfile` | Docker 이미지 빌드 | Docker/Cloud Run |
| `docker-compose.yml` | 로컬 Docker Compose | 로컬 개발 |
| `.env.example` | 환경 변수 템플릿 | 모든 환경 |
| `setup-github.sh` | GitHub 자동 설정 | 초기 설정 |

---

## 🔐 보안 체크리스트

배포 전 반드시 확인하세요:

- [ ] `.env` 파일이 `.gitignore`에 추가됨
- [ ] `grcil_erp.db` (DB 파일)이 `.gitignore`에 추가됨
- [ ] `SECRET_KEY`가 환경 변수로 설정됨
- [ ] FLASK_ENV가 `production`으로 설정됨
- [ ] DEBUG가 `False`로 설정됨
- [ ] HTTPS 활성화됨 (Netlify 자동)
- [ ] CORS 화이트리스트 설정됨
- [ ] 관리자 비밀번호가 안전한가

---

## 📞 배포 문제 해결

### 문제: "Module not found" 에러
```bash
# 해결
pip install -r requirements.txt --upgrade
```

### 문제: "Permission denied" (Git push)
```bash
# SSH 키 확인
ssh -T git@github.com

# 또는 HTTPS 사용
git remote set-url origin https://github.com/username/grcil-erp.git
```

### 문제: "HWPX 파일 파싱 실패"
```bash
# 파일 형식 확인
unzip -l "파일.hwpx"

# document.xml이 있는지 확인
```

### 문제: "포트 이미 사용 중"
```bash
# 포트 변경
python -m http.server 8092
python app.py --port 5001
```

---

## 🎁 GitHub Pages에서 소개 페이지 추가

```bash
# 1. docs/ 폴더 생성
mkdir -p docs

# 2. index.html 작성
cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>구로ERP</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 2rem; }
        h1 { color: #1e7e74; }
    </style>
</head>
<body>
    <h1>🏛️ 구로ERP</h1>
    <p>장애인 자립생활 지원 센터 전자결재 시스템</p>
    <a href="./grcil_erp_dashboard.html">대시보드 접속</a>
</body>
</html>
EOF

# 3. 커밋 & 푸시
git add docs/
git commit -m "docs: Add landing page"
git push origin main
```

---

## ✅ 최종 체크리스트

배포 완료 후 다음을 확인하세요:

- [ ] GitHub 저장소에 모든 파일 푸시됨
- [ ] GitHub Actions 워크플로우 실행 완료
- [ ] Netlify 배포 완료 (녹색 상태)
- [ ] 프로덕션 URL 접속 가능
- [ ] API 헬스 체크 통과
- [ ] HWPX/Excel 파일 업로드 테스트 완료
- [ ] 데이터베이스 쿼리 성능 확인
- [ ] 에러 로깅 설정 완료
- [ ] 모니터링 대시보드 설정 (선택)
- [ ] 백업 정책 수립

---

## 🎉 축하합니다!

구로ERP를 성공적으로 배포했습니다! 🚀

### 다음 단계:

1. **사용자 교육**
   - QUICK_START.md 공유
   - 실제 HWPX/Excel 파일로 테스트

2. **기능 개선** (v1.0)
   - HWP/PDF 보고서 생성
   - 추가 API 엔드포인트

3. **모니터링**
   - 에러 로그 확인
   - 사용자 피드백 수집

4. **확장** (v1.1+)
   - 모바일 앱
   - 클라우드 동기화

---

**작성일**: 2026-05-28  
**상태**: 🟢 배포 준비 완료  
**버전**: 0.9.0 (Beta)

```
🎯 배포 목표:
✅ 로컬 개발 환경 완성
✅ GitHub 저장소 연동
✅ 자동 배포 설정
✅ 프로덕션 배포
→ 이제 시작할 준비가 되었습니다!
```

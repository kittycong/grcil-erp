#!/bin/bash

# 구로ERP GitHub 저장소 연동 및 배포 스크립트
# 사용법: bash setup-github.sh <github-username> <repo-name>

set -e

if [ "$#" -ne 2 ]; then
    echo "❌ 사용법: bash setup-github.sh <github-username> <repo-name>"
    echo ""
    echo "예제:"
    echo "  bash setup-github.sh hwiwon grcil-erp"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME=$2
REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "🚀 구로ERP GitHub 연동 시작"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📌 GitHub 사용자: $GITHUB_USER"
echo "📌 저장소명: $REPO_NAME"
echo "📌 URL: $REPO_URL"
echo ""

# Step 1: 현재 디렉토리 확인
if [ ! -f "app.py" ] || [ ! -f "hwpx_parser.py" ]; then
    echo "❌ 에러: grcil-erp 디렉토리에서 실행해주세요"
    exit 1
fi

echo "✅ Step 1: 현재 디렉토리 확인 완료"

# Step 2: Git 원격 저장소 설정
echo ""
echo "🔧 Step 2: Git 원격 저장소 설정..."

# 이미 원격이 설정되어 있는지 확인
if git remote get-url origin 2>/dev/null; then
    echo "⚠️  원격 저장소가 이미 설정되어 있습니다"
    git remote set-url origin "$REPO_URL"
    echo "✅ 원격 저장소 URL 변경 완료"
else
    git remote add origin "$REPO_URL"
    echo "✅ 원격 저장소 추가 완료"
fi

# Step 3: 브랜치 이름 변경 (master → main)
echo ""
echo "🔧 Step 3: 브랜치 이름 설정..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" = "master" ]; then
    git branch -m main
    echo "✅ 브랜치명 변경: master → main"
fi

# Step 4: SSH 키 설정 (선택사항)
echo ""
echo "🔧 Step 4: SSH 키 설정 (선택사항)"
echo ""
echo "깃허브에 접속할 때 비밀번호를 입력하지 않으려면 SSH 키를 설정하세요."
echo ""
read -p "SSH 키를 설정하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    SSH_KEY_PATH="$HOME/.ssh/grcil_deploy_key"
    
    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo "🔑 SSH 키 생성 중..."
        ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "grcil-erp-deploy"
        echo "✅ SSH 키 생성 완료: $SSH_KEY_PATH"
        echo ""
        echo "📋 다음 공개키를 GitHub에 추가해주세요:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        cat "$SSH_KEY_PATH.pub"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "GitHub Settings → SSH and GPG keys → New SSH key 에서 추가하세요"
        echo ""
    else
        echo "✅ SSH 키가 이미 존재합니다: $SSH_KEY_PATH"
    fi
    
    # SSH 원격 설정
    SSH_REPO_URL="git@github.com:$GITHUB_USER/$REPO_NAME.git"
    git remote set-url origin "$SSH_REPO_URL"
    echo "✅ SSH 원격 저장소로 변경: $SSH_REPO_URL"
fi

# Step 5: 환경 파일 생성
echo ""
echo "🔧 Step 5: 환경 파일 생성..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# 환경 변수 설정
FLASK_ENV=development
FLASK_APP=app.py
DATABASE_URL=sqlite:///.grcil_erp/grcil_erp.db
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DEBUG=False
EOF
    echo "✅ .env 파일 생성 완료"
else
    echo "⚠️  .env 파일이 이미 존재합니다"
fi

# Step 6: 깃 푸시 확인
echo ""
echo "🚀 Step 6: 깃 푸시 준비..."
echo ""
echo "다음 명령어로 저장소에 푸시할 수 있습니다:"
echo ""
echo "  git push -u origin main"
echo ""
read -p "지금 푸시하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 푸시 중..."
    git push -u origin main
    echo "✅ 푸시 완료!"
    echo ""
    echo "📊 저장소 URL: $REPO_URL"
fi

# Step 7: 배포 옵션 제시
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ GitHub 연동 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 다음 배포 옵션 중 선택하세요:"
echo ""
echo "1️⃣  GitHub Pages (정적 사이트 호스팅 - 무료)"
echo "   → README.md 참고"
echo ""
echo "2️⃣  Netlify (자동 배포 - 무료)"
echo "   → https://www.netlify.com/ 에서 GitHub 저장소 연결"
echo "   → DEPLOYMENT.md 참고"
echo ""
echo "3️⃣  Heroku (백엔드 서버 - 유료)"
echo "   → https://www.heroku.com/ 에서 계정 생성"
echo "   → DEPLOYMENT.md 참고"
echo ""
echo "4️⃣  로컬 개발 계속"
echo "   → python app.py"
echo ""
echo "📚 자세한 배포 가이드:"
echo "   → cat DEPLOYMENT.md"
echo ""

# 최종 체크리스트
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 체크리스트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Git 저장소 초기화"
echo "✅ 파일 커밋"
echo "✅ 원격 저장소 연결"
echo "✅ .env 파일 생성"
echo "⏳ GitHub 저장소 생성 (수동)"
echo "⏳ git push -u origin main (위에서 실행)"
echo "⏳ 배포 플랫폼 선택 (위에서 참고)"
echo ""

exit 0

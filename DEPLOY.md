# GitHub 배포 가이드

## 1. GitHub 저장소 생성

1. [GitHub](https://github.com)에 로그인
2. 우측 상단 "+" 버튼 클릭 → "New repository"
3. Repository name: `emotion_experiment` (또는 원하는 이름)
4. Public으로 설정
5. "Create repository" 클릭

## 2. 로컬에서 Git 초기화 및 푸시

프로젝트 디렉토리에서 다음 명령어 실행:

```bash
# 프로젝트 디렉토리로 이동
cd emotion_experiment

# Git 초기화
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: Emotion recognition experiment app"

# GitHub 저장소와 연결 (YOUR_USERNAME을 본인 GitHub 아이디로 변경)
git remote add origin https://github.com/YOUR_USERNAME/emotion_experiment.git

# main 브랜치로 푸시
git branch -M main
git push -u origin main
```

## 3. Streamlit Cloud 배포

### 3.1 Streamlit Cloud 계정 생성
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인

### 3.2 앱 배포
1. "New app" 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: `YOUR_USERNAME/emotion_experiment`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. "Deploy!" 클릭

### 3.3 배포 URL
배포가 완료되면 다음과 같은 URL을 받게 됩니다:
```
https://YOUR_USERNAME-emotion-experiment-app-xxxxx.streamlit.app
```

## 4. 데이터 파일 관리

### 중요: 개인정보 보호
- `data/` 디렉토리는 `.gitignore`에 포함되어 GitHub에 업로드되지 않습니다
- 실험 데이터는 로컬에만 저장됩니다
- 필요시 별도의 클라우드 스토리지(Google Drive, AWS S3 등)를 사용하세요

### 데이터 다운로드
실험 완료 시 앱 내에서 직접 CSV 파일을 다운로드할 수 있습니다.

## 5. 코드 업데이트

코드를 수정한 후 GitHub에 푸시하면 자동으로 Streamlit Cloud에 반영됩니다:

```bash
git add .
git commit -m "설명 메시지"
git push
```

## 6. 환경 변수 설정 (선택사항)

민감한 정보(API 키 등)가 필요한 경우:

1. Streamlit Cloud 대시보드에서 앱 선택
2. "Settings" → "Secrets" 메뉴
3. TOML 형식으로 환경 변수 추가:

```toml
# .streamlit/secrets.toml 형식
api_key = "your_api_key_here"
database_url = "your_database_url"
```

앱에서 사용:
```python
import streamlit as st

api_key = st.secrets["api_key"]
```

## 7. 커스텀 도메인 연결 (선택사항)

Streamlit Cloud에서 커스텀 도메인을 연결할 수 있습니다:

1. 앱 설정에서 "Custom domain" 메뉴
2. 소유한 도메인 입력
3. DNS 레코드 설정 지침 따르기

## 8. 문제 해결

### 앱이 실행되지 않는 경우
1. Streamlit Cloud 로그 확인
2. `requirements.txt`에 모든 패키지가 포함되어 있는지 확인
3. Python 버전 호환성 확인

### 파일이 업로드되지 않는 경우
- `.gitignore` 파일 확인
- Git 상태 확인: `git status`

### 데이터가 저장되지 않는 경우
- Streamlit Cloud는 임시 파일 시스템을 사용합니다
- 영구 저장이 필요하면 외부 데이터베이스 사용 권장

## 9. 추천 개선사항

### 데이터베이스 연동
영구적인 데이터 저장을 위해 다음 옵션 고려:
- Google Sheets API
- Firebase
- PostgreSQL (Supabase)
- MongoDB Atlas

### 인증 시스템
참가자 관리를 위한 로그인 시스템:
```python
import streamlit_authenticator as stauth
```

### 분석 대시보드
실험 결과 분석을 위한 별도 페이지 추가:
- `pages/2_데이터_분석.py`
- 시각화: matplotlib, plotly 등

## 10. 참고 자료

- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub 가이드](https://docs.github.com)

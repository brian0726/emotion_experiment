# 빠른 시작 가이드

## 로컬에서 실행하기

### 1. 필수 요구사항
- Python 3.8 이상
- pip

### 2. 설치

```bash
# 프로젝트 디렉토리로 이동
cd emotion_experiment

# 패키지 설치
pip install -r requirements.txt
```

### 3. 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱이 실행됩니다.

## GitHub에서 배포하기

### 방법 1: 명령줄 사용

```bash
# Git 저장소 초기화 (이미 완료됨)
git init

# GitHub에 저장소 생성 후 연결
git remote add origin https://github.com/YOUR_USERNAME/emotion_experiment.git

# 커밋 및 푸시
git add .
git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

### 방법 2: GitHub Desktop 사용

1. [GitHub Desktop](https://desktop.github.com/) 다운로드 및 설치
2. "Add Local Repository" 클릭
3. `emotion_experiment` 폴더 선택
4. "Publish repository" 클릭
5. 저장소 이름 입력 및 Public으로 설정
6. "Publish Repository" 클릭

## Streamlit Cloud 배포

1. [https://share.streamlit.io/](https://share.streamlit.io/)에 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `YOUR_USERNAME/emotion_experiment`
5. Main file: `app.py`
6. "Deploy!" 클릭

배포 완료 후 받은 URL을 참가자들에게 공유하세요!

## 데이터 수집하기

### 로컬 실행 시
- 실험 완료 후 `data/` 폴더에 CSV 파일이 자동 저장됩니다
- 앱 내에서 "데이터 다운로드" 버튼으로 직접 다운로드 가능

### Streamlit Cloud 배포 시
- 참가자가 실험 완료 후 직접 CSV 파일 다운로드
- 또는 Google Sheets API를 연동하여 자동 저장 (추가 설정 필요)

## 사용 방법

### 실험 진행
1. 참가자 정보 입력 (이름, 성별, 생년월일, DRC 코드, 학번)
2. 실험 안내 확인
3. 각 파트별 연습 시행
4. 본 실험 진행 (총 3개 파트)
5. 완료 후 데이터 다운로드

### 설문조사
- 좌측 사이드바에서 "설문조사" 페이지 선택
- 질문에 응답 후 제출

## 주의사항

1. **Google Drive 파일 설정**
   - 각 감정별 이미지/동영상 파일을 Google Drive에 업로드
   - 공유 설정: "링크가 있는 모든 사용자"
   - `app.py`의 `GIFS` 딕셔너리에 파일 ID 입력

2. **개인정보 보호**
   - `data/` 폴더는 Git에 업로드되지 않음
   - 참가자 데이터는 안전하게 관리하세요

3. **실험 3 (복합 자극)**
   - 현재 이미지와 동영상 URL이 같은 파일을 사용
   - 별도 파일이 필요한 경우 코드 수정 필요

## 문제 해결

### 앱이 시작되지 않는 경우
```bash
# 패키지 재설치
pip install --upgrade -r requirements.txt
```

### 포트가 이미 사용 중인 경우
```bash
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

### 데이터가 저장되지 않는 경우
- `data/` 폴더 권한 확인
- 디스크 공간 확인

## 다음 단계

- `DEPLOY.md`: 상세한 배포 가이드
- `README.md`: 프로젝트 전체 문서
- 코드 커스터마이징: `app.py` 및 설문 페이지 수정

## 지원

문제가 발생하면 GitHub Issues에 등록해 주세요!

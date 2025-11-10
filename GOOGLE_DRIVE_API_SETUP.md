# Google Drive API 설정 가이드

이 애플리케이션은 Google Drive 폴더에서 실험 자극 파일을 가져오기 위해 Google Drive API를 사용합니다.

## 1. Google Cloud Console에서 API 키 생성

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 프로젝트 생성 또는 기존 프로젝트 선택
3. **API 및 서비스 > 사용 설정된 API 및 서비스**로 이동
4. **+ API 및 서비스 사용 설정** 클릭
5. "Google Drive API" 검색 후 사용 설정
6. **사용자 인증 정보** 탭으로 이동
7. **+ 사용자 인증 정보 만들기 > API 키** 선택
8. 생성된 API 키 복사

## 2. API 키 제한 설정 (권장)

보안을 위해 API 키에 제한을 설정하는 것이 좋습니다:

1. 생성된 API 키 옆의 편집 아이콘 클릭
2. **애플리케이션 제한사항**에서 적절한 옵션 선택
3. **API 제한사항**에서 "키 제한" 선택
4. "Google Drive API"만 선택
5. 저장

## 3. Streamlit Cloud에 API 키 설정

### 로컬 개발 환경

1. 프로젝트 루트에 `.streamlit` 폴더 생성
2. `.streamlit/secrets.toml` 파일 생성
3. 다음 내용 추가:

```toml
GOOGLE_DRIVE_API_KEY = "여기에_API_키_입력"
```

### Streamlit Cloud 배포

1. Streamlit Cloud 앱 대시보드에서 앱 선택
2. **Settings > Secrets** 메뉴 클릭
3. 다음 내용 추가:

```toml
GOOGLE_DRIVE_API_KEY = "여기에_API_키_입력"
```

4. Save 클릭

## 4. 구글 드라이브 폴더 공유 설정

API 키로 폴더에 접근하려면 폴더가 **공개 또는 링크가 있는 모든 사용자에게 공유**되어야 합니다:

1. Google Drive에서 각 자극 폴더를 선택
2. 우클릭 > **공유** 선택
3. **링크가 있는 모든 사용자** 또는 **공개**로 설정
4. 권한: **뷰어** (읽기 전용)
5. 완료

## 5. 테스트

설정이 완료되면 앱을 실행하여 자극이 정상적으로 표시되는지 확인하세요.

```bash
streamlit run app.py
```

## 문제 해결

### API 키가 작동하지 않는 경우

1. API 키가 올바르게 복사되었는지 확인
2. Google Drive API가 사용 설정되었는지 확인
3. 폴더가 공개 또는 링크 공유로 설정되었는지 확인
4. API 키 제한 설정이 올바른지 확인

### 파일이 표시되지 않는 경우

1. 폴더 ID가 올바른지 확인 (app.py의 MEDIA_FILES)
2. 폴더에 실제 파일이 있는지 확인
3. 파일이 이미지/동영상 형식인지 확인
4. 브라우저 콘솔에서 오류 메시지 확인

## 보안 주의사항

- `.streamlit/secrets.toml` 파일은 절대 Git에 커밋하지 마세요
- `.gitignore`에 `.streamlit/` 폴더가 포함되어 있는지 확인하세요
- API 키는 안전하게 보관하고 공개하지 마세요

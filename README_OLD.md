# 감정 인식 실험 프로그램

감정 인식 실험을 위한 Streamlit 기반 웹 애플리케이션입니다.

## 기능

### 메인 실험
- **3가지 실험 타입**
  - 실험 1: 이미지 기반 감정 인식
  - 실험 2: 동영상 기반 감정 인식
  - 실험 3: 이미지 + 동영상 복합 감정 인식

- **데이터 수집**
  - 참가자 정보 (이름, 성별, 생년월일, DRC 코드, 학번)
  - 각 문항별 응답 시간 측정
  - 정답/오답 여부 기록
  - 연습 시행과 본 시행 구분

- **실험 진행**
  - 각 파트별 연습 시행 제공
  - 총 21문항 (각 파트당)
  - 중간 휴식 시간 (30초)
  - 진행률 표시

### 설문조사
- 감정 인식 능력에 대한 자가 평가
- 실험 난이도 평가
- 추가 의견 수집

## 설치 및 실행

### 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/emotion_experiment.git
cd emotion_experiment

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

### GitHub를 통한 배포

#### Streamlit Cloud 사용

1. GitHub에 저장소 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
3. "New app" 클릭
4. 저장소 선택 및 배포

#### 배포 URL
배포 후 다음과 같은 형태의 URL로 접근 가능합니다:
```
https://YOUR_USERNAME-emotion-experiment-app-XXXXX.streamlit.app
```

## 데이터 저장

실험 결과는 `data/` 디렉토리에 CSV 형식으로 저장됩니다.

### 파일 구조
```
data/
├── response_학번_날짜_시간.csv  # 실험 응답 데이터
└── survey_이름_날짜_시간.csv    # 설문 데이터
```

### 응답 데이터 컬럼
- `trial_number`: 문항 번호
- `experiment_type`: 실험 타입 (1, 2, 3)
- `correct_emotion`: 정답 감정
- `selected_emotion`: 선택한 감정
- `is_correct`: 정답 여부
- `reaction_time`: 반응 시간 (초)
- `is_practice`: 연습 시행 여부
- `name`: 참가자 이름
- `gender`: 성별
- `birthdate`: 생년월일
- `drc_code`: DRC 코드
- `student_id`: 학번
- `timestamp`: 기록 시각

## 프로젝트 구조

```
emotion_experiment/
├── app.py                    # 메인 실험 앱
├── pages/
│   └── 1_설문조사.py         # 설문조사 페이지
├── data/                     # 데이터 저장 디렉토리
├── requirements.txt          # 패키지 의존성
├── .gitignore               # Git 제외 파일
└── README.md                # 프로젝트 설명
```

## 감정 리스트

총 21개의 감정 카테고리:
- 긍정: 행복, 활기찬, 즐거운, 신뢰하는, 사랑하는
- 부정: 분노, 슬픔, 혐오, 두려, 공포
- 복합: 이조화, 공감하는, 정의하는, 충격받은, 실망하는, 질투하는, 신선망심, 창피함, 우울함
- 중립: 중립, 진지함

## 미디어 파일 설정

Google Drive에 저장된 이미지/동영상 파일을 사용합니다.
- `GIFS` 딕셔너리에 각 감정별 Google Drive 파일 ID 매핑
- URL 형식: `https://drive.google.com/uc?export=view&id={FILE_ID}`

## 특수 기능

### 스킵 기능
특정 학번(2023321063)으로 로그인 시 본 실험에서 문항 스킵 기능 활성화

## 주의사항

1. Google Drive 파일 공유 설정을 "링크가 있는 모든 사용자"로 설정해야 합니다.
2. 실험 3 (복합 자극)의 경우 `CONTEXT_IMAGES`와 `CONTEXT_VIDEOS` 딕셔너리에 파일 ID를 추가해야 합니다.
3. `data/` 디렉토리는 자동으로 생성되며, `.gitignore`에 포함되어 개인정보 보호가 됩니다.

## 개발 정보

- **프레임워크**: Streamlit
- **언어**: Python 3.8+
- **데이터 저장**: CSV
- **원본**: Google Apps Script 기반 실험을 Streamlit으로 전환

## 라이선스

이 프로젝트는 연구 목적으로 사용됩니다.

## 문의

실험 관련 문의사항은 연구팀에 연락해 주세요.

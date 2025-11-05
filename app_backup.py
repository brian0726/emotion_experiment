import streamlit as st
import time
import pandas as pd
import random
from datetime import datetime
import os
import asyncio

# 페이지 설정
st.set_page_config(
    page_title="감정 인식 실험",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #2196f3;
        color: white;
        border-radius: 8px;
        padding: 15px;
        font-size: 18px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1976d2;
        transform: translateY(-2px);
    }
    .choice-button {
        padding: 15px 10px;
        margin: 5px;
        font-size: 16px;
        border: 2px solid #ddd;
        border-radius: 8px;
        background: white;
        cursor: pointer;
    }
    h1 {
        color: #333;
        text-align: center;
    }
    .instructions {
        font-size: 18px;
        line-height: 1.6;
        color: #555;
        background: white;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .timer {
        font-size: 24px;
        font-weight: bold;
        color: #2196f3;
        text-align: center;
        padding: 10px;
        background: white;
        border-radius: 8px;
        margin: 10px 0;
    }
    .prompt-text {
        color: #f44336;
        font-size: 20px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .progress-text {
        text-align: center;
        font-size: 16px;
        color: #666;
        margin: 10px 0;
    }
    .stimulus-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 400px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# 전체 감정 리스트 (23개: 기본 8개 + 복합 15개)
ALL_EMOTIONS = [
    # 기본 정서 (8개)
    "기쁨", "분노", "혐오", "중립", "즐거움", "슬픔", "놀람", "공포",
    # 복합 정서 (15개)
    "애절하는", "실망하는", "공감하는", "힘들어하는", "사랑하는",
    "초조한", "안심하는", "우울한", "불안한", "씁쓸한",
    "활기찬", "쑥스러운", "진지한", "창피한", "피로한"
]

# 감정별 미디어 파일 ID/URL 매핑
# 실제 Google Drive 파일 ID로 교체 필요
# 형식: "감정": {"image": [10개 파일ID], "video": [3개 파일ID], "context": [3개 파일ID]}
MEDIA_FILES = {emotion: {
    "image": [f"IMAGE_{emotion}_{i}" for i in range(10)],  # 각 감정당 이미지 10개
    "video": [f"VIDEO_{emotion}_{i}" for i in range(3)],   # 각 감정당 동영상 3개
    "context": [f"CONTEXT_{emotion}_{i}" for i in range(3)] # 각 감정당 맥락 3개
} for emotion in ALL_EMOTIONS}

# Session State 초기화
def init_session_state():
    if 'stage' not in st.session_state:
        st.session_state.stage = 'participant_info'
    if 'participant_info' not in st.session_state:
        st.session_state.participant_info = {}
    if 'experiment_type' not in st.session_state:
        st.session_state.experiment_type = 1
    if 'current_trial' not in st.session_state:
        st.session_state.current_trial = 0
    if 'trial_order' not in st.session_state:
        st.session_state.trial_order = []
    if 'responses' not in st.session_state:
        st.session_state.responses = []
    if 'is_practice' not in st.session_state:
        st.session_state.is_practice = False
    if 'trial_start_time' not in st.session_state:
        st.session_state.trial_start_time = None
    if 'stimulus_start_time' not in st.session_state:
        st.session_state.stimulus_start_time = None
    if 'current_emotion' not in st.session_state:
        st.session_state.current_emotion = None
    if 'current_choices' not in st.session_state:
        st.session_state.current_choices = []
    if 'skip_enabled' not in st.session_state:
        st.session_state.skip_enabled = False
    if 'show_stimulus' not in st.session_state:
        st.session_state.show_stimulus = True
    if 'show_prompt' not in st.session_state:
        st.session_state.show_prompt = False
    if 'stimulus_shown_time' not in st.session_state:
        st.session_state.stimulus_shown_time = None

# 선택지 생성 (정답 1개 + 랜덤 6개) - 총 7개
def generate_choices(correct_emotion):
    others = [e for e in ALL_EMOTIONS if e != correct_emotion]
    random_others = random.sample(others, 6)
    choices = [correct_emotion] + random_others
    random.shuffle(choices)
    return choices

# Google Drive 미디어 URL 생성
def get_media_url(emotion, media_type='image'):
    """
    media_type: 'image', 'video', 'context'
    해당 감정의 여러 파일 중 1개를 랜덤으로 선택

    랜덤 방식:
    - 이미지: 10개 중 1개 랜덤 선택
    - 동영상: 3개 중 1개 랜덤 선택
    - 맥락: 3개 중 1개 랜덤 선택
    """
    if emotion not in MEDIA_FILES:
        return None

    files = MEDIA_FILES[emotion].get(media_type, [])
    if not files:
        return None

    # 랜덤으로 1개 선택
    file_id = random.choice(files)

    # Google Drive URL 생성
    return f"https://drive.google.com/uc?export=view&id={file_id}"

# 데이터 저장
def save_response_data():
    if not st.session_state.responses:
        return

    df = pd.DataFrame(st.session_state.responses)

    # 참가자 정보 추가
    for key, value in st.session_state.participant_info.items():
        df[key] = value

    # 타임스탬프 추가
    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 파일 저장
    os.makedirs('data', exist_ok=True)
    filename = f"data/response_{st.session_state.participant_info.get('student_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    return filename

# 1. 참가자 정보 입력 화면
def participant_info_screen():
    st.title("감정 인식 실험")

    st.markdown('<div class="instructions">실험에 참가하기 전 다음 정보를 입력해 주세요.</div>', unsafe_allow_html=True)

    with st.form("participant_form"):
        # 이름
        name = st.text_input("이름 *", placeholder="홍길동", key="form_name")

        # 성별
        gender = st.selectbox("성별 *", ["선택해 주세요", "남", "여", "기타"], key="form_gender")

        # 생년월일
        birthdate = st.date_input("생년월일 *", key="form_birthdate")

        # DRC 코드
        st.markdown("##### DRC 코드")
        st.markdown('<p style="color: #666; font-size: 14px; margin-top: -10px;">4자리 혹은 5자리로 된 숫자 아이디</p>', unsafe_allow_html=True)
        drc_code = st.text_input(
            "DRC 코드",
            placeholder="1234 또는 12345",
            key="form_drc",
            label_visibility="collapsed"
        )
        st.markdown('<p style="color: #f44336; font-size: 14px; margin-top: -10px;">※ DRC 코드 미기입 시 크레딧 부여 불가능</p>', unsafe_allow_html=True)

        # 학번
        student_id = st.text_input("학번 *", placeholder="2024123456", key="form_student_id")

        st.markdown('<p style="color: #999; font-size: 12px; margin-top: 10px;">* 필수 입력 항목</p>', unsafe_allow_html=True)

        submitted = st.form_submit_button("다음")

        if submitted:
            if not name or gender == "선택해 주세요" or not student_id:
                st.error("필수 항목(*)을 모두 입력해 주세요.")
            else:
                st.session_state.participant_info = {
                    'name': name,
                    'gender': gender,
                    'birthdate': str(birthdate),
                    'drc_code': drc_code,
                    'student_id': student_id
                }

                # 특정 학번이면 스킵 기능 활성화
                if student_id == '2023321063':
                    st.session_state.skip_enabled = True

                st.session_state.stage = 'instruction'
                st.rerun()

# 2. 실험 안내 화면
def instruction_screen():
    st.title("실험 안내")

    st.markdown("""
    <div class="instructions">
    <p style="font-size: 20px; line-height: 1.8;">
    지금부터 여러분은 사진 및 동영상을 보고<br>
    해당하는 감정의 이름을 고르는 과제를 수행하게 됩니다.<br><br>

    화면에 제시되는 자극을 주의 깊게 관찰하고,<br>
    가장 적합하다고 생각되는 감정 형용사를 선택해 주세요.<br><br>

    실험은 총 3개 파트로 구성되어 있으며,<br>
    각 파트마다 연습 시행 후 본 실험이 진행됩니다.
    </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("실험 시작", use_container_width=True):
        st.session_state.stage = 'practice_intro'
        st.session_state.experiment_type = 1
        st.rerun()

# 3. 연습 안내 화면
def practice_intro_screen():
    st.title("연습 시행")

    exp_type = st.session_state.experiment_type

    instructions_text = {
        1: "다음의 예시를 통해 연습을 해 봅시다. 사진에 가장 적합한 형용사를 선택해 주세요.",
        2: "다음의 예시를 통해 연습을 해 봅시다. 동영상에 가장 적합한 형용사를 선택해 주세요.",
        3: "다음의 예시를 통해 연습을 해 봅시다. 동영상에 가장 적합한 형용사를 선택해 주세요."
    }

    st.markdown(f'<div class="instructions">{instructions_text[exp_type]}</div>', unsafe_allow_html=True)

    if st.button("연습 시작", use_container_width=True):
        # 연습용 감정 선택
        practice_emotion = random.choice(ALL_EMOTIONS)
        st.session_state.current_emotion = practice_emotion
        st.session_state.current_choices = generate_choices(practice_emotion)
        st.session_state.is_practice = True
        st.session_state.trial_start_time = time.time()
        st.session_state.stimulus_shown_time = time.time()
        st.session_state.show_stimulus = True
        st.session_state.show_prompt = False
        st.session_state.stage = 'experiment'
        st.rerun()

# 4. 실험 화면
def experiment_screen():
    emotion = st.session_state.current_emotion
    choices = st.session_state.current_choices
    is_practice = st.session_state.is_practice
    exp_type = st.session_state.experiment_type

    # 진행률 표시
    if not is_practice:
        total_trials = len(st.session_state.trial_order)
        current = st.session_state.current_trial
        progress = current / total_trials if total_trials > 0 else 0

        st.progress(progress)
        st.markdown(f'<div class="progress-text">{current + 1} / {total_trials}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="progress-text">연습 시행</div>', unsafe_allow_html=True)

    # 경과 시간 계산
    elapsed = int(time.time() - st.session_state.trial_start_time) if st.session_state.trial_start_time else 0
    stimulus_elapsed = int(time.time() - st.session_state.stimulus_shown_time) if st.session_state.stimulus_shown_time else 0

    # 타이머 표시
    st.markdown(f'<div class="timer">{elapsed:02d}초</div>', unsafe_allow_html=True)

    # 안내문
    instruction_texts = {
        1: "다음의 이미지를 주의 깊게 봐 주세요. 사진에 가장 적합한 형용사를 선택해 주세요.",
        2: "다음의 동영상을 주의 깊게 봐 주세요. 동영상에 가장 적합한 형용사를 선택해 주세요.",
        3: "다음의 동영상을 주의 깊게 봐 주세요. 동영상에 가장 적합한 형용사를 선택해 주세요."
    }

    if not is_practice:
        st.markdown(f'<div class="instructions">{instruction_texts[exp_type]}</div>', unsafe_allow_html=True)

    # 자극 제시 (5초간)
    if st.session_state.show_stimulus and stimulus_elapsed < 5:
        media_url = get_media_url(emotion, 'video' if exp_type >= 2 else 'image')

        # PLACEHOLDER 이미지 표시
        st.markdown('<div class="stimulus-container">', unsafe_allow_html=True)
        st.info(f"🎬 자극 제시 중... ({emotion})\n\n실제 배포 시 미디어 파일로 교체됩니다.")
        st.markdown('</div>', unsafe_allow_html=True)

        # 자동 리프레시
        time.sleep(0.5)
        st.rerun()

    # 5초 후 자극 숨기기
    elif st.session_state.show_stimulus and stimulus_elapsed >= 5:
        st.session_state.show_stimulus = False
        st.rerun()

    # 5초 후 "빠르게 응답해 주세요" 프롬프트 표시
    if not st.session_state.show_stimulus and elapsed >= 5 and not st.session_state.show_prompt:
        st.session_state.show_prompt = True

    if st.session_state.show_prompt:
        st.markdown('<div class="prompt-text">⚡ 빠르게 응답해 주세요</div>', unsafe_allow_html=True)

    # 10초 후 자동 넘어가기
    if elapsed >= 10:
        handle_choice(None, emotion, is_practice)
        return

    # 선택지 표시 (자극이 사라진 후)
    if not st.session_state.show_stimulus:
        st.markdown("### 가장 적합한 감정을 선택해 주세요")

        # 선택지를 3-3-1 형태로 배치 (총 7개)
        cols1 = st.columns(3)
        for i in range(3):
            with cols1[i]:
                if st.button(choices[i], key=f"choice_{i}", use_container_width=True):
                    handle_choice(choices[i], emotion, is_practice)

        cols2 = st.columns(3)
        for i in range(3, 6):
            with cols2[i-3]:
                if st.button(choices[i], key=f"choice_{i}", use_container_width=True):
                    handle_choice(choices[i], emotion, is_practice)

        cols3 = st.columns([1, 1, 1])
        with cols3[1]:
            if st.button(choices[6], key=f"choice_6", use_container_width=True):
                handle_choice(choices[6], emotion, is_practice)

        # 스킵 버튼 (특정 학번만, 본 실험에서만)
        if st.session_state.skip_enabled and not is_practice:
            st.markdown("---")
            if st.button("⏭️ 스킵", use_container_width=True):
                handle_skip(emotion)

# 선택 처리
def handle_choice(selected_emotion, correct_emotion, is_practice):
    reaction_time = time.time() - st.session_state.trial_start_time
    is_correct = (selected_emotion == correct_emotion) if selected_emotion else False

    # 응답 기록
    response_data = {
        'trial_number': st.session_state.current_trial + 1,
        'experiment_type': st.session_state.experiment_type,
        'correct_emotion': correct_emotion,
        'selected_emotion': selected_emotion if selected_emotion else 'no_response',
        'is_correct': is_correct,
        'reaction_time': reaction_time,
        'is_practice': is_practice
    }

    st.session_state.responses.append(response_data)

    if is_practice:
        st.session_state.stage = 'practice_repeat'
        st.rerun()
    else:
        st.session_state.current_trial += 1

        # 중간 휴식 (약 12번째 문항 후)
        if st.session_state.current_trial == len(st.session_state.trial_order) // 2:
            st.session_state.stage = 'rest'
            st.rerun()
        # 모든 문항 완료
        elif st.session_state.current_trial >= len(st.session_state.trial_order):
            finish_experiment_part()
        else:
            # 다음 문항
            next_trial()

# 스킵 처리
def handle_skip(correct_emotion):
    reaction_time = time.time() - st.session_state.trial_start_time

    response_data = {
        'trial_number': st.session_state.current_trial + 1,
        'experiment_type': st.session_state.experiment_type,
        'correct_emotion': correct_emotion,
        'selected_emotion': 'skipped',
        'is_correct': False,
        'reaction_time': reaction_time,
        'is_practice': False
    }

    st.session_state.responses.append(response_data)
    st.session_state.current_trial += 1

    if st.session_state.current_trial >= len(st.session_state.trial_order):
        finish_experiment_part()
    else:
        next_trial()

# 다음 문항
def next_trial():
    emotion = st.session_state.trial_order[st.session_state.current_trial]
    st.session_state.current_emotion = emotion
    st.session_state.current_choices = generate_choices(emotion)
    st.session_state.trial_start_time = time.time()
    st.session_state.stimulus_shown_time = time.time()
    st.session_state.show_stimulus = True
    st.session_state.show_prompt = False
    st.rerun()

# 5. 연습 반복 확인 화면
def practice_repeat_screen():
    st.title("연습 완료")

    st.markdown('<div class="instructions">추가 연습을 원하십니까?</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("예", use_container_width=True):
            st.session_state.stage = 'practice_intro'
            st.rerun()

    with col2:
        if st.button("아니오, 본 실험 시작", use_container_width=True):
            st.session_state.stage = 'main_intro'
            st.rerun()

# 6. 본 실험 안내 화면
def main_intro_screen():
    st.title("본 실험")

    st.markdown("""
    <div class="instructions">
    연습이 모두 완료되었습니다. 지금부터는 본 실험이 시작됩니다.<br>
    과제는 총 23문항으로 약 3분 가량 소요될 예정입니다.
    </div>
    """, unsafe_allow_html=True)

    if st.button("본 실험 시작", use_container_width=True):
        # 본 실험 문항 준비 (23개)
        trial_order = random.sample(ALL_EMOTIONS, 23)  # 23개 랜덤 선택
        st.session_state.trial_order = trial_order
        st.session_state.current_trial = 0
        st.session_state.is_practice = False

        # 첫 문항 설정
        emotion = trial_order[0]
        st.session_state.current_emotion = emotion
        st.session_state.current_choices = generate_choices(emotion)
        st.session_state.trial_start_time = time.time()
        st.session_state.stimulus_shown_time = time.time()
        st.session_state.show_stimulus = True
        st.session_state.show_prompt = False
        st.session_state.stage = 'experiment'
        st.rerun()

# 7. 휴식 화면
def rest_screen():
    st.title("휴식 시간")

    st.markdown('<div class="instructions">휴식 시간입니다. 30초간 휴식 후 다시 과제가 시작될 예정입니다.</div>', unsafe_allow_html=True)

    # 타이머
    timer_placeholder = st.empty()

    for remaining in range(30, 0, -1):
        timer_placeholder.markdown(f'<div class="timer" style="font-size: 48px;">{remaining}</div>', unsafe_allow_html=True)
        time.sleep(1)

    next_trial()

# 실험 파트 완료 처리
def finish_experiment_part():
    exp_type = st.session_state.experiment_type

    if exp_type == 1:
        st.session_state.stage = 'next_part'
        st.session_state.experiment_type = 2
    elif exp_type == 2:
        st.session_state.stage = 'next_part'
        st.session_state.experiment_type = 3
    else:
        st.session_state.stage = 'completion'

    st.rerun()

# 8. 다음 파트 안내 화면
def next_part_screen():
    exp_type = st.session_state.experiment_type

    titles = {2: "실험 2", 3: "실험 3"}
    texts = {
        2: """첫 번째 실험이 완료되었습니다.

이제 두 번째 실험을 시작합니다.
동영상을 주의 깊게 관찰하고 감정을 선택해 주세요.""",
        3: """두 번째 실험이 완료되었습니다.

이제 마지막 실험을 시작합니다.
동영상을 주의 깊게 관찰하고 감정을 선택해 주세요."""
    }

    st.title(titles[exp_type])

    st.markdown(f'<div class="instructions" style="white-space: pre-line; font-size: 20px;">{texts[exp_type]}</div>', unsafe_allow_html=True)

    if st.button("다음 실험 시작", use_container_width=True):
        st.session_state.stage = 'practice_intro'
        st.rerun()

# 9. 완료 화면
def completion_screen():
    st.title("실험 완료")

    st.markdown('<div class="instructions">실험이 완료되었습니다. 참여해 주셔서 감사합니다.</div>', unsafe_allow_html=True)

    # 데이터 저장
    filename = save_response_data()

    if filename:
        st.success(f"결과가 성공적으로 저장되었습니다.")

        # CSV 다운로드 버튼
        try:
            with open(filename, 'rb') as f:
                st.download_button(
                    label="📥 데이터 다운로드",
                    data=f,
                    file_name=os.path.basename(filename),
                    mime='text/csv',
                    use_container_width=True
                )
        except:
            pass

    st.markdown("---")

    st.markdown("""
    <div class="instructions" style="font-size: 20px;">
    실험이 모두 완료되었습니다.<br><br>

    실험에 참여해 주셔서 감사합니다.<br>
    귀하의 응답은 소중한 연구 자료로 활용될 것입니다.<br><br>

    창을 닫으셔도 좋습니다.
    </div>
    """, unsafe_allow_html=True)

    if st.button("처음으로", use_container_width=True):
        # 세션 초기화
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 메인 앱
def main():
    init_session_state()

    stage = st.session_state.stage

    if stage == 'participant_info':
        participant_info_screen()
    elif stage == 'instruction':
        instruction_screen()
    elif stage == 'practice_intro':
        practice_intro_screen()
    elif stage == 'experiment':
        experiment_screen()
    elif stage == 'practice_repeat':
        practice_repeat_screen()
    elif stage == 'main_intro':
        main_intro_screen()
    elif stage == 'rest':
        rest_screen()
    elif stage == 'next_part':
        next_part_screen()
    elif stage == 'completion':
        completion_screen()

if __name__ == "__main__":
    main()

import streamlit as st
import time
import pandas as pd
import random
from datetime import datetime
import os
import asyncio
from surveys import survey_mfi_screen, survey_phq9_screen, survey_tipi_screen
from gdrive_utils import get_random_file_from_folder, get_file_embed_url

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
    .question-container {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid #2196f3;
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

# 전체 감정 리스트 (23개: 기본 6개 + 복합 16개)
ALL_EMOTIONS = [
    # 기본 정서 (6개)
    "기쁨", "분노", "혐오", "중립", "슬픔", "놀람", "공포",
    # 복합 정서 (16개)
    "즐거움", "애원하는", "실망하는", "공감하는", "충격받은", "질투하는",
    "초조한", "안심하는", "우울한", "불안한", "사랑하는", "쌀쌀맞음",
    "활기찬", "쑥스러운", "진지한", "창피한"
]

# 감정별 미디어 파일 폴더 ID 매핑
# Google Drive 폴더 ID (각 폴더 내에서 랜덤하게 파일 선택)
MEDIA_FILES = {
    "기쁨": {"image": ["1fv7FADmEGxoWsa0nneM4H8SAHJ675Anp"], "video": ["1vo_HVDroVQpP8v6Z1c31lCHSB4qaL3nF"], "context": ["1wx8F1aN1SOWfaaawdSYB2KoNJgBD_BuW"]},
    "분노": {"image": ["1vfb5T2vOkR_WxMIMi-N3BQ5rwJlpEVUq"], "video": ["1cg0ntXkmqQeOT-DAuPDARqoLlqRCosxB"], "context": ["1iwFxh9buPcbqfv1djj2YUUEJISiK5vqj"]},
    "혐오": {"image": ["1jw5NO36f243Sp6wplc1R8JklLz06E3iC"], "video": ["1nRjJ9QZvRI9c578mErvotY9KfBw9W0Js"], "context": ["1wM2Sk6YvZ72ANBfBmAQ3ewh3tkMf2Rjg"]},
    "중립": {"image": ["12pm_q_pUJArqGw5l60k1YZrLSjBzMU4Y"], "video": ["1HJQvKSyFvMs3OluLARkUxWpt30PKf635"], "context": ["1xAzFkRlooY_6HusRd-X0zT97Gdz_agCE"]},
    "슬픔": {"image": ["1Z439Wc2-R09I5K7g0TGDa13qAGI-RCBp"], "video": ["12s0z9toDX3lfMRcdUwjQAyfgUvG_TlFo"], "context": ["1iOAH8hTOKcrwCOLyjf-z4HKBwM3uE3e1"]},
    "놀람": {"image": ["1EzGRc3b3ZrJ5KWtIavg8J7qoSHHRY75C"], "video": ["1025BftCg08x2809Ci37LcMYxzGOiFB2p"], "context": ["1TEKMRsWts-8SriOI0up4Hc6MIoF9IqO4"]},
    "공포": {"image": ["16ab_8uMPXYR_OWhwn-GW2z-FCyEdAUXb"], "video": ["1-AkeI0xWrST247vDNR9KO-km6fJ0y188"], "context": ["1rO60zjXGu5K0-Xm72dktsQGE7Uv2vRO4"]},
    "즐거움": {"image": ["1cMntV216JiXHrRyBJ4JKFaBnt3tSD5-z"], "video": ["16Uol3om5G2MLIcWPh25RRptsIxeWR3G5"], "context": ["1U2P9bnp7_sVYCqa86Z6_I-gm-4camQk-"]},
    "애원하는": {"image": ["1QEHraj991BQIqT5MJgzoaLeD0eyzf03p"], "video": ["1L8N6J_mIO0f4tAb7YoLY8LWp2s2qSam7"], "context": ["1JF6O1eZrbI8OEkWzJdfPsJqsoARyPHfO"]},
    "실망하는": {"image": ["10H67JnwDeUpHnLuIuSE56c7WjzKnh000"], "video": ["15oOTzsVi8b9PbSj_DKkLEDuJ09t-opy1"], "context": ["1hpmTQj2czi8DL7yRXF2ox0q4oNwGd0YF"]},
    "공감하는": {"image": ["1HzvOS1xzUfGHD8-rA7CHnTaQ_hgsXbQ7"], "video": ["1hP8LLCfhZSu2lWuA8sg1rKw6kpvbcSjq"], "context": ["17ZAgZv7jdPylW9SFi3kWWfSVBB4MEFAV"]},
    "충격받은": {"image": ["1KtAQgBFDt62LL4mdi7CaDNZ_pprwmVhx"], "video": ["1mkZB-sVrA1nwp2HmxCiFL2hGB3TE_pfR"], "context": ["1ZAaWg3TYJX7lYH2NBO3Z3pz1b801KRFf"]},
    "질투하는": {"image": ["1gE8BrJsQXvTa_SDhM6Eu94zc65wW0lmV"], "video": ["1l-5bTE_vjhCb0jGERr9qmm-7uQYBuLTq"], "context": ["1xPCmbzEPhM2OKAAVTS5b26iRUflu9Bgu"]},
    "초조한": {"image": ["1NLvpmf2IGIkGWu35MjcdBon4qOfWUxpY"], "video": ["1ZqAWW2rKsoU-eFizdxbM2t8CF3R3H7D3"], "context": ["1x8E8Tj3A-6oUpA2-68OJRqnyL-X9nRmI"]},
    "안심하는": {"image": ["1iPOFbVATnloUgSoEjkuYzFHcX36eBHSm"], "video": ["1w0yZHTAnhn1PVUx92lw5YxAo_dy3OoNH"], "context": ["1Yyj6mCKiGGevfk9mXlCRb1H_C8cbTF2u"]},
    "우울한": {"image": ["1TjfDqWOUtlKj67dL1vGPTKEUcQy0nchB"], "video": ["1iW5K_C4D_ercmX2_v8lVZNSoT4eKFb5t"], "context": ["1co7QJqn80bkp0fUnokdwQqYUPaPiS6IP"]},
    "불안한": {"image": ["1lxmA_sDqh0AULA_9ExbDgRS9I_2tFeP-"], "video": ["1NvrXor0niKLCjTfMwLYkmIp_jVYChuRZ"], "context": ["19wgT5CeK9AzKp5aNulf_xlyngiaoDohn"]},
    "사랑하는": {"image": ["1iT2-rFgOoerKsw9gi6zvYfQbdVESAw4h"], "video": ["1jI4h6X0ial8Lh93u4w6nloufAjk36mFA"], "context": ["1esvlLNRFCtKlB-lhNsEOfGphuSv0-hFF"]},
    "쌀쌀맞음": {"image": ["15m5MXNTNes69iQDlfkjqTfjmnIR3HFo8"], "video": ["1goPaSkqoC84fOgt08Fo64edMJgeWmU1g"], "context": ["1uAUculDrvbvMJwUYg31-LJVvWfhUPaJi"]},
    "활기찬": {"image": ["1iIJVmfhRV49TkfoQyyVaf_w-yoLi-_t5"], "video": ["1pbFnZV5ZVjK9hMaAtR11K91koEOKJpz_"], "context": ["14TSi83RKKEzb2cYbKIZxViwqTYsQs3Qb"]},
    "쑥스러운": {"image": ["1GMO7H-lHEepT2ELFrOtVzdMrsKpoG3o9"], "video": ["1lU_KfpUJjyviW6htZUjmJ3HzDJujqj5C"], "context": ["1vgekNQin5r2yi69FiSJubQ1bLAxFHvkj"]},
    "진지한": {"image": ["12dEIGSDhLCh438jiMfV-XI__HrDrotgC"], "video": ["1GWhCpYC1BKLH7znmZsFFH4KLtLcR2ZDx"], "context": ["1ZRv1MbRZjdQuO8me_4eCPz0NWGzAwX9k"]},
    "창피한": {"image": ["1wHbSk5eB2ZDQGJAs0fsGyS6y186zzu2b"], "video": ["1L04KawJrNgHiR96z13MuZSnRZkt5QjwF"], "context": ["1YVo1ztd4W9afbpC_YCOcorqrnBzO7Cqn"]},
}

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

# Google Drive 미디어 파일 가져오기
def get_media_file(emotion, media_type='image'):
    """
    media_type: 'image', 'video', 'context'
    해당 감정의 폴더에서 랜덤하게 파일 하나를 선택

    Returns:
        파일 정보 딕셔너리 {"id": "...", "name": "...", "mimeType": "...", "url": "..."}
        또는 None
    """
    if emotion not in MEDIA_FILES:
        return None

    folders = MEDIA_FILES[emotion].get(media_type, [])
    if not folders:
        return None

    # 랜덤으로 폴더 1개 선택 (현재는 각 타입당 폴더가 1개씩)
    folder_id = random.choice(folders)

    # MIME 타입 필터 결정
    mime_type_prefix = None
    if media_type == 'image':
        mime_type_prefix = "image/"
    elif media_type == 'video':
        mime_type_prefix = "video/"

    # 폴더에서 랜덤 파일 가져오기
    file_info = get_random_file_from_folder(folder_id, mime_type_prefix)

    if file_info:
        # 임베드 가능한 URL 추가
        file_info['url'] = get_file_embed_url(file_info['id'], file_info.get('mimeType', ''))

    return file_info

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

                st.session_state.stage = 'survey_mfi'
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
        1: "다음의 예시를 통해 연습을 해 봅시다. 다음 화면을 주의 깊게 보고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.",
        2: "다음의 예시를 통해 연습을 해 봅시다. 다음 화면을 주의 깊게 보고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.",
        3: "다음의 예시를 통해 연습을 해 봅시다. 다음 화면을 주의 깊게 보고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요."
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

    # 타이머 표시 (카운트다운)
    if st.session_state.show_stimulus:
        # 자극 제시 중: 5초에서 카운트다운
        remaining = max(0, 5 - stimulus_elapsed)
        st.markdown(f'<div class="timer">남은 시간: {remaining}초</div>', unsafe_allow_html=True)
    else:
        # 응답 대기 중: 10초에서 카운트다운 (전체 15초 - 경과 시간)
        remaining = max(0, 15 - elapsed)
        st.markdown(f'<div class="timer">남은 시간: {remaining}초</div>', unsafe_allow_html=True)

    # 안내문
    instruction_texts = {
        1: "다음 화면을 주의 깊게 보고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.",
        2: "다음 화면을 주의 깊게 보고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.",
        3: "다음 화면을 주의 깊게 보고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요."
    }

    if not is_practice:
        st.markdown(f'<div class="instructions">{instruction_texts[exp_type]}</div>', unsafe_allow_html=True)

    # 자극 제시 (5초간)
    if st.session_state.show_stimulus and stimulus_elapsed < 5:
        # 미디어 타입 결정
        if exp_type == 1:
            media_type = 'image'
        elif exp_type == 2:
            media_type = 'video'
        else:  # exp_type == 3
            media_type = 'context'

        # 구글 드라이브에서 랜덤 파일 가져오기
        file_info = get_media_file(emotion, media_type)

        st.markdown('<div class="stimulus-container">', unsafe_allow_html=True)

        if file_info and 'url' in file_info:
            # 실제 미디어 표시
            mime_type = file_info.get('mimeType', '')
            file_url = file_info['url']

            if mime_type.startswith('image/'):
                # 이미지 표시
                st.image(file_url, use_container_width=True)
            elif mime_type.startswith('video/'):
                # 동영상 표시 (iframe 사용)
                st.markdown(f'''
                    <iframe src="{file_url}"
                            width="100%"
                            height="480"
                            frameborder="0"
                            allow="autoplay; encrypted-media"
                            allowfullscreen>
                    </iframe>
                ''', unsafe_allow_html=True)
            else:
                # 기타 파일 타입
                st.markdown(f'<iframe src="{file_url}" width="100%" height="600" frameborder="0"></iframe>',
                           unsafe_allow_html=True)
        else:
            st.warning(f"미디어를 찾을 수 없습니다: {emotion} - {media_type}")
            st.info("Google Drive API 키가 설정되지 않았거나, 폴더에 파일이 없을 수 있습니다.")

        st.markdown('</div>', unsafe_allow_html=True)

        # 자동 리프레시
        time.sleep(0.5)
        st.rerun()

    # 5초 후 자극 숨기기
    elif st.session_state.show_stimulus and stimulus_elapsed >= 5:
        st.session_state.show_stimulus = False
        st.rerun()

    # 5초 후 "빠르게 응답해 주세요" 프롬프트 표시
    if not st.session_state.show_stimulus and elapsed >= 10 and not st.session_state.show_prompt:
        st.session_state.show_prompt = True

    if st.session_state.show_prompt:
        st.markdown('<div class="prompt-text">⚡ 빠르게 응답해 주세요</div>', unsafe_allow_html=True)

    # 15초 후 자동 넘어가기 (자극 5초 + 응답 10초)
    if elapsed >= 15:
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

        # 모든 문항 완료
        if st.session_state.current_trial >= len(st.session_state.trial_order):
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

# 실험 유형 간 30초 휴식 화면
def rest_between_exp_screen():
    st.title("휴식 시간")
    
    exp_type = st.session_state.experiment_type
    
    if exp_type == 2:
        msg = "첫 번째 실험이 완료되었습니다.\n\n30초간 휴식 후 두 번째 실험이 시작됩니다."
    else:
        msg = "두 번째 실험이 완료되었습니다.\n\n30초간 휴식 후 마지막 실험이 시작됩니다."
    
    st.markdown(f'<div class="instructions" style="white-space: pre-line;">{msg}</div>', unsafe_allow_html=True)
    
    # 타이머
    timer_placeholder = st.empty()
    
    for remaining in range(30, 0, -1):
        timer_placeholder.markdown(f'<div class="timer" style="font-size: 48px;">{remaining}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    # 휴식 후 다음 파트 안내로
    st.session_state.stage = 'next_part'
    st.rerun()
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
        st.session_state.stage = 'rest_between_exp'
        st.session_state.experiment_type = 2
    elif exp_type == 2:
        st.session_state.stage = 'rest_between_exp'
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

    if st.button("종료", use_container_width=True):
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
    elif stage == 'survey_mfi':
        survey_mfi_screen()
    elif stage == 'survey_phq9':
        survey_phq9_screen()
    elif stage == 'survey_tipi':
        survey_tipi_screen()
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
    elif stage == 'rest_between_exp':
        rest_between_exp_screen()
    elif stage == 'rest':
        rest_screen()
    elif stage == 'next_part':
        next_part_screen()
    elif stage == 'completion':
        completion_screen()

if __name__ == "__main__":
    main()

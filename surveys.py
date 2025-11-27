"""
설문조사 화면 모듈
- MFI 피로도 설문
- PHQ-9 우울 설문
- TIPI 성격 설문
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# MFI 피로도 설문 문항
MFI_QUESTIONS = [
    "나는 몸 상태가 좋다.",
    "나는 피곤함을 느낀다.",
    "나는 기운이 없다.",
    "육체적으로 나는 몸 상태가 나쁘다고 생각한다.",
    "나는 쉽게 피곤해진다.",
    "육체적으로 나는 몸 상태가 아주 좋다고 생각한다.",
    "나는 어떤 일을 하는 동안 그 일에 대한 생각을 계속 유지할 수 있다.",
    "나는 어떤 일을 하는 것이 힘겹다.",
    "나는 집중을 잘 할 수 있다.",
    "어떤 일에 집중하기 위해서 많은 노력이 필요하다.",
    "나는 어떠한 일도 하고 싶지 않다.",
    "생각이 쉽게 산만해진다."
]

# PHQ-9 우울 설문 문항
PHQ9_QUESTIONS = [
    "기분이 가라앉거나, 우울하거나, 희망이 없다고 느꼈다.",
    "평소 하던 일에 대한 흥미가 없었거나 즐거움을 느끼지 못했다.",
    "잠들기가 어렵거나 자주 깼다 / 혹은 너무 많이 잤다.",
    "평소보다 식욕이 줄었다 / 혹은 평소보다 많이 먹었다.",
    "다른 사람들에게서 볼 때 혹은 본인이 느끼기에 평소보다 몸이 느려졌거나 / 혹은 너무 안절부절 못하여 가만히 앉아 있을 수 없었다.",
    "피곤하거나 기운이 없었다.",
    "내가 잘못했거나, 실패했다고 생각이 들었다 / 혹은 자신과 가족을 실망시켰다고 생각했다.",
    "신문을 읽거나 TV를 보는 것과 같은 일상적인 일에도 집중할 수가 없었다.",
    "차라리 죽는 것이 더 낫겠다고 생각했거나 / 혹은 자해할 생각을 했다."
]

# TIPI 성격 설문 문항
TIPI_QUESTIONS = [
    "외향적이다. 적극적이다.",
    "비판적이다. 논쟁을 좋아한다.",
    "신뢰할 수 있다. 자기 절제를 잘한다.",
    "근심 걱정이 많다. 쉽게 흥분한다.",
    "새로운 경험들에 개방적이다. 복잡다단하다.",
    "내성적이다. 조용하다.",
    "동정심이 많다. 다정다감하다.",
    "정리정돈을 잘 못한다. 덤벙댄다.",
    "차분하다. 감정의 기복이 적다.",
    "변화를 싫어한다. 창의적이지 못하다."
]

# 1. MFI 피로도 설문 화면
def survey_mfi_screen():
    st.title("피로도 설문 (MFI)")

    st.markdown("""
    <div class="instructions">
    <strong>Multidimensional Fatigue Inventory (다차원 피로 척도)</strong><br><br>
    현재 상태를 가장 잘 반영하는 정도에 표시하세요.<br>
    </div>
    """, unsafe_allow_html=True)

    with st.form("mfi_form"):
        # 라디오 버튼 간격 조정 CSS - 5개 버튼을 균등하게 배치
        st.markdown("""
        <style>
        /* MFI 라디오 버튼 강제 균등 배치 - 더 구체적인 selector */
        .stRadio > div {
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important;
            width: 100% !important;
            gap: 0 !important;
        }
        .stRadio > div > label {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 5px !important;
            width: 100% !important;
        }
        .stRadio > div > label > div {
            margin: 0 auto !important;
        }
        /* 라디오 버튼 텍스트 숨기기 (숫자만 표시) */
        .stRadio > div > label > div:last-child {
            display: flex !important;
            justify-content: center !important;
        }
        </style>
        """, unsafe_allow_html=True)

        responses = {}

        for i, question in enumerate(MFI_QUESTIONS, 1):
            st.markdown(f"""
            <div class="question-container">
            <strong>{i}. {question}</strong>
            </div>
            """, unsafe_allow_html=True)

            responses[f"MFI_Q{i}"] = st.radio(
                f"문항 {i}",
                options=[1, 2, 3, 4, 5],
                index=None,
                format_func=lambda x: f"{x}",
                horizontal=True,
                key=f"MFI_Q{i}",
                label_visibility="collapsed"
            )

            # 척도 레이블 - 컬럼 사용하여 정확한 20% 위치에 배치
            label_cols = st.columns(5)
            label_cols[0].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>전혀 그렇지 않다</div>", unsafe_allow_html=True)
            label_cols[1].markdown("<div style='text-align: center; font-size: 11px; color: #666;'></div>", unsafe_allow_html=True)
            label_cols[2].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>보통이다</div>", unsafe_allow_html=True)
            label_cols[3].markdown("<div style='text-align: center; font-size: 11px; color: #666;'></div>", unsafe_allow_html=True)
            label_cols[4].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>매우 그렇다</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button("다음")

        if submitted:
            # 미응답 검증
            if None in responses.values():
                st.error("모든 문항에 응답해 주세요.")
                st.stop()

            # 설문 데이터 저장
            survey_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'survey_type': 'MFI',
                **st.session_state.participant_info,
                **responses
            }

            # session_state에 저장
            if 'survey_responses' not in st.session_state:
                st.session_state.survey_responses = {}
            st.session_state.survey_responses['mfi'] = survey_data

            # 다음 단계로
            st.session_state.stage = 'survey_phq9'
            st.rerun()

# 2. PHQ-9 우울 설문 화면
def survey_phq9_screen():
    st.title("우울 설문 (PHQ-9)")

    st.markdown("""
    <div class="instructions">
    <strong>Patient Health Questionnaire-9 (환자 건강 질문지)</strong><br><br>
    지난 2주간, 얼마나 자주 다음과 같은 문제들을 겪으셨습니까?<br>
    </div>
    """, unsafe_allow_html=True)

    with st.form("phq9_form"):
        # 라디오 버튼 간격 조정 CSS - 4개 버튼을 균등하게 배치
        st.markdown("""
        <style>
        /* PHQ-9 라디오 버튼 강제 균등 배치 - 더 구체적인 selector */
        .stRadio > div {
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important;
            width: 100% !important;
            gap: 0 !important;
        }
        .stRadio > div > label {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 5px !important;
            width: 100% !important;
        }
        .stRadio > div > label > div {
            margin: 0 auto !important;
        }
        /* 라디오 버튼 텍스트 숨기기 (숫자만 표시) */
        .stRadio > div > label > div:last-child {
            display: flex !important;
            justify-content: center !important;
        }
        </style>
        """, unsafe_allow_html=True)

        responses = {}

        for i, question in enumerate(PHQ9_QUESTIONS, 1):
            st.markdown(f"""
            <div class="question-container">
            <strong>{i}. {question}</strong>
            </div>
            """, unsafe_allow_html=True)

            responses[f"PHQ9_Q{i}"] = st.radio(
                f"문항 {i}",
                options=[0, 1, 2, 3],
                index=None,
                format_func=lambda x: f"{x}",
                horizontal=True,
                key=f"PHQ9_Q{i}",
                label_visibility="collapsed"
            )

            # 척도 레이블 - 컬럼 사용하여 정확한 25% 위치에 배치
            label_cols = st.columns(4)
            label_cols[0].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>전혀 아님</div>", unsafe_allow_html=True)
            label_cols[1].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>2~3일 이상</div>", unsafe_allow_html=True)
            label_cols[2].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>7일 이상</div>", unsafe_allow_html=True)
            label_cols[3].markdown("<div style='text-align: center; font-size: 11px; color: #666;'>거의 매일</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button("다음")

        if submitted:
            # 미응답 검증
            if None in responses.values():
                st.error("모든 문항에 응답해 주세요.")
                st.stop()

            # 총점 계산
            total_score = sum(responses.values())

            # 설문 데이터 저장
            survey_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'survey_type': 'PHQ-9',
                'total_score': total_score,
                **st.session_state.participant_info,
                **responses
            }

            # session_state에 저장
            if 'survey_responses' not in st.session_state:
                st.session_state.survey_responses = {}
            st.session_state.survey_responses['phq9'] = survey_data

            # 다음 단계로
            st.session_state.stage = 'survey_tipi'
            st.rerun()

# 3. TIPI 성격 설문 화면
def survey_tipi_screen():
    st.title("성격 설문 (TIPI)")

    st.markdown("""
    <div class="instructions">
    <strong>Ten-Item Personality Inventory (10문항 성격 척도)</strong><br><br>
    다음은 귀하가 평소에 어떤 사람인지에 대한 질문입니다.<br>
    각 문항에 대해 귀하에게 얼마나 해당되는지 응답해 주세요.<br><br>
    <strong>내가 보기에 나 자신은:</strong><br>
    </div>
    """, unsafe_allow_html=True)

    scale_labels = {
        1: "전혀 동의하지 않는다",
        2: "동의하지 않는다",
        3: "그다지 동의하지 않는다",
        4: "중간이다",
        5: "어느 정도 동의한다",
        6: "동의한다",
        7: "매우 동의한다"
    }

    with st.form("tipi_form"):
        st.markdown("""
        <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <strong>응답 척도</strong><br>
        1 = 전혀 동의하지 않는다 | 4 = 중간이다 | 7 = 매우 동의한다
        </div>
        """, unsafe_allow_html=True)

        responses = {}

        for i, question in enumerate(TIPI_QUESTIONS, 1):
            st.markdown(f"""
            <div class="question-container">
            <strong>{i}. _____ {question}</strong>
            </div>
            """, unsafe_allow_html=True)

            responses[f"TIPI_Q{i}"] = st.selectbox(
                f"문항 {i}",
                options=[None, 1, 2, 3, 4, 5, 6, 7],
                format_func=lambda x: "선택하세요" if x is None else f"{x} - {scale_labels[x]}",
                key=f"TIPI_Q{i}",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)

        submitted = st.form_submit_button("설문 완료 (실험 시작)")

        if submitted:
            # 미응답 검증
            if None in responses.values():
                st.error("모든 문항에 응답해 주세요.")
                st.stop()

            # 설문 데이터 저장
            survey_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'survey_type': 'TIPI',
                **st.session_state.participant_info,
                **responses
            }

            # session_state에 저장
            if 'survey_responses' not in st.session_state:
                st.session_state.survey_responses = {}
            st.session_state.survey_responses['tipi'] = survey_data

            # 모든 설문 데이터를 파일로 저장
            save_all_surveys()

            # 실험 안내로
            st.session_state.stage = 'instruction'
            st.rerun()

# 모든 설문 데이터 저장
def save_all_surveys():
    if 'survey_responses' not in st.session_state:
        return

    os.makedirs('data', exist_ok=True)
    student_id = st.session_state.participant_info.get('student_id', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # 각 설문을 개별 CSV로 저장
    for survey_type, data in st.session_state.survey_responses.items():
        filename = f"data/{survey_type}_{student_id}_{timestamp}.csv"
        df = pd.DataFrame([data])
        df.to_csv(filename, index=False, encoding='utf-8-sig')

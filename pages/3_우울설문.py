import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="우울 설문 (PHQ-9)",
    page_icon="💙",
    layout="centered"
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
    }
    .stButton>button:hover {
        background-color: #1976d2;
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
    .question-container {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 15px 0;
        border-left: 4px solid #2196f3;
    }
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session State 초기화
if 'phq9_completed' not in st.session_state:
    st.session_state.phq9_completed = False

st.title("💙 우울 설문 (PHQ-9)")

if not st.session_state.phq9_completed:
    st.markdown("""
    <div class="instructions">
    <strong>Patient Health Questionnaire-9 (환자 건강 질문지)</strong><br><br>
    지난 2주간, 얼마나 자주 다음과 같은 문제들을 겪으셨습니까?
    </div>
    """, unsafe_allow_html=True)

    # PHQ-9 문항
    phq9_questions = [
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

    scale_options = {
        0: "전혀 아님",
        1: "며칠간",
        2: "일주일 이상",
        3: "거의 매일"
    }

    with st.form("phq9_form"):
        responses = {}

        for i, question in enumerate(phq9_questions, 1):
            st.markdown(f"""
            <div class="question-container">
            <strong>{i}. {question}</strong>
            </div>
            """, unsafe_allow_html=True)

            responses[f"q{i}"] = st.radio(
                f"문항 {i}",
                options=[0, 1, 2, 3],
                format_func=lambda x: scale_options[x],
                horizontal=True,
                key=f"phq9_q{i}",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)

        # 경고 메시지
        st.markdown("""
        <div class="warning-box">
        ⚠️ <strong>중요:</strong> 만약 9번 문항에서 "며칠간" 이상으로 응답하신 경우,
        전문가의 도움을 받으실 것을 권장드립니다.<br><br>

        <strong>위기 상담 연락처:</strong><br>
        • 자살예방 상담전화: 1393<br>
        • 정신건강 위기상담: 1577-0199<br>
        • 청소년 상담: 1388
        </div>
        """, unsafe_allow_html=True)

        # 참가자 정보
        st.markdown("---")
        st.markdown("### 참가자 정보")
        name = st.text_input("이름", key="phq9_name")
        student_id = st.text_input("학번", key="phq9_student_id")

        submitted = st.form_submit_button("제출")

        if submitted:
            if not name or not student_id:
                st.error("이름과 학번을 모두 입력해 주세요.")
            else:
                # 총점 계산
                total_score = sum(responses.values())

                # 설문 데이터 저장
                survey_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': name,
                    'student_id': student_id,
                    'survey_type': 'PHQ-9',
                    'total_score': total_score
                }

                # 응답 추가
                for key, value in responses.items():
                    survey_data[key] = value

                # CSV 파일로 저장
                os.makedirs('data', exist_ok=True)
                filename = f"data/phq9_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                df = pd.DataFrame([survey_data])
                df.to_csv(filename, index=False, encoding='utf-8-sig')

                st.session_state.phq9_completed = True
                st.session_state.phq9_score = total_score
                st.session_state.phq9_q9 = responses['q9']
                st.rerun()

else:
    st.success("✅ 우울 설문이 성공적으로 제출되었습니다!")

    # 총점에 따른 안내
    score = st.session_state.get('phq9_score', 0)
    q9_score = st.session_state.get('phq9_q9', 0)

    st.markdown(f"""
    <div class="instructions">
    설문에 참여해 주셔서 감사합니다.<br>
    총점: <strong>{score}점</strong>
    </div>
    """, unsafe_allow_html=True)

    # 심각도 안내
    if score < 5:
        severity = "최소 수준"
        color = "#4caf50"
    elif score < 10:
        severity = "경미한 수준"
        color = "#8bc34a"
    elif score < 15:
        severity = "중간 수준"
        color = "#ff9800"
    elif score < 20:
        severity = "중증도 수준"
        color = "#ff5722"
    else:
        severity = "심각한 수준"
        color = "#f44336"

    st.markdown(f"""
    <div style="background: {color}20; border-left: 4px solid {color}; padding: 15px; border-radius: 5px; margin: 20px 0;">
    <strong>우울 심각도:</strong> {severity}
    </div>
    """, unsafe_allow_html=True)

    # 9번 문항 경고
    if q9_score >= 1:
        st.markdown("""
        <div class="warning-box">
        ⚠️ <strong>전문가 상담 권장</strong><br><br>
        자해나 자살 생각이 있으신 경우, 전문가의 도움을 받으시기를 적극 권장드립니다.<br><br>

        <strong>위기 상담 연락처:</strong><br>
        • 자살예방 상담전화: 1393 (24시간)<br>
        • 정신건강 위기상담: 1577-0199 (24시간)<br>
        • 청소년 상담: 1388 (24시간)
        </div>
        """, unsafe_allow_html=True)

    if st.button("새로운 설문 작성"):
        st.session_state.phq9_completed = False
        st.rerun()

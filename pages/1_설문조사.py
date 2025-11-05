import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="설문조사",
    page_icon="📋",
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
</style>
""", unsafe_allow_html=True)

# Session State 초기화
if 'survey_completed' not in st.session_state:
    st.session_state.survey_completed = False

st.title("📋 설문조사")

if not st.session_state.survey_completed:
    st.markdown("""
    <div class="instructions">
    다음 설문에 응답해 주세요. 모든 질문에 솔직하게 답변해 주시면 감사하겠습니다.
    </div>
    """, unsafe_allow_html=True)

    with st.form("survey_form"):
        st.subheader("기본 정보")

        name = st.text_input("이름")
        age = st.number_input("나이", min_value=10, max_value=100, value=20)
        gender = st.selectbox("성별", ["선택해 주세요", "남", "여", "기타"])

        st.markdown("---")
        st.subheader("감정 인식에 대한 질문")

        q1 = st.slider(
            "1. 평소 다른 사람의 감정을 잘 파악하는 편입니까?",
            min_value=1,
            max_value=7,
            value=4,
            help="1: 전혀 그렇지 않다, 7: 매우 그렇다"
        )

        q2 = st.slider(
            "2. 사진이나 영상을 통해 감정을 읽는 것이 쉽다고 생각합니까?",
            min_value=1,
            max_value=7,
            value=4,
            help="1: 전혀 그렇지 않다, 7: 매우 그렇다"
        )

        q3 = st.slider(
            "3. 복잡한 감정(여러 감정이 섞인)을 구분하는 것이 어렵습니까?",
            min_value=1,
            max_value=7,
            value=4,
            help="1: 전혀 그렇지 않다, 7: 매우 그렇다"
        )

        st.markdown("---")
        st.subheader("실험 관련 질문")

        q4 = st.radio(
            "4. 이전에 비슷한 감정 인식 실험에 참여한 적이 있습니까?",
            ["없음", "1-2회", "3회 이상"]
        )

        q5 = st.text_area(
            "5. 감정을 판단할 때 주로 어떤 요소를 고려했습니까?",
            placeholder="예: 표정, 목소리 톤, 상황 맥락 등"
        )

        q6 = st.slider(
            "6. 실험 과제의 난이도는 어떠했습니까?",
            min_value=1,
            max_value=7,
            value=4,
            help="1: 매우 쉬웠다, 7: 매우 어려웠다"
        )

        st.markdown("---")
        st.subheader("추가 의견")

        q7 = st.text_area(
            "7. 실험에 대한 의견이나 어려웠던 점이 있다면 자유롭게 작성해 주세요.",
            placeholder="(선택사항)"
        )

        submitted = st.form_submit_button("제출")

        if submitted:
            if not name or gender == "선택해 주세요":
                st.error("필수 항목을 모두 입력해 주세요.")
            else:
                # 설문 데이터 저장
                survey_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': name,
                    'age': age,
                    'gender': gender,
                    'q1_emotion_recognition': q1,
                    'q2_media_emotion_reading': q2,
                    'q3_complex_emotion_difficulty': q3,
                    'q4_previous_experience': q4,
                    'q5_decision_factors': q5,
                    'q6_task_difficulty': q6,
                    'q7_additional_comments': q7
                }

                # CSV 파일로 저장
                os.makedirs('data', exist_ok=True)
                filename = f"data/survey_{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                df = pd.DataFrame([survey_data])
                df.to_csv(filename, index=False, encoding='utf-8-sig')

                st.session_state.survey_completed = True
                st.rerun()

else:
    st.success("✅ 설문이 성공적으로 제출되었습니다!")

    st.markdown("""
    <div class="instructions">
    설문에 참여해 주셔서 감사합니다.<br>
    귀하의 소중한 의견은 연구 개선에 큰 도움이 됩니다.
    </div>
    """, unsafe_allow_html=True)

    if st.button("새로운 설문 작성"):
        st.session_state.survey_completed = False
        st.rerun()

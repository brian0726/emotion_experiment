import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="피로도 설문 (MFI)",
    page_icon="😴",
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
</style>
""", unsafe_allow_html=True)

# Session State 초기화
if 'mfi_completed' not in st.session_state:
    st.session_state.mfi_completed = False

st.title("😴 피로도 설문 (MFI)")

if not st.session_state.mfi_completed:
    st.markdown("""
    <div class="instructions">
    <strong>Multidimensional Fatigue Inventory (다차원 피로 척도)</strong><br><br>
    현재 상태를 가장 잘 반영하는 정도에 표시하세요.
    </div>
    """, unsafe_allow_html=True)

    # MFI 문항
    mfi_questions = [
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

    scale_labels = ["1<br>전혀<br>그렇지<br>않다", "2", "3", "4", "5<br>매우<br>그렇다"]

    with st.form("mfi_form"):
        responses = {}

        for i, question in enumerate(mfi_questions, 1):
            st.markdown(f"""
            <div class="question-container">
            <strong>{i}. {question}</strong>
            </div>
            """, unsafe_allow_html=True)

            responses[f"q{i}"] = st.radio(
                f"문항 {i}",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: f"{x}",
                horizontal=True,
                key=f"mfi_q{i}",
                label_visibility="collapsed"
            )

            st.markdown("<br>", unsafe_allow_html=True)

        # 참가자 정보
        st.markdown("---")
        st.markdown("### 참가자 정보")
        name = st.text_input("이름", key="mfi_name")
        student_id = st.text_input("학번", key="mfi_student_id")

        submitted = st.form_submit_button("제출")

        if submitted:
            if not name or not student_id:
                st.error("이름과 학번을 모두 입력해 주세요.")
            else:
                # 설문 데이터 저장
                survey_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': name,
                    'student_id': student_id,
                    'survey_type': 'MFI'
                }

                # 응답 추가
                for key, value in responses.items():
                    survey_data[key] = value

                # CSV 파일로 저장
                os.makedirs('data', exist_ok=True)
                filename = f"data/mfi_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                df = pd.DataFrame([survey_data])
                df.to_csv(filename, index=False, encoding='utf-8-sig')

                st.session_state.mfi_completed = True
                st.rerun()

else:
    st.success("✅ 피로도 설문이 성공적으로 제출되었습니다!")

    st.markdown("""
    <div class="instructions">
    설문에 참여해 주셔서 감사합니다.<br>
    귀하의 소중한 응답은 연구에 큰 도움이 됩니다.
    </div>
    """, unsafe_allow_html=True)

    if st.button("새로운 설문 작성"):
        st.session_state.mfi_completed = False
        st.rerun()

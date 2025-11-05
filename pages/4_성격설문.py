import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="성격 설문 (TIPI)",
    page_icon="🎭",
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
if 'tipi_completed' not in st.session_state:
    st.session_state.tipi_completed = False

st.title("🎭 성격 설문 (TIPI)")

if not st.session_state.tipi_completed:
    st.markdown("""
    <div class="instructions">
    <strong>Ten-Item Personality Inventory (10문항 성격 척도)</strong><br><br>
    다음은 귀하가 평소에 어떤 사람인지에 대한 질문입니다.<br>
    각 문항에 대해 귀하에게 얼마나 해당되는지 응답해 주세요.<br><br>
    <strong>내가 보기에 나 자신은:</strong>
    </div>
    """, unsafe_allow_html=True)

    # TIPI 문항 (한국판)
    tipi_questions = [
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
        1 = 전혀 동의하지 않는다<br>
        4 = 중간이다<br>
        7 = 매우 동의한다
        </div>
        """, unsafe_allow_html=True)

        responses = {}

        for i, question in enumerate(tipi_questions, 1):
            st.markdown(f"""
            <div class="question-container">
            <strong>{i}. {question}</strong>
            </div>
            """, unsafe_allow_html=True)

            # 슬라이더 사용
            responses[f"q{i}"] = st.slider(
                f"문항 {i}",
                min_value=1,
                max_value=7,
                value=4,
                key=f"tipi_q{i}",
                label_visibility="collapsed"
            )

            # 현재 선택된 값 표시
            st.caption(f"선택: {scale_labels[responses[f'q{i}']]}")

            st.markdown("<br>", unsafe_allow_html=True)

        # 참가자 정보
        st.markdown("---")
        st.markdown("### 참가자 정보")
        name = st.text_input("이름", key="tipi_name")
        student_id = st.text_input("학번", key="tipi_student_id")

        submitted = st.form_submit_button("제출")

        if submitted:
            if not name or not student_id:
                st.error("이름과 학번을 모두 입력해 주세요.")
            else:
                # Big Five 차원 계산
                # 외향성 (Extraversion): (Q1 + (8-Q6)) / 2
                # 우호성 (Agreeableness): ((8-Q2) + Q7) / 2
                # 성실성 (Conscientiousness): (Q3 + (8-Q8)) / 2
                # 정서적 안정성 (Emotional Stability): ((8-Q4) + Q9) / 2
                # 개방성 (Openness): (Q5 + (8-Q10)) / 2

                extraversion = (responses['q1'] + (8 - responses['q6'])) / 2
                agreeableness = ((8 - responses['q2']) + responses['q7']) / 2
                conscientiousness = (responses['q3'] + (8 - responses['q8'])) / 2
                emotional_stability = ((8 - responses['q4']) + responses['q9']) / 2
                openness = (responses['q5'] + (8 - responses['q10'])) / 2

                # 설문 데이터 저장
                survey_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': name,
                    'student_id': student_id,
                    'survey_type': 'TIPI',
                    'extraversion': round(extraversion, 2),
                    'agreeableness': round(agreeableness, 2),
                    'conscientiousness': round(conscientiousness, 2),
                    'emotional_stability': round(emotional_stability, 2),
                    'openness': round(openness, 2)
                }

                # 응답 추가
                for key, value in responses.items():
                    survey_data[key] = value

                # CSV 파일로 저장
                os.makedirs('data', exist_ok=True)
                filename = f"data/tipi_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                df = pd.DataFrame([survey_data])
                df.to_csv(filename, index=False, encoding='utf-8-sig')

                st.session_state.tipi_completed = True
                st.session_state.tipi_results = {
                    '외향성 (Extraversion)': extraversion,
                    '우호성 (Agreeableness)': agreeableness,
                    '성실성 (Conscientiousness)': conscientiousness,
                    '정서적 안정성 (Emotional Stability)': emotional_stability,
                    '개방성 (Openness)': openness
                }
                st.rerun()

else:
    st.success("✅ 성격 설문이 성공적으로 제출되었습니다!")

    st.markdown("""
    <div class="instructions">
    설문에 참여해 주셔서 감사합니다.<br>
    아래는 Big Five 성격 특성 결과입니다.
    </div>
    """, unsafe_allow_html=True)

    # Big Five 결과 표시
    results = st.session_state.get('tipi_results', {})

    for trait, score in results.items():
        # 점수에 따른 색상
        if score >= 5.5:
            color = "#4caf50"
            level = "높음"
        elif score >= 4.5:
            color = "#2196f3"
            level = "중간"
        else:
            color = "#ff9800"
            level = "낮음"

        st.markdown(f"""
        <div style="background: white; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {color};">
        <strong>{trait}</strong><br>
        <div style="display: flex; align-items: center; margin-top: 10px;">
            <div style="flex-grow: 1; background: #e0e0e0; height: 30px; border-radius: 15px; overflow: hidden;">
                <div style="width: {score/7*100}%; background: {color}; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    {score:.2f}
                </div>
            </div>
            <span style="margin-left: 10px; font-weight: bold; color: {color};">{level}</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    # Big Five 설명
    with st.expander("📖 Big Five 성격 특성 설명"):
        st.markdown("""
        **1. 외향성 (Extraversion)**
        - 사교적, 활동적, 적극적인 정도
        - 높음: 사람들과 어울리기를 좋아하고 에너지가 넘침
        - 낮음: 조용하고 독립적이며 혼자 있는 것을 선호

        **2. 우호성 (Agreeableness)**
        - 타인에 대한 동정심, 협조적인 정도
        - 높음: 타인을 배려하고 협력적이며 공감을 잘함
        - 낮음: 비판적이고 경쟁적이며 자기주장이 강함

        **3. 성실성 (Conscientiousness)**
        - 조직적, 책임감 있는 정도
        - 높음: 계획적이고 신중하며 목표 지향적
        - 낮음: 자유분방하고 융통성 있으며 즉흥적

        **4. 정서적 안정성 (Emotional Stability)**
        - 감정 조절 능력, 스트레스 대처 능력
        - 높음: 차분하고 안정적이며 스트레스를 잘 견딤
        - 낮음: 불안하고 감정적이며 스트레스에 민감

        **5. 개방성 (Openness)**
        - 새로운 경험과 아이디어에 대한 개방성
        - 높음: 창의적이고 호기심이 많으며 다양성을 추구
        - 낮음: 전통적이고 실용적이며 익숙한 것을 선호
        """)

    if st.button("새로운 설문 작성"):
        st.session_state.tipi_completed = False
        st.rerun()

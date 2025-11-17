import streamlit as st
import time
import pandas as pd
import random
from datetime import datetime
import os
import asyncio
import io
import gspread
from google.oauth2.service_account import Credentials
from surveys import survey_mfi_screen, survey_phq9_screen, survey_tipi_screen

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
    /* 메인 컨테이너의 상단 패딩 - 충분한 여백 확보 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }

    /* Streamlit 헤더 여백 조정 */
    .stApp > header {
        height: 2rem !important;
    }

    .main {
        background-color: #f5f5f5;
    }

    /* 제목 스타일 및 여백 조정 */
    h1 {
        color: #333;
        text-align: center;
        margin-top: 0 !important;
        margin-bottom: 0.5rem !important;
        padding-top: 0 !important;
    }

    .stButton>button {
        width: 100%;
        background-color: #2196f3;
        color: white;
        border-radius: 8px;
        padding: 12px;
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

    /* 안내문 여백 축소 */
    .instructions {
        font-size: 16px;
        line-height: 1.4;
        color: #555;
        background: white;
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
    }

    /* 타이머 여백 축소 */
    .timer {
        font-size: 22px;
        font-weight: bold;
        color: #2196f3;
        text-align: center;
        padding: 8px;
        background: white;
        border-radius: 8px;
        margin: 5px 0;
    }

    .prompt-text {
        color: #f44336;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
        animation: pulse 1s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }

    /* 진행률 텍스트 여백 축소 */
    .progress-text {
        text-align: center;
        font-size: 14px;
        color: #666;
        margin: 5px 0;
    }

    .question-container {
        background: white;
        padding: 12px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #2196f3;
    }

    /* 자극 컨테이너 높이 및 여백 조정 */
    .stimulus-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 320px;
        margin: 10px 0;
    }

    /* Progress bar 여백 조정 */
    .stProgress > div {
        margin-bottom: 0.5rem !important;
    }

    /* 버튼 그룹 간격 조정 */
    .row-widget.stButton {
        margin-bottom: 0.25rem !important;
    }

    /* 전체 요소 간 간격 축소 */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* 캡션 스타일 (디버그용) */
    .stCaption {
        font-size: 10px !important;
        margin: 2px 0 !important;
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
    "기쁨": {
        "image": [
            "1Zkses874-UuG4A_-__2duE51hep6If1j",
            "1Ont1RcegoaFfrI3219Ikr8cXV6uvglqL",
            "1YDoBo0czkU66D95JgdTOI8wbghLZoAmy",
            "1ZNeCT6BzIkCc9Qlhw0FWDZC_tASDBIh1",
            "1goWcU3wQ5S0xjDzBZV4wVhfYnXUeR9q0",
            "1KScgP_iHlFO5tUwC7QxKsQpFLkvQLr3I",
            "1ACWVr2oSo7N9LQ02kpQrZu4kEed-Us9m",
            "11x_5wwj66ecDUWsnFJiLUaH3sZkAXYFW",
            "1IF5BY2xkpnlQ0wMesj3x78T5g71DQEul",
            "15BaFON-FhGkJO0eUOoik40UScCZTIr9x"
        ],
        "video": [
            "19zOp3h7wL8FT6EoVQ9JGL4x8KxDsy4Kn",
            "1-cJzQBdo2p1FpVx1-x5L4eMBWGWEGfXd",
            "1vYvkcii1mnXXmoAfyDIBLAXY41RUaf4I"
        ],
        "context": [
            "1Un6MX1QS-7kLm0TmF5HudbCkvyztIF2q",
            "13gMPrItCCJcaW8xMrV3kXF0XnCKsBvl_",
            "19F3WwhiXLh6f5m5ucwnrm1SbJp0IuNmr"
        ]
    },
    "분노": {
        "image": [
            "1VyYa-SGDfELBu-19pXRjhZWoTuyyjHFx",
            "1yNk544ZLUVlLGkjGc8Q42QPortVKgcVC",
            "1RTq0IDP6m3_q71VXfoFNDkmkeCBDd1jo",
            "1pbConKsQ5OqEtSESJmb4f77vT-yvcINe",
            "1CsNLvKePRqwbyh8oLCd223B6Ft5GsPBa",
            "1A1kzu7ZPxJ4wAUWkxOLb9SjoFzY1FESn",
            "1YlshSNqtyBhn-sk6_BZlWEwUwno1_9ye",
            "1aYU0vm90-qF9xG0IdS67rpOmMaaTPF1p",
            "1H0y4rd2-EU7_Eeg3NCOJ5L7-GBzifiZ8",
            "1Aiy0is6ZgRPoupamjR5pky92JvqIaM9f"
        ],
        "video": [
            "1bu6w9b_6u24EptxHGBs53fytX1xHHG7t",
            "1T-IDWjNPU73wy97QHJMfd3FhHIo-8mBD",
            "1VceriH84Mqo0UKcuodo4xJLkQZB7SzHf"
        ],
        "context": [
            "1lBHrhcS4kuKvfXBqzRzlUMHcx6K-fiCM",
            "1rruwzoXikyzC3W1vPECqfxvXv5H32Der",
            "1bZEU7n2L5PFBE1CZZYkN_hrA3OIcgxdy"
        ]
    },
    "혐오": {
        "image": [
            "1z7RbUW2oLX3_m9fiyq42Jaq1dVwhhvR_",
            "1SifkybdXOSoMlapNUJXmIqX3YrSXKRB9",
            "1_QWtJUdNYcRCj7WqamFe6-w7jx89cSr7",
            "1BkbZb3Rq6Mn4XOPNSy2Du6N1LvRjy7_M",
            "1T6KZK4DwaSOURIx8qoub0rOZIUv-8Xtv",
            "1qnCsL3HSqcjWaAb8aPdoYUuM2KxmB7gP",
            "1qaJt3mMCUYVLgP7mb76IhbIDfAGBjBlZ",
            "1Zbpt-dC9WBHLQMujcAofEXcFXhW5mYAX",
            "1OJOXwx4Yh6ZAW5zjJLL39v_9CDYEGUAo",
            "17Oju3H446qeuBfl_c-M10e5uTcXwA0qi"
        ],
        "video": [
            "1u4IxhJz-z_OnQTQIJY9GY0Tt4Q_y9J-_",
            "1WxFe5p4seNwUexmUxL0MtI_4zGkCXaz1",
            "1KArVjofwKf6ZrGN6SJqXIIUwetmRgZt_"
        ],
        "context": [
            "13bpNPsD5CyZxLHvaEmzvfFKzUUgys3zn",
            "1BNnyLxErDtoEYGm4jc3EcFypKcqtLmgP",
            "1VF95OjUmRL-8HIRrv4qwBuj-m1xFrc6Z"
        ]
    },
    "중립": {
        "image": [
            "1o3axkrf0tQFYDduYwIHTMxTNcd1oThxJ",
            "1V-VoAiH8b7ZwbNgVCYWLe7MrX0S-cAYw",
            "1NIVdvkHgTK7dsNwPxKvEtuc0migiuFN1",
            "1ZM5UV64L21s7C8vPVWnJzdtkZTmCtbt5",
            "14SX1OHK4ibPDXG4pORRxPCySjFbt3219",
            "1ZvfUS0TsdnHTgQax6g6eOTMoZL6yV4B-",
            "1GVSu2JF2t1qmCgxvRFhFHuPkVa3wO4dc",
            "1BghGYzNdZBOJUBWgVIPi8h1xdAGzp4H1",
            "1541RJRVWZF1S104fAKe7TXJwmV6cylqo",
            "1j1pP8gRHSY-Xs340M-wBW-ApcGInQgoh"
        ],
        "video": [
            "1VO-yaXMD4e6GnpL3a83sxamgwrHbk2lw",
            "1BY8XN0giJoMJrgUMAZLzxeh7vz6aFg7q",
            "1gkvRsNKp4G_oZ4YVZn1z3xBDncJ0EZmW"
        ],
        "context": [
            "1bsPS2bkbq9avGVDP7l-ybF4lnjQMM_VC",
            "1JP3hydA45UGkppggNHWOBqwtS4xUo5-K",
            "11migpkDDR2c71dmx7sNGibGkNfNdLRd3"
        ]
    },
    "슬픔": {
        "image": [
            "118d9zexPwNz_98JxwylMD5m-BG4PiJV3",
            "1d9BUmNdOc-briQA_v3fWNk7cRkPxTGrQ",
            "1eFibJJcj1JliqesA_m0WKJ_Hl5maKXcs",
            "1OX3DpxSdXV2qHgNXwuS1uoWJyaM6ffUP",
            "1c5HvsqUQvl6S7zXuFbq5rDZF7g5f4_LS",
            "1FDcsqOdxtS_zihYyu3ZaOjwGHsjClJu8",
            "1z5oDFI5y-CIhYTo4rGakOdsbDy8T3GM0",
            "1vF7OVXQt1M8YbSVFdNaB8ZnYnwqGay04",
            "1A6-9FUlF9L74-IkSh5OMpLbSlJ0ffZAf",
            "1Hf-3FOQ6ecjoCufqqL1TlW0tw6eJZou_"
        ],
        "video": [
            "1cvo0Thq8sJ4pDcZ1df9ElF9Atg8ZDOI4",
            "1wmT_ujjXyA7OJr6ySJxhABUaidZkjoRP",
            "13HXjWJ5P2qfzYOxbSxcGAIkNLH8vwFFx"
        ],
        "context": [
            "1n4V78lvO3UkAAOvnzy1SHLd9OW3fHtWN",
            "1wXmhubHUG-uPU7JDtRX5-OSHun92-4xj",
            "1i5Z8RMYl_-aCit7o1gYrbrMDi_0Y_U5T"
        ]
    },
    "놀람": {
        "image": [
            "1uuStKLAP86HPSKGJNr3aWAmLxFH51yVU",
            "1grYrpy-ekVnuuh9wERese3TTSW-swF4b",
            "1WD_eW7fKXbeqaUh_QZsWRR10AcoI-lTQ",
            "1UJCp5G7Z3-VgRIjnSFCArRX-v67CGidI",
            "1Nm3gOeDZIf7Lybt5t5EqaqHOXizkI8Cn",
            "1U8WLiGm7KqaoozbiQQef2llR9Acs78WN",
            "1BaO_6KCaaJN4MjIFQcrSzlPeesIBvFqB",
            "1iTmPwv-BX4Tg_5aMtpxDy-TlICYA9nSv",
            "1qxvwW5pdGjjVThGonF-9gnXgnA-sfGW2",
            "1X-_Vdlv3la5zhiqAJIUyjrrJVEGXiXEx"
        ],
        "video": [
            "1blIln92Wo4ehBtjZz_gU1Dq6kHm-j-YM",
            "17_NfYWvbIaY36TotghCWdlzlV2RHtQ7J",
            "1HpnppSmKuhdSRu6mZvEd9hFUVHAuZ_RU"
        ],
        "context": [
            "16yAYsYk69Y0CXm4dnIoWkaKkpJcTH8Z1",
            "1BANdKftx8B3AWcIryoi1qz3k2bBvrJCM",
            "1m8SMesnVzW87-e8Q2Y6ACiWtDzrmIyLl"
        ]
    },
    "공포": {
        "image": [
            "1gJsvNkuG1oYedX7RHAnxqwPa2kEkBoLH",
            "1gDRJLO8r3To2OPpyNHip69zEHa5Cooxv",
            "11VZbGLIkY9bhlakHau0tsOs5Z3SZc9Uv",
            "1qwQBEgfYmh8gnQHQmkNatp_9Mxh25sDT",
            "1uOzTkm_1rqZ75fA-t5K77sBSIAZQBiW_",
            "1_kJa93LQGmuBGd1RRB3hA6x8ctf0H5JV",
            "1Kbn8uxVCFlQylyFUBQcQfAOj5cjRhLsr",
            "1HR_md5KsS34qFjMJRQPlXIXUob5_MAHC",
            "1TA1Lhg2PFpEGNI9Ck4rp-BOPZaM7mHIr",
            "1XArooLwi_83v0deH7QrZ65i9QgKC7scx"
        ],
        "video": [
            "13IINEhnsNpFzMzT55DXuF0jYaT27jFNI",
            "19236LY-w-VuPjY_OkjQSag22C-xC3JTM",
            "18cskG3qZr5xSPCBet2bQBBfHiL0CXD47"
        ],
        "context": [
            "18DWIxQZxSt5nzKJHxkcOU1R9rdpd8kC8",
            "1phlvANn3TVrF6ZNvmGnaocEajzagFzQY",
            "1tZMhmdw92XWnjf4c7EJlNkVFUz-iVb8b"
        ]
    },
    "즐거움": {
        "image": [
            "112PtmXlqefjBItCkDaumBv2WPiRpG0c3",
            "1R73RTEf52kzeLwpIeHcOWi1sUwdAKeKx",
            "1RnlVLC_ayERCD3vtpQs67jFk7AllfdTA",
            "1h_pjV5N3Cz_Q7iV7dcbVlLd2kEBTS7VW",
            "1srSl6cGaYRFFG_xHBVSzAkGVWnRfYu3Z",
            "1MHgWYpyeUtZh9CjuHxtsOFzZ27F03Law",
            "1aBFJgUP1EELhE05y3A2o2_34hAMgbx24",
            "12bjcT6sY_7qy0V8Xf86PwSEikFvqAO2C",
            "1PsGZ7IDjsMGq804W71vprNAK_xZ1u2zE",
            "1kDmUKgtKXmfTFlPSyW9tAyJBFVEGLGaS"
        ],
        "video": [
            "1CI-vh-qVyEQN4SxwXPVo72RjWbJRRt7u",
            "1aR_cMyx7vhzQRnuh37VhNOUCFqV9siBS",
            "1zUDbwYhruSirujaUDHxdw8Je899vsyr6"
        ],
        "context": [
            "15Nl1XNAJobohl7XAnqPrXbbrZuS7cPx2",
            "1C4EslDCeJzf7eToN4rH7NXj9B-XtHpbn",
            "1pZ69s3zzmUxszNZI-zkdJXttKOMIQVfD"
        ]
    },
    "애원하는": {
        "image": [
            "1XZyRLCzAgQGQIiYh-Nih4pogDlttMpF-",
            "1DfX94HaHrlHF2eEQBQ4fGKtAGSmVfwep",
            "1d4aYHfVGglv50lFaTjTdL4-YwRydjk5P",
            "1uSx1RZpSxtlW3yQ6vm__PIWEVDZoNBYZ",
            "1ptytZ902IAf6WjuXv84wN-wnxRzkEhzO",
            "1I0eqVqCdqHBSM4SEqMq7rkJ183ZbQTQl",
            "1KV5RoF6yz6vg8TS4Y9Us2cXSLcGXjhwD",
            "1-NCTLryz3BlR1YyQfizsTn7zbOvRz4hk",
            "1QY4W43mrrd9oOVvdmDg9sf5tZpnokoYz",
            "118VxRXMX6RlYc0FbztRwjutGLa5vDC5P"
        ],
        "video": [
            "1sF1_xsKRgZEFTE0XT67DBvpF-GuxEc0B",
            "1ptxVSYugmzG8HdhGKVVk3Nc67cQPJ_yk",
            "1UB4bjS72Pj7KENpzrP4bQOeTz7JyO-qT"
        ],
        "context": [
            "16WEzsmydI7EagRlCH1rbk_EijfaE-EG5",
            "1oS_dyva010wLvXazSJtTbFCsVMDoQ7ZZ",
            "1Mj_B-sexOu9BsgbJ1E22rkRauCdRs38u"
        ]
    },
    "실망하는": {
        "image": [
            "1o5J9EtZlEx7x_DudTXyvoqeide7kr9It",
            "18rt2MOhyr22GNeEKGtnIKXOZGezp5Gs-",
            "1_Orb3QyflYU-S-wEcL4SXBe6J5yE8QT5",
            "1IcWLYVdQvcC3OXjJtR046d_7Edenufdh",
            "1qBfPXrd_bFZsB_cfzxR_fiYFEjL4lY8R",
            "1Z7KOqJUFUSAcwDxyam_74nDJGOUwmKEm",
            "1CZQ80SzfXBEpf--pYMw35HWKtffR0w1R",
            "1W-w6Hsiyq_V0CJTisrV5giUsWA3B8cFr",
            "15HnH5vMPtqN_ngftcIUh_eaIjT1OyRvF",
            "1jgeaqzD_sl4SiB31AR3MPNPGh5wI0f_5"
        ],
        "video": [
            "1ZVFo3j9TPmj5CerpU8QnZyCQ5qtoOXVb",
            "1mb-XYXdTN5VHCE8T8Lu7zSk7kqOv6aMb",
            "1xiNpA4noSX3ANZq0MS8-gE8qmRyVe-ci"
        ],
        "context": [
            "1Xwq8LvXjCknv_Eaw4mZAaVTji8xuxVPi",
            "1I_IJ46lrkQA5CDQDCEvilXAkOtAYR4M2",
            "1Zup3KYF2EksSlft4V3c8dftW2Q5yEbVP"
        ]
    },
    "공감하는": {
        "image": [
            "1-t3rI9DlAEeVgCHMQb5yJ7_n7F91ivdg",
            "1wKtXR6nFOEfrJhlq1NOLqUGJzvwha92K",
            "1p72c4fExtfdMODmpPKLyLDKNKW-FukaE",
            "1rcaUnk4Q0bq9yz34a5xJpDnkvBWzjqsV",
            "1ex5unpqflQG6FVLtzI-QKIrcC1yZnJfW",
            "1F9kHnb-TCZSeVDSiPB7AEyoffbJNu10i",
            "14lVezFoEuIWx-8Sx1hyJkpR5YS7saYuE",
            "1YUjvkIaiWigPX48rERZVnZ8ZT1ToYrrX",
            "1B01kPv5gXe50jO4LrjQ5rZ1xu79-7nZ-",
            "1d-UiV9Ofm5CcX8KYwvEaAWn5BL7Td8Ph"
        ],
        "video": [
            "1qB56HbOKhF0nHo0lBQ26FNztxZrjLxU0",
            "1ZuLJCcSfiw-ivkFZxbpcq4E9x_EsHEV8",
            "1B6eHMWZBOuVnNbET7eHHMhqNPfDzBxxa"
        ],
        "context": [
            "1N7_WmBWS4Qxjtfj1DsEe6ZQiuXY1Qudu",
            "1i5ptNqPkJSgzhaGfO2D7IzkcBDhwPKIm",
            "17qs3jQ6k92edbtXDPWC___4uefhM9yUd"
        ]
    },
    "충격받은": {
        "image": [
            "1s-EE_rX9LWYDE3Vz9fR9GM6Xns1-2MBt",
            "1e53WPphyj8r_XL2tkrnyPahBt9KstXbu",
            "1Z3_RKc2NlWkGOPh1nJorRop6bZI1CNIZ",
            "1olpcVbblCkoFVNXgA34r5U0-DLarW-5v",
            "1eO1CwuCfqyKFp7iepWu3rO_TScPuqO-3",
            "19wQmc4ZAlw5jEwvT437uxLQtUo0GLJ5D",
            "1JOge-TGUzK7kMLsWCShLBv5OppM-UrBC",
            "1U9tH5jeXJGlMlGotPd7UyngMB-PjE3Lw",
            "19VedfPAfnEyJOwuCK_Vje17NVcSvMaOc",
            "1ojRDyU679bh9cGjNqUOVXUnutskg19-4"
        ],
        "video": [
            "19MienRQ9c55A1t3iQcVorhlRag_O7qou",
            "1mfWTi2e2N6xz6UdZk6V7Gfp8xCR2z5Gj",
            "17J5wxHNbWyhniNAe1XCEFA4MPhXxtaH4"
        ],
        "context": [
            "1zqJMZafmwDx8wbeyeWvuSl2IAdlS3K9R",
            "1KY3os6-iU-Io-Pvl_6E3uOIQN_OMFoTA",
            "1HVhBSU0ZQYHT6LPvHqNcCxim7WOZ3f_K"
        ]
    },
    "질투하는": {
        "image": [
            "1_ExilbNsMPTn4eoD74qXQVJ0XpX56UVW",
            "1bpC3Yl3HEqO2G9-dTr336q9QRmPeUXIO",
            "1j1rxMzshT-g-GY5eDxNwVzt0EIWIzeuN",
            "1w-rS9wei_TgMrHAs-snmmAXHreaG3x5k",
            "1qgBo0pcRXQSRRrWTxZ9e1RPgUzb3vPcj",
            "1h8e94bcJ3gDf0m5OVVXPVAJuUjQEGiQF",
            "1SASFp0cVdAqSdG7U6s_8wKtT5XL192RQ",
            "1CebtnHTKC5O9W-eHeHGtU8_7tDq_b_RC",
            "1guE52RR9Ou6z9ddxCGCEFQaqKEbaCHGC",
            "1ZEJA6erLYsHpANmv4uYi7OU5XhurZQoG"
        ],
        "video": [
            "1_tXYi2spgsygNkstFvWjuUNnyjBf-KDZ",
            "1Ke88fKlLSg7pUFHpJlPCmAeDbWOp1-gv",
            "1_OTyqD4iiPhjH52YHCcX1p1A4N_z3hZY"
        ],
        "context": [
            "176ZUUprceTdptFxL7BUxASWnNZxOj6m3",
            "1B_QST6J_n6QJp9nAhX-Ir2axX6BQc7xI",
            "16yqXbjtk5x0ZOGjGJrbVG_0QdGKzKQVZ"
        ]
    },
    "초조한": {
        "image": [
            "13ZYG8Ugqqv8bi6nPVMwkpE5Vb-I72qWU",
            "1YQhHtoUEUt_bwaOyLYtteDVQXP-Lujpv",
            "1ezdr9Qdk5c9qdBt9DnnCoVJy9TL8cg62",
            "1I4xoX6SG5hLdxPCpb75958jEosR5cHbS",
            "10JYOkFUWYqsQIG5C9w8EUere7oKOZvkb",
            "1fFC2LVmAqsNGZZ_sDkaO1Wv50BU_tbRM",
            "1TnF5N7DGn_rREHYwJjPBjVRY8Wwn91e5",
            "1ZM907vi8rM4fdjEYrL90WhwTUUJEkDSr",
            "1g47aSlgtdkV0urcB26hKWHTiCpJUEJr1",
            "1kYbpdX5EO0FEnMEb0qa_5sOvXMMrwlD3"
        ],
        "video": [
            "1aB1t2-GhgII0MCxvNCrk9UU88gN8iWKH",
            "1oetF9L5A4JT9X0RQn6nFxNuktBYEknn8",
            "1afiVx8rQWgpDNgoS1ldNxWK2MJfqVfl3"
        ],
        "context": [
            "1ekLwSmsQtA5KG9UKRz2cbtujMHCB8cAo",
            "1O8HesklCKbaDAYpXQqXMFpO3Z_ZYYunp",
            "1yismmj_kOmQZT9iZaJk3KAeLHjxyUNOK"
        ]
    },
    "안심하는": {
        "image": [
            "1yg27o56U2rkaQTVU2IFnfAnQW2H-ku9t",
            "16qPclrKreyt1L4r2Ck8vT3qvnxhAzlDN",
            "13N0yjQGJr5wwN3QmX1wKJYVqGUZoO7lP",
            "1wsR1xqh19-iJTvSbo5B8ROryI6xtcW5i",
            "1lEffr6JC6DMebiNbPmUp3mUDBT6lNVPT",
            "1hilWJp8G6tKE-qgonXv8Kao6dEsnzE8E",
            "142R2RjS2-unId4ykeTwd0XWQRfVB0xAJ",
            "1gbcS7A2KtK6wu9l1F8NetpRfUvy0KrdS",
            "14fwRHnCPjpoOt4rN3lcpXCmEVTBW20hz",
            "1BSafDzbcN6DnNm7T2tDzg_2j_T_nm-nc"
        ],
        "video": [
            "1hnHQ89lAtOT4SFpxOTKj0uCjbsLmdzPo",
            "1cGiktioy0eK_w8TxsX7o9BRmsUvo0Ra2",
            "1R5DlcpcwduZdZvzR-6AETDtu434wMAAd"
        ],
        "context": [
            "1Vx73kumEQGe3Jf5Oy4fAiIt-C0XfEueV",
            "1bgyNdZ3kwt8hhhdKcXGMM7DBLwCBHyyH",
            "1ITIR0NPSE_PWxm17BEqHFRLPueNoYHUf"
        ]
    },
    "우울한": {
        "image": [
            "1IZdAViusYSeYmeAtNPJ3DbcQFZ0YMbH4",
            "19F_3j62_aczUQ-yTJGNvVbxYvnAKVKz6",
            "1zWi0YwwMX796J0bC_cEExHSyQZ1oXLyg",
            "14ckBMnMBPA0T2U4mVBSQJcjW1qi4KaVy",
            "1WDyxChA9NNW70ES9ii9iACfRGnYlB_9V",
            "1MRbyZy2usSv78WKuxgQef0bdoafYdDad",
            "1K-3eLg4eH071txQrCddN-YcgqxO_gd34",
            "1uloddC8R8TugxFzbk8IHZSPW37ubFLaI",
            "16M6BtEQ3IXO2XM5SnlOQJduO2dbCx5vt",
            "1i0kx5XMfASnzdmbKaC-gu4Z1BEzUsY5h"
        ],
        "video": [
            "17LWzO6qhibDrqqUsoEfBgV5NLcgzlKU9",
            "1ySuABq-5OtFB5rLKSRGanDAQ208uypzR",
            "1EwlXwkdc1ynCdhkVzoVXOTbvLNcmuRv0"
        ],
        "context": [
            "1CSs023_TiIJbeq0mqlUXgHkhIAPWIba4",
            "1FN0cM2HGRDmJIEM3y9aqHUX1DLDuPHtB",
            "1lznvCIxXFXlmFZ6Tz1ViNKetvgV3nu-v"
        ]
    },
    "불안한": {
        "image": [
            "1il7LdJBVRe9Sa9CYpewjO6LKVwLoVaMV",
            "1QqhZdNLhxFDFyT7P0TjjqPBNahZpnj63",
            "1_IBHaYmpNSZ1C5MYCQL84V2AKoueFnL_",
            "1SEQlAciBoKMbCs4hunRIadCQZQMUviQY",
            "1_c24vmQGVKtM0OsLf0Bw7gCpl7nt-nxI",
            "1tz52ybD99jSCLxUNS67Kll9SPiTj667b",
            "1tB4ve5U1ibYnNF00nnAB2PJjovm1ABCr",
            "17VWt9qM5wrYWHoADhZBQ00TeD3dUDwUP",
            "1D2bWJddsteX7X7HXq7gc1jIrA896N6tW",
            "19oEpwI-wcxt8tf0V_-9-RqlhvzvNTv1Q"
        ],
        "video": [
            "1v_X718rja0aeuqeIFFl3NUaDzBBoOap0",
            "1ZiLe2ncqEvG5liskt9lOi2q36Vzw-nt2",
            "1YrY6b0qcOAuKHe6TPWf2r-kDDAJbfO1S"
        ],
        "context": [
            "1q8uKAnUCy4KFdoYu6BslsZi6kAZYDO91",
            "1iJ-G1uGI11lx47a288SiOtFMKbw2hclE",
            "1gFK7k0hWGAGCkj3ncgbOgazx1yvlVIfZ"
        ]
    },
    "사랑하는": {
        "image": [
            "1naIhOwztDkUgGj6vf2nipy6TK4m77Ynx",
            "1cgTEabUmY6roPmTxAlC8MCkzgIRdIplQ",
            "1Bqwoi_2dJeEXqvh4-2mj8P6qRjnU4aex",
            "1NiMEABTc9kSRZoRE0R7_H_o3v3XEZJ7p",
            "1XeL6exS3JRje6uEjISIpORL7jLC3tTJl",
            "1DFIbXy5y3VdAzhlIK4P3chBp_45Zjv-d",
            "14uGwp4vtrVqDkO_UGo6p-z6yod0dAISL",
            "1ummVZT6er38PG9THNSS1jFF4e34LWgwp",
            "1a7Fu-bqMcRis6J4mpAuGqcASbJrUyw1a",
            "1LOLns7rS_8x8TRQLICYx-H15UyHKLAAZ"
        ],
        "video": [
            "16CKJepvy43eibCQXBZWZumkBf9ioJT1D",
            "14cmVML61JJjAN8NJFWBJLzR8ryoeuxXG",
            "1n1L-ErSH9jSz6hrDyWoXW9o-JulbLckM"
        ],
        "context": [
            "1DOrMddv00him9-FVESkO9bIRFjY--J6l",
            "1yhSlBz10mLdT1yQvhZkqXYG6wDLrfXR8",
            "1StJkHoc_N2phRmEeLgQ9mgvxO3djLD_9"
        ]
    },
    "쌀쌀맞음": {
        "image": [
            "19gBo_xGykoXp2Jqdcv5BhyL8owgz9naI",
            "1-rt3OKF_Ap1_uY01DeksIrqpMj-ud4ki",
            "1HHHF7u-Fe6aKIBxS03t5KeVbhXWi1nct",
            "1PJQRUvWikyUtN-SMC5dXArs8KaKB_Ui5",
            "1elrZmvp_wTbNHQozOxTbH51g5n6Zm51C",
            "1WVQbbQJXEZEttk-tkA8lSGSejap7iCY9",
            "1sY0mUrbfrLpP_jwi4DFHYl_Uv3BzXxfS",
            "1VHJUJXa4uejwDlvOkWvp92BfI5TJnA5n",
            "1-mw9OLenR-WM9PH12W0e6I122EgsrojS",
            "1St2jmjluZTgPPBfixRdaQc8yxfquysZI"
        ],
        "video": [
            "17LMxnM0vluzur-agj1SHBECJOVtm-cRW",
            "1ArjTUEJk0BXEIha5YwMuXvif64glo1eO",
            "1pujHvlECpq8DZd5mch2NgW3VGVOr_6_G"
        ],
        "context": [
            "1y0q1Uo5maCa2V67hVcrtfkBMVYadJVnJ",
            "1w4ZzGWfTwHCtxr2ZzmjyZtv2oIbyipjx",
            "1CvE1iVkzaCA3NXSWM5XyfpMAZgs5ZRKE"
        ]
    },
    "활기찬": {
        "image": [
            "16-fbchsgRmMZ5uwwXof3ktoExzz5wbon",
            "1B9yhZT491WgYv-2Dp-I0h8c0eaTaG1iL",
            "15pvToQp3xGfw-kRw4Hxk_L6jKxhJhrwI",
            "1NCTwoX__zMIVz5nCJ7zQ3-IrGq2KRCVa",
            "1OJE3tua618HWGSkPrDiwWPVWELrkLUe_",
            "1R7SpK_A0AJR8Gzym5wbqNLIJOO6QzTrK",
            "1vs0gS8Erroi483aAIPYSWS1KFv8cTDhk",
            "1i_Hyq_r4mJagxIJ2aS7Qeoq13REwS_SZ",
            "1zFiqs9VVg3lgTr0aarFESYgnUXj3EvvC",
            "1tcOgMNrZueH6AGsbpey1aXV1rfYRF0TM"
        ],
        "video": [
            "1giiHwHtY7cHNElkZjfKLpT5k8xBO5UCt",
            "1n-zl3IH14aKP53JtXef8fHHPhnDJLcG1",
            "1SKRDUaBl0ynhQWubmoHLMJgA6ZU-2Gjh"
        ],
        "context": [
            "1fNDAvyvJGHZQkrsVV1jXR0m172Pa5D3N",
            "1EG4n336OcAaMpvYXz3aS0APf1yFLsnC8",
            "1JLNnQM83xuoIWPkjdkqfMYBstFEbc8Gk"
        ]
    },
    "쑥스러운": {
        "image": [
            "1SkJb3QC-e9K3g-yY7Ukkh5sYZ9bdHzw_",
            "1C7YCCTaWnxJ1gqhaRElvqT7mnGgyR1Mq",
            "14yVqI6_2CJbgOC20BPvuvxlEKKQ5jnrg",
            "1utfacXdr8nttHC7EDFULpTizVKfIwirY",
            "1B2uVtlme7p3kT64ir0KdZDJ0TMX0ScBz",
            "1WUywCYwXchesPthyAnAj9dKbHkUzyYsO",
            "1b0qS-k31i6oXbmNOWHPtJXwZ0_cdzEIa",
            "18sx-tfR3G-T2HsZjGH4pKcWzDgRs4nDV",
            "1gJmPdYbYVQlBuUEut3UflVfbP53niDOt",
            "1oJsubgrET6VmipFoD68pG1g8OxUAq6eN"
        ],
        "video": [
            "1LMcHIAl6vpI6JKAVOwgxKVMFQZYlzCel",
            "1-QdftnJuPGDBmHC6or7Jt68ZlgMQK0d2",
            "1iCw2Jvdodhm38WGLPiLpfPCxGFzigBIK"
        ],
        "context": [
            "1IkJZN7WKxHV-l-wArbp1JiJ7tsqXtO59",
            "1PiCiF_6GBmQyUeOzBG2khPS8lbKwvwVf",
            "1WlHszji6fJPx7Wb-lgTk6EL1u9qeonub"
        ]
    },
    "진지한": {
        "image": [
            "1tr5J6hE9DRMbQ93cPpE4js0wFi4snFJU",
            "1kYgYWsjJAQtkpRBQ5eJRxOStuio73A6s",
            "187bgu-x7EyKRYkHLQny0-us6801nN3nl",
            "1UTapIHXU13yCpPVC0feHkUNJnP7vEJ1y",
            "1sJf4CKvNgKWEEkSeub5AFW6rk2LCxGh8",
            "1fZw_mwZtdwofNaFR33Q3UJXX4SThWN_j",
            "1U79pceKbHt3mp07gBu8DXg4V30XK_nxR",
            "1gMNQs3RCvdqh99HriSJQoFogoSAf39cO",
            "1s9u3xNZRvZUgAd3Es162GzQO6sK6RWRQ",
            "1nfjY6PrG5tvsZqn9TO6hp4fTmhhLufz5"
        ],
        "video": [
            "1s_qIS4cF8NKiNABdCv3zxkIeKtvGIqej",
            "1aw0DXm33gZeErNXEoAmgoSYPqsAZGA98",
            "1bwUhHC0whS6Xdzo84dRdcLJntI7EOUyu"
        ],
        "context": [
            "1HyO3opc2DYrytm7wzGvCmvB5OmqX7wC4",
            "1gNMeYlH1MbvTqmayMt3Rx45dC59Adf5x",
            "1Dr2NiaH0T0zCIMvAcWTgLr1fhGkZ9sgl"
        ]
    },
    "창피한": {
        "image": [
            "1GwZhN-nJb47OjyFyGsLoewhHxb9BGmje",
            "16lbyXTnCKFARAo_OjYatYE50Vo0OUuTl",
            "1_12mibfwd6qxiH5_SL3KlXIASxn2YfI_",
            "1SOt0rM76325z2YrXssF3rl6evS-R-Hgw",
            "1z5rViWNi7LGxB3BB5NhVYDBmJH6-MCyg",
            "1Ago57f68Iw2arfAM8kjyxBQ2w0RPeOFy",
            "1xbQJBjzafB4vb_VnRt53dQVuhN0vjUaT",
            "19KHxViCxW_2XDqkXzgzWkv1aGBMTxgUv",
            "1DMoGGe1vB_9t_mg6sIQBQImngKF8889r",
            "1nW_k0t70RKlajYCKm6BQ_cnd8NfA_rvX"
        ],
        "video": [
            "1eo7gOw2w7Kj7JbsIPowe0Fb0sQQ4MbD8",
            "1yd6k7HyvZhemREhUGI3b_tppx0EZU7RW",
            "1GagY1HfSdAESKja9gCmUbdkaMlYlzD-F"
        ],
        "context": [
            "1vxFS3kflSb7HuAcnhYJCGLkGc4YbozBy",
            "1Kbj45kw9uZBfRmz-R6Szexg1yzsKFq8P",
            "1ZddCNLfH88GaJ31v4HlfTs9UhHyUq2GF"
        ]
    }
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
    if 'stimulus_shown_time' not in st.session_state:
        st.session_state.stimulus_shown_time = None
    if 'current_stimulus_file' not in st.session_state:
        st.session_state.current_stimulus_file = None
    if 'current_stimulus_id' not in st.session_state:
        st.session_state.current_stimulus_id = None
    if 'current_choices_list' not in st.session_state:
        st.session_state.current_choices_list = []
    if 'stimulus_timestamp' not in st.session_state:
        st.session_state.stimulus_timestamp = None

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
    해당 감정의 파일 ID 목록에서 랜덤하게 파일 하나를 선택

    Returns:
        파일 정보 딕셔너리 {"id": "...", "url": "..."}
        또는 None
    """
    if emotion not in MEDIA_FILES:
        return None

    file_ids = MEDIA_FILES[emotion].get(media_type, [])
    if not file_ids:
        return None

    # 랜덤으로 파일 ID 1개 선택
    file_id = random.choice(file_ids)

    # 직접 URL 생성 (API 호출 불필요)
    if media_type == 'video':
        url = f"https://drive.google.com/file/d/{file_id}/preview"
    else:  # image or context
        # 여러 URL 형식 시도 (Google Drive 직접 링크)
        url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
        # 대체 URL들
        alt_urls = [
            f"https://drive.google.com/uc?export=view&id={file_id}",
            f"https://lh3.googleusercontent.com/d/{file_id}",
            f"https://drive.google.com/uc?id={file_id}"
        ]

    return {
        'id': file_id,
        'url': url,
        'alt_urls': alt_urls if media_type != 'video' else [],
        'mimeType': 'video/mp4' if media_type == 'video' else 'image/jpeg'
    }

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

# 데이터 변환 및 점수 계산 함수
def prepare_final_dataframe():
    """
    모든 데이터를 엑셀 양식에 맞게 변환하여 하나의 DataFrame 행으로 만듦
    """
    # 결과를 저장할 딕셔너리
    result = {}

    # A. 참가자 정보
    participant_info = st.session_state.participant_info
    result['이름'] = participant_info.get('name', '')
    result['성별'] = participant_info.get('gender', '')
    result['생년월일'] = participant_info.get('birthdate', '')
    result['DRC코드'] = participant_info.get('drc_code', '')
    result['학번'] = participant_info.get('student_id', '')
    result['참가완료시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # B. 설문 점수 계산
    if 'survey_responses' in st.session_state:
        survey_data = st.session_state.survey_responses

        # MFI 점수 계산 (12문항)
        mfi_items = []
        for i in range(1, 13):
            key = f'MFI_Q{i}'
            if key in survey_data:
                value = survey_data[key]
                # 역문항 처리: 1, 3, 6, 7, 9번
                if i in [1, 3, 6, 7, 9]:
                    value = 6 - value
                mfi_items.append(value)

        if len(mfi_items) == 12:
            # MFI 신체 총합 (1-6번)
            result['MFI 신체_총합'] = sum(mfi_items[0:6])
            # MFI 정신 총합 (7-12번)
            result['MFI 정신_총합'] = sum(mfi_items[6:12])
            # MFI 총합
            result['MFI 총합'] = result['MFI 신체_총합'] + result['MFI 정신_총합']

        # PHQ-9 점수 계산 (9문항 단순 합계)
        phq9_total = 0
        for i in range(1, 10):
            key = f'PHQ9_Q{i}'
            if key in survey_data:
                phq9_total += survey_data[key]
        result['PHQ-9 총합'] = phq9_total

        # TIPI 점수 계산 (10문항)
        tipi_items = []
        for i in range(1, 11):
            key = f'TIPI_Q{i}'
            if key in survey_data:
                value = survey_data[key]
                # 역문항 처리: 2, 4, 6, 8, 10번
                if i in [2, 4, 6, 8, 10]:
                    value = 8 - value
                tipi_items.append(value)

        if len(tipi_items) == 10:
            # 각 성격 특성 점수 계산 (원본과 역문항의 평균)
            result['Extraversion 점수'] = (survey_data.get('TIPI_Q1', 0) + (8 - survey_data.get('TIPI_Q6', 0))) / 2
            result['Agreeableness 점수'] = ((8 - survey_data.get('TIPI_Q2', 0)) + survey_data.get('TIPI_Q7', 0)) / 2
            result['Conscientiousness 점수'] = (survey_data.get('TIPI_Q3', 0) + (8 - survey_data.get('TIPI_Q8', 0))) / 2
            result['Emotional Stability 점수'] = ((8 - survey_data.get('TIPI_Q4', 0)) + survey_data.get('TIPI_Q9', 0)) / 2
            result['Openness to Experience 점수'] = (survey_data.get('TIPI_Q5', 0) + (8 - survey_data.get('TIPI_Q10', 0))) / 2

    # C. 실험 데이터 변환 (Wide Format)
    if 'responses' in st.session_state:
        # 연습 제외한 본 실험 응답만 필터링
        main_responses = [r for r in st.session_state.responses if not r.get('is_practice', False)]

        # 실험 유형별로 분류
        exp1_responses = [r for r in main_responses if r['experiment_type'] == 1]
        exp2_responses = [r for r in main_responses if r['experiment_type'] == 2]
        exp3_responses = [r for r in main_responses if r['experiment_type'] == 3]

        # 각 실험 유형별로 처리
        for exp_type, responses in [(1, exp1_responses), (2, exp2_responses), (3, exp3_responses)]:
            for idx, response in enumerate(responses, 1):
                prefix = f"{exp_type}-{idx}"

                # 제시자극파일명
                result[f"{prefix} 제시자극파일명"] = response.get('stimulus_id', '')

                # 제시자극정서명
                result[f"{prefix} 제시자극정서명"] = response.get('correct_emotion', '')

                # 선지정서명 (선택지 목록)
                choices = response.get('choices', '')
                if isinstance(choices, list):
                    result[f"{prefix} 선지정서명"] = ', '.join(choices)
                else:
                    result[f"{prefix} 선지정서명"] = choices

                # 참가자응답
                result[f"{prefix} 참가자응답"] = response.get('selected_emotion', '')

                # 정답여부 (1 또는 0)
                result[f"{prefix} 정답여부"] = 1 if response.get('is_correct', False) else 0

                # 반응시간(ms)
                result[f"{prefix} 반응시간(ms)"] = response.get('reaction_time_ms', 0)

                # 자극제시시점
                stimulus_ts = response.get('stimulus_timestamp')
                if stimulus_ts:
                    result[f"{prefix} 자극제시시점"] = datetime.fromtimestamp(stimulus_ts / 1000).strftime('%Y-%m-%d-%H:%M:%S')
                else:
                    result[f"{prefix} 자극제시시점"] = ''

                # 응답시점
                response_ts = response.get('response_timestamp')
                if response_ts:
                    result[f"{prefix} 응답시점"] = datetime.fromtimestamp(response_ts / 1000).strftime('%Y-%m-%d-%H:%M:%S')
                else:
                    result[f"{prefix} 응답시점"] = ''

    # DataFrame 생성 (한 행만)
    df = pd.DataFrame([result])
    return df

# Google Sheets 업로드 함수
def upload_to_gsheet(df):
    """
    DataFrame을 Google Sheets에 업로드
    """
    try:
        # Streamlit secrets에서 서비스 계정 정보 가져오기
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        # gspread 클라이언트 생성
        gc = gspread.authorize(credentials)

        # 스프레드시트 열기 (없으면 생성)
        TARGET_SPREADSHEET_NAME = "감정인식실험_결과"

        try:
            sh = gc.open(TARGET_SPREADSHEET_NAME)
        except gspread.exceptions.SpreadsheetNotFound:
            # 스프레드시트가 없으면 생성
            sh = gc.create(TARGET_SPREADSHEET_NAME)
            # 첫 번째 워크시트 가져오기
            worksheet = sh.get_worksheet(0)
            # 헤더 추가
            worksheet.append_row(df.columns.tolist())

        # 워크시트 가져오기
        worksheet = sh.get_worksheet(0)

        # 첫 번째 행이 비어있으면 헤더 추가
        if not worksheet.row_values(1):
            worksheet.append_row(df.columns.tolist())

        # 데이터 추가 (리스트로 변환)
        row_data = df.values.tolist()[0]
        # NaN 값을 빈 문자열로 변환
        row_data = [str(val) if pd.notna(val) else '' for val in row_data]
        worksheet.append_row(row_data)

        return True, None

    except Exception as e:
        return False, str(e)

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

    # 표준 연습 안내 문구
    st.markdown('<div class="instructions">다음의 예시를 통해 연습을 해 봅시다. 다음 화면을 주의 깊게 관찰하고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.</div>', unsafe_allow_html=True)

    if st.button("연습 시작", use_container_width=True):
        # 연습용 감정 선택
        practice_emotion = random.choice(ALL_EMOTIONS)
        st.session_state.current_emotion = practice_emotion
        st.session_state.current_choices = generate_choices(practice_emotion)

        # 미디어 타입 결정 및 파일 미리 선택
        exp_type = st.session_state.experiment_type
        if exp_type == 1:
            media_type = 'image'
        elif exp_type == 2:
            media_type = 'video'
        else:  # exp_type == 3
            media_type = 'context'

        # 자극 파일을 미리 선택하여 저장
        stimulus_file = get_media_file(practice_emotion, media_type)
        st.session_state.current_stimulus_file = stimulus_file

        # 메타데이터 저장
        if stimulus_file:
            st.session_state.current_stimulus_id = stimulus_file.get('id', None)
        else:
            st.session_state.current_stimulus_id = None

        st.session_state.current_choices_list = st.session_state.current_choices
        st.session_state.stimulus_timestamp = int(time.time() * 1000)  # 밀리초 단위

        st.session_state.is_practice = True
        st.session_state.trial_start_time = time.time()
        st.session_state.stimulus_shown_time = time.time()
        st.session_state.show_stimulus = True
        st.session_state.stage = 'experiment'
        st.rerun()

# 4. 실험 화면
def experiment_screen():
    emotion = st.session_state.current_emotion
    choices = st.session_state.current_choices
    is_practice = st.session_state.is_practice

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

    # 안내문 (모든 실험 타입에 동일한 표준 문구)
    if not is_practice:
        st.markdown('<div class="instructions">다음 화면을 주의 깊게 관찰하고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.</div>', unsafe_allow_html=True)

    # 자극과 선택지를 동일한 위치에서 교체하기 위한 단일 컨테이너
    interaction_placeholder = st.empty()

    # 자극 제시 (5초간)
    if st.session_state.show_stimulus and stimulus_elapsed < 5:
        with interaction_placeholder.container():
            # 저장된 자극 파일 가져오기 (더 이상 새로 선택하지 않음)
            file_info = st.session_state.current_stimulus_file

            st.markdown('<div class="stimulus-container">', unsafe_allow_html=True)

            if file_info and 'url' in file_info:
                # 실제 미디어 표시
                mime_type = file_info.get('mimeType', '')
                file_url = file_info['url']

                # 디버그: 파일 ID와 URL 표시 (개발 중에만)
                if st.session_state.skip_enabled:  # 테스트 계정일 때만 표시
                    st.caption(f"파일 ID: {file_info.get('id', 'Unknown')}")
                    st.caption(f"URL: {file_url}")

                if mime_type.startswith('image/'):
                    # 이미지 표시 (여러 URL 형식 시도)
                    alt_urls = file_info.get('alt_urls', [])
                    onerror_chain = ""
                    for i, alt_url in enumerate(alt_urls):
                        if i == len(alt_urls) - 1:
                            # 마지막 대체 URL - 실패 시 placeholder 표시
                            onerror_chain += f"this.onerror=function(){{this.src='https://via.placeholder.com/480x480?text=Image+Load+Failed';}}; this.src='{alt_url}';"
                        else:
                            # 중간 대체 URL들
                            onerror_chain += f"this.src='{alt_url}';"

                    st.markdown(f'''
                        <div style="text-align: center;">
                            <img src="{file_url}" style="max-width: 100%; height: auto; max-height: 480px;"
                                 onerror="{onerror_chain}">
                        </div>
                    ''', unsafe_allow_html=True)
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
                st.warning(f"미디어를 찾을 수 없습니다: {emotion}")
                st.info("Google Drive API 키가 설정되지 않았거나, 폴더에 파일이 없을 수 있습니다.")

            st.markdown('</div>', unsafe_allow_html=True)

        # 자동 리프레시 (더 빠른 업데이트를 위해 0.1초로 단축)
        time.sleep(0.1)
        st.rerun()

    # 5초 후 자극 숨기기
    elif st.session_state.show_stimulus and stimulus_elapsed >= 5:
        st.session_state.show_stimulus = False
        st.rerun()

    # 선택지 표시 (자극이 사라진 후에만, 동일한 위치에)
    elif not st.session_state.show_stimulus:
        with interaction_placeholder.container():
            # stimulus-container와 동일한 높이 유지를 위한 컨테이너
            st.markdown('<div class="stimulus-container">', unsafe_allow_html=True)

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

            st.markdown('</div>', unsafe_allow_html=True)

    # 10초 후 "빠르게 응답해 주세요" 프롬프트 표시 (자극 5초 + 응답 5초 경과 시)
    if not st.session_state.show_stimulus and elapsed >= 10:
        st.markdown('<div class="prompt-text">⚡ 빠르게 응답해 주세요</div>', unsafe_allow_html=True)

    # 15초 후 자동 넘어가기 (자극 5초 + 응답 10초)
    if elapsed >= 15:
        handle_choice(None, emotion, is_practice)
        return

    # 지속적인 화면 갱신을 위한 리런 루프 (타이머 업데이트)
    time.sleep(0.1)
    st.rerun()

# 선택 처리
def handle_choice(selected_emotion, correct_emotion, is_practice):
    reaction_time = time.time() - st.session_state.trial_start_time
    is_correct = (selected_emotion == correct_emotion) if selected_emotion else False
    response_timestamp = int(time.time() * 1000)  # 현재 시간 (밀리초)

    # 응답 기록
    response_data = {
        'trial_number': st.session_state.current_trial + 1,
        'experiment_type': st.session_state.experiment_type,
        'stimulus_id': st.session_state.current_stimulus_id,
        'correct_emotion': correct_emotion,
        'choices': ', '.join(st.session_state.current_choices_list) if st.session_state.current_choices_list else '',
        'selected_emotion': selected_emotion if selected_emotion else 'no_response',
        'is_correct': is_correct,
        'reaction_time': reaction_time,
        'reaction_time_ms': int(reaction_time * 1000),  # 밀리초 단위 반응 시간
        'stimulus_timestamp': st.session_state.stimulus_timestamp,
        'response_timestamp': response_timestamp,
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
    response_timestamp = int(time.time() * 1000)  # 현재 시간 (밀리초)

    response_data = {
        'trial_number': st.session_state.current_trial + 1,
        'experiment_type': st.session_state.experiment_type,
        'stimulus_id': st.session_state.current_stimulus_id,
        'correct_emotion': correct_emotion,
        'choices': ', '.join(st.session_state.current_choices_list) if st.session_state.current_choices_list else '',
        'selected_emotion': 'skipped',
        'is_correct': False,
        'reaction_time': reaction_time,
        'reaction_time_ms': int(reaction_time * 1000),  # 밀리초 단위 반응 시간
        'stimulus_timestamp': st.session_state.stimulus_timestamp,
        'response_timestamp': response_timestamp,
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

    # 미디어 타입 결정 및 파일 미리 선택
    exp_type = st.session_state.experiment_type
    if exp_type == 1:
        media_type = 'image'
    elif exp_type == 2:
        media_type = 'video'
    else:  # exp_type == 3
        media_type = 'context'

    # 자극 파일을 미리 선택하여 저장
    stimulus_file = get_media_file(emotion, media_type)
    st.session_state.current_stimulus_file = stimulus_file

    # 메타데이터 저장
    if stimulus_file:
        st.session_state.current_stimulus_id = stimulus_file.get('id', None)
    else:
        st.session_state.current_stimulus_id = None

    st.session_state.current_choices_list = st.session_state.current_choices
    st.session_state.stimulus_timestamp = int(time.time() * 1000)  # 밀리초 단위

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

        # 미디어 타입 결정 및 파일 미리 선택
        exp_type = st.session_state.experiment_type
        if exp_type == 1:
            media_type = 'image'
        elif exp_type == 2:
            media_type = 'video'
        else:  # exp_type == 3
            media_type = 'context'

        # 자극 파일을 미리 선택하여 저장
        stimulus_file = get_media_file(emotion, media_type)
        st.session_state.current_stimulus_file = stimulus_file

        # 메타데이터 저장
        if stimulus_file:
            st.session_state.current_stimulus_id = stimulus_file.get('id', None)
        else:
            st.session_state.current_stimulus_id = None

        st.session_state.current_choices_list = st.session_state.current_choices
        st.session_state.stimulus_timestamp = int(time.time() * 1000)  # 밀리초 단위

        st.session_state.trial_start_time = time.time()
        st.session_state.stimulus_shown_time = time.time()
        st.session_state.show_stimulus = True
        st.session_state.stage = 'experiment'
        st.rerun()

# 7. 휴식 화면

# 실험 유형 간 30초 휴식 화면
def rest_between_exp_screen():
    # 화면 클리어를 위한 컨테이너
    st.empty()

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
    # 화면 클리어를 위한 컨테이너
    st.empty()

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
다음 화면을 주의 깊게 관찰하고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요.""",
        3: """두 번째 실험이 완료되었습니다.

이제 마지막 실험을 시작합니다.
다음 화면을 주의 깊게 관찰하고, 얼굴 표정에 가장 적합한 감정 단어를 선택해 주세요."""
    }

    st.title(titles[exp_type])

    st.markdown(f'<div class="instructions" style="white-space: pre-line; font-size: 20px;">{texts[exp_type]}</div>', unsafe_allow_html=True)

    if st.button("다음 실험 시작", use_container_width=True):
        st.session_state.stage = 'practice_intro'
        st.rerun()

# 9. 완료 화면
def completion_screen():
    st.title("실험 완료")

    st.markdown('<div class="instructions">실험이 완료되었습니다. 데이터를 처리 중입니다...</div>', unsafe_allow_html=True)

    # 데이터를 엑셀 양식에 맞게 변환
    try:
        final_df = prepare_final_dataframe()
        st.success("✅ 데이터 변환 완료")

        # Google Sheets에 자동 저장 시도
        if 'gcp_service_account' in st.secrets:
            with st.spinner('Google Sheets에 데이터를 저장하는 중...'):
                success, error_msg = upload_to_gsheet(final_df)

            if success:
                st.success("✅ Google Sheets에 자동 저장 완료!")
            else:
                st.error(f"⚠️ Google Sheets 저장 실패: {error_msg}")
                st.info("아래에서 수동으로 다운로드할 수 있습니다.")
        else:
            st.warning("⚠️ Google Sheets 연동 설정이 없어 수동 다운로드만 가능합니다.")

        st.markdown("---")

        # 엑셀 파일로 다운로드 버튼
        col1, col2 = st.columns(2)

        with col1:
            # 엑셀 파일 생성
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                final_df.to_excel(writer, sheet_name='실험결과', index=False)

            excel_buffer.seek(0)

            # 다운로드 버튼
            student_id = st.session_state.participant_info.get('student_id', 'unknown')
            excel_filename = f"결과_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

            st.download_button(
                label="📥 엑셀 파일 다운로드",
                data=excel_buffer,
                file_name=excel_filename,
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                use_container_width=True
            )

        with col2:
            # 기존 CSV 다운로드도 유지
            filename = save_response_data()
            if filename:
                try:
                    with open(filename, 'rb') as f:
                        st.download_button(
                            label="📄 CSV 파일 다운로드 (원본)",
                            data=f,
                            file_name=os.path.basename(filename),
                            mime='text/csv',
                            use_container_width=True
                        )
                except:
                    pass

    except Exception as e:
        st.error(f"데이터 처리 중 오류가 발생했습니다: {str(e)}")
        st.info("관리자에게 문의해 주세요.")

        # 에러가 나도 기본 CSV는 저장
        filename = save_response_data()
        if filename:
            st.success(f"기본 데이터는 저장되었습니다: {filename}")

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

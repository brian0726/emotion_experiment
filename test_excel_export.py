"""
Test script to verify Excel export functionality
"""

import pandas as pd
from datetime import datetime
import json

# Sample session state data
sample_participant = {
    'name': '홍길동',
    'gender': '남',
    'birthdate': '2000-01-01',
    'drc_code': '12345',
    'student_id': '2024123456'
}

# Sample survey responses
sample_survey = {
    # MFI (12 items)
    'MFI_Q1': 3, 'MFI_Q2': 4, 'MFI_Q3': 2, 'MFI_Q4': 5,
    'MFI_Q5': 3, 'MFI_Q6': 4, 'MFI_Q7': 2, 'MFI_Q8': 3,
    'MFI_Q9': 4, 'MFI_Q10': 3, 'MFI_Q11': 2, 'MFI_Q12': 4,

    # PHQ-9 (9 items)
    'PHQ9_Q1': 0, 'PHQ9_Q2': 1, 'PHQ9_Q3': 0, 'PHQ9_Q4': 2,
    'PHQ9_Q5': 1, 'PHQ9_Q6': 0, 'PHQ9_Q7': 1, 'PHQ9_Q8': 0,
    'PHQ9_Q9': 1,

    # TIPI (10 items)
    'TIPI_Q1': 5, 'TIPI_Q2': 3, 'TIPI_Q3': 6, 'TIPI_Q4': 4,
    'TIPI_Q5': 5, 'TIPI_Q6': 3, 'TIPI_Q7': 6, 'TIPI_Q8': 2,
    'TIPI_Q9': 5, 'TIPI_Q10': 3
}

# Sample experiment responses
sample_responses = [
    {
        'trial_number': 1,
        'experiment_type': 1,
        'stimulus_id': 'test_file_id_1',
        'correct_emotion': '기쁨',
        'choices': '기쁨, 슬픔, 화남, 놀람, 공포, 혐오, 중립',
        'selected_emotion': '기쁨',
        'is_correct': True,
        'reaction_time': 2.5,
        'reaction_time_ms': 2500,
        'stimulus_timestamp': 1700000000000,
        'response_timestamp': 1700000002500,
        'is_practice': False
    },
    {
        'trial_number': 2,
        'experiment_type': 1,
        'stimulus_id': 'test_file_id_2',
        'correct_emotion': '슬픔',
        'choices': '기쁨, 슬픔, 화남, 놀람, 공포, 혐오, 중립',
        'selected_emotion': '화남',
        'is_correct': False,
        'reaction_time': 3.2,
        'reaction_time_ms': 3200,
        'stimulus_timestamp': 1700000020000,
        'response_timestamp': 1700000023200,
        'is_practice': False
    }
]

def test_data_transformation():
    """Test the data transformation logic"""

    result = {}

    # A. Participant info
    result['이름'] = sample_participant.get('name', '')
    result['성별'] = sample_participant.get('gender', '')
    result['생년월일'] = sample_participant.get('birthdate', '')
    result['DRC코드'] = sample_participant.get('drc_code', '')
    result['학번'] = sample_participant.get('student_id', '')
    result['참가완료시간'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # B. Survey scores
    # MFI
    mfi_items = []
    for i in range(1, 13):
        key = f'MFI_Q{i}'
        if key in sample_survey:
            value = sample_survey[key]
            if i in [1, 3, 6, 7, 9]:  # Reverse items
                value = 6 - value
            mfi_items.append(value)

    result['MFI 신체_총합'] = sum(mfi_items[0:6])
    result['MFI 정신_총합'] = sum(mfi_items[6:12])
    result['MFI 총합'] = result['MFI 신체_총합'] + result['MFI 정신_총합']

    # PHQ-9
    phq9_total = sum(sample_survey.get(f'PHQ9_Q{i}', 0) for i in range(1, 10))
    result['PHQ-9 총합'] = phq9_total

    # TIPI
    result['Extraversion 점수'] = (sample_survey.get('TIPI_Q1', 0) + (8 - sample_survey.get('TIPI_Q6', 0))) / 2
    result['Agreeableness 점수'] = ((8 - sample_survey.get('TIPI_Q2', 0)) + sample_survey.get('TIPI_Q7', 0)) / 2
    result['Conscientiousness 점수'] = (sample_survey.get('TIPI_Q3', 0) + (8 - sample_survey.get('TIPI_Q8', 0))) / 2
    result['Emotional Stability 점수'] = ((8 - sample_survey.get('TIPI_Q4', 0)) + sample_survey.get('TIPI_Q9', 0)) / 2
    result['Openness to Experience 점수'] = (sample_survey.get('TIPI_Q5', 0) + (8 - sample_survey.get('TIPI_Q10', 0))) / 2

    # C. Experiment data
    for idx, response in enumerate(sample_responses, 1):
        prefix = f"1-{idx}"  # Type 1 experiment

        result[f"{prefix} 제시자극파일명"] = response.get('stimulus_id', '')
        result[f"{prefix} 제시자극정서명"] = response.get('correct_emotion', '')
        result[f"{prefix} 선지정서명"] = response.get('choices', '')
        result[f"{prefix} 참가자응답"] = response.get('selected_emotion', '')
        result[f"{prefix} 정답여부"] = 1 if response.get('is_correct', False) else 0
        result[f"{prefix} 반응시간(ms)"] = response.get('reaction_time_ms', 0)

        stimulus_ts = response.get('stimulus_timestamp')
        if stimulus_ts:
            result[f"{prefix} 자극제시시점"] = datetime.fromtimestamp(stimulus_ts / 1000).strftime('%Y-%m-%d-%H:%M:%S')

        response_ts = response.get('response_timestamp')
        if response_ts:
            result[f"{prefix} 응답시점"] = datetime.fromtimestamp(response_ts / 1000).strftime('%Y-%m-%d-%H:%M:%S')

    # Create DataFrame
    df = pd.DataFrame([result])

    # Display results
    print("=" * 80)
    print("Excel Export Data Test")
    print("=" * 80)

    print("\n1. Participant Information:")
    for key in ['이름', '성별', '생년월일', 'DRC코드', '학번', '참가완료시간']:
        print(f"  {key}: {result[key]}")

    print("\n2. Survey Scores:")
    print(f"  MFI 신체_총합: {result['MFI 신체_총합']}")
    print(f"  MFI 정신_총합: {result['MFI 정신_총합']}")
    print(f"  MFI 총합: {result['MFI 총합']}")
    print(f"  PHQ-9 총합: {result['PHQ-9 총합']}")
    print(f"  Extraversion: {result['Extraversion 점수']:.2f}")
    print(f"  Agreeableness: {result['Agreeableness 점수']:.2f}")
    print(f"  Conscientiousness: {result['Conscientiousness 점수']:.2f}")
    print(f"  Emotional Stability: {result['Emotional Stability 점수']:.2f}")
    print(f"  Openness to Experience: {result['Openness to Experience 점수']:.2f}")

    print("\n3. Experiment Data (first 2 trials):")
    for i in range(1, 3):
        prefix = f"1-{i}"
        if f"{prefix} 제시자극파일명" in result:
            print(f"\n  Trial {i}:")
            print(f"    자극파일: {result[f'{prefix} 제시자극파일명']}")
            print(f"    정서: {result[f'{prefix} 제시자극정서명']}")
            print(f"    응답: {result[f'{prefix} 참가자응답']}")
            print(f"    정답여부: {result[f'{prefix} 정답여부']}")
            print(f"    반응시간: {result[f'{prefix} 반응시간(ms)']}ms")

    # Save to Excel for testing
    test_filename = f"test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(test_filename, index=False, sheet_name='실험결과')
    print(f"\nTest Excel file created: {test_filename}")
    print(f"Total columns: {len(df.columns)}")

    return df

if __name__ == "__main__":
    test_data_transformation()
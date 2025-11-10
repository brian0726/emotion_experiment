import pandas as pd
import re
import json

# 엑셀 파일 읽기
df = pd.read_excel('C:/Users/daena/Downloads/2차년도_정서인식컴퓨터과제_데이터 인풋용 엑셀.xlsx')

# 감정명 매핑 (app.py의 ALL_EMOTIONS와 일치시키기)
emotion_name_mapping = {
    "기쁨": "기쁨",
    "분노": "분노",
    "혐오": "혐오",
    "중립": "중립",
    "슬픔": "슬픔",
    "놀람": "놀람",
    "공포": "공포",
    "즐거움": "즐거움",
    "애원하는": "애원하는",
    "실망하는": "실망하는",
    "공감하는": "공감하는",
    "충격받은": "충격받은",
    "질투하는": "질투하는",
    "초조한": "초조한",
    "안심하는": "안심하는",
    "우울한": "우울한",
    "불안한": "불안한",
    "사랑하는": "사랑하는",
    "쌀쌀맞음": "쌀쌀맞음",
    "활기찬": "활기찬",
    "쑥스러운": "쑥스러운",
    "진지한": "진지한",
    "창피한": "창피한",
}

# 영문-한글 매핑 보조
eng_to_kor = {
    "amused": "즐거움",
    "appealing": "애원하는",
    "disappointed": "실망하는",
    "empathic": "공감하는",
    "appalled": "충격받은",
    "jealous": "질투하는",
    "nervous": "초조한",
    "reassured": "안심하는",
    "subdued": "우울한",
    "uneasy": "불안한",
    "loving": "사랑하는",
    "unfriendly": "쌀쌀맞음",
    "vibrant": "활기찬",
    "embarassed": "쑥스러운",
    "grave": "진지한",
    "mortified": "창피한",
}

# 감정별 링크 추출
emotion_links = {}

for idx, row in df.iterrows():
    emotion_col = str(row.iloc[5])  # Unnamed: 5
    url = str(row.iloc[6])  # Unnamed: 6

    if pd.notna(url) and 'drive.google.com' in url:
        # 폴더 ID 추출
        folder_id_match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
        if not folder_id_match:
            continue
        folder_id = folder_id_match.group(1)

        # 감정명 파싱
        kor_name = None

        # 영문(한글) 형태 파싱
        if '(' in emotion_col and ')' in emotion_col:
            match = re.search(r'(\w+)\((.+?)\)', emotion_col)
            if match:
                eng_name = match.group(1).lower()
                kor_from_bracket = match.group(2)

                # 영문명으로 매핑
                if eng_name in eng_to_kor:
                    kor_name = eng_to_kor[eng_name]
                else:
                    kor_name = kor_from_bracket
        else:
            # 순수 한글명 (기본 정서)
            for potential_name in ["기쁨", "분노", "혐오", "중립", "슬픔", "놀람", "공포"]:
                if potential_name in emotion_col:
                    kor_name = potential_name
                    break

        if not kor_name or kor_name not in emotion_name_mapping:
            continue

        # 미디어 타입 결정
        if '10개' in emotion_col or 'YFace_10' in emotion_col:
            media_type = 'image'
        elif 'YFace' in emotion_col and '10' not in emotion_col:
            media_type = 'video'
        elif '아동' in emotion_col or '맥락' in emotion_col:
            media_type = 'context'
        else:
            continue

        # 데이터 저장
        if kor_name not in emotion_links:
            emotion_links[kor_name] = {'image': [], 'video': [], 'context': []}

        emotion_links[kor_name][media_type].append(folder_id)

# 결과 출력
print("# 추출된 감정별 구글 드라이브 폴더 ID")
print(f"# 총 {len(emotion_links)}개 감정")
print()
print("MEDIA_FILES = {")

for emotion in emotion_name_mapping.values():
    if emotion in emotion_links:
        data = emotion_links[emotion]
        print(f'    "{emotion}": {{')
        print(f'        "image": {data["image"]},')
        print(f'        "video": {data["video"]},')
        print(f'        "context": {data["context"]}')
        print(f'    }},')
    else:
        print(f'    "{emotion}": {{"image": [], "video": [], "context": []}},')

print("}")

# JSON 파일로도 저장
with open('media_files.json', 'w', encoding='utf-8') as f:
    json.dump(emotion_links, f, ensure_ascii=False, indent=2)

print("\n✓ media_files.json 파일로 저장 완료")

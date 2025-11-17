"""
엑셀 파일에서 개별 파일 ID를 읽어 MEDIA_FILES 형식으로 변환
"""
import pandas as pd
import json

# 엑셀 파일 읽기
df = pd.read_excel('파일_ID_목록.xlsx', engine='openpyxl')

# 감정별로 파일 ID 그룹화
result = {}

for emotion in df['감정'].unique():
    result[emotion] = {
        'image': [],
        'video': [],
        'context': []
    }

# 각 행을 처리
for _, row in df.iterrows():
    emotion = row['감정']
    media_type = row['자극타입']
    file_id = row['파일ID']

    result[emotion][media_type].append(file_id)

# JSON 파일로 저장
with open('media_files_with_file_ids.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("변환 완료!")
print(f"\n파일 저장: media_files_with_file_ids.json")

# 통계 출력
print("\n=== 통계 ===")
for emotion, media in result.items():
    total = sum(len(files) for files in media.values())
    img = len(media.get('image', []))
    vid = len(media.get('video', []))
    ctx = len(media.get('context', []))
    print(f"{emotion}: {total}개 (이미지:{img}, 동영상:{vid}, 맥락:{ctx})")

"""
공개 구글 드라이브 폴더에서 파일 ID 추출 (API 키 불필요)
"""
import json
import subprocess
import re

def get_file_ids_from_folder(folder_id):
    """curl로 공개 폴더 페이지를 가져와서 파일 ID 추출"""
    try:
        cmd = f'curl -s "https://drive.google.com/drive/folders/{folder_id}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return []

        # 파일 ID 패턴 (33자)
        pattern = r'"([a-zA-Z0-9_-]{33})"'
        potential_ids = re.findall(pattern, result.stdout)

        # 중복 제거 및 필터링
        seen = set([folder_id])
        exclude_prefixes = ['AIzaSy', '6Lc4', '6PSdkF', 'A2ChQF', 'AA2YrT']

        file_ids = []
        for fid in potential_ids:
            if fid not in seen and not any(fid.startswith(p) for p in exclude_prefixes):
                file_ids.append(fid)
                seen.add(fid)

        return file_ids[:10]  # 상위 10개만

    except Exception as e:
        print(f"Error fetching {folder_id}: {e}")
        return []

# media_files.json 읽기
with open("media_files.json", "r", encoding="utf-8") as f:
    folder_data = json.load(f)

result = {}

for emotion, media_types in folder_data.items():
    print(f"처리 중: {emotion}")
    result[emotion] = {}

    for media_type, folder_list in media_types.items():
        if not folder_list:
            result[emotion][media_type] = []
            continue

        folder_id = folder_list[0]
        file_ids = get_file_ids_from_folder(folder_id)
        result[emotion][media_type] = file_ids
        print(f"  {media_type}: {len(file_ids)}개")

# 저장
with open("media_file_ids_extracted.json", 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n완료! media_file_ids_extracted.json에 저장됨")

# 통계
total = 0
for emotion, media in result.items():
    count = sum(len(files) for files in media.values())
    total += count

print(f"\n총 {total}개 파일 ID 추출됨")

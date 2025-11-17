"""
Google Drive API로 폴더의 파일 ID 추출
"""
import json
import requests
import pandas as pd

# API 키 입력
API_KEY = input("Google Drive API 키를 입력하세요: ").strip()

def get_files_from_folder(folder_id, api_key):
    """Google Drive API로 폴더의 파일 목록 가져오기"""
    try:
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "key": api_key,
            "fields": "files(id, name, mimeType)",
            "pageSize": 1000
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        files = data.get("files", [])

        return files

    except Exception as e:
        print(f"Error: {e}")
        return []

# media_files.json 읽기
with open("media_files.json", "r", encoding="utf-8") as f:
    folder_data = json.load(f)

# 엑셀용 데이터 리스트
excel_rows = []
result_json = {}

print("파일 ID 추출 중...")
print("=" * 60)

for emotion, media_types in folder_data.items():
    print(f"\n감정: {emotion}")
    result_json[emotion] = {}

    for media_type, folder_list in media_types.items():
        if not folder_list:
            result_json[emotion][media_type] = []
            continue

        folder_id = folder_list[0]
        print(f"  {media_type}: ", end="")

        files = get_files_from_folder(folder_id, API_KEY)
        file_ids = [f["id"] for f in files]

        result_json[emotion][media_type] = file_ids
        print(f"{len(file_ids)}개 파일")

        # 엑셀용 행 추가
        for idx, file in enumerate(files, 1):
            excel_rows.append({
                "감정": emotion,
                "자극타입": media_type,
                "폴더ID": folder_id,
                "파일번호": idx,
                "파일ID": file["id"],
                "파일명": file["name"],
                "파일타입": file.get("mimeType", "")
            })

# JSON 저장
with open("media_file_ids_extracted.json", 'w', encoding='utf-8') as f:
    json.dump(result_json, f, ensure_ascii=False, indent=2)

# 엑셀 저장
df = pd.DataFrame(excel_rows)
df.to_excel("파일_ID_목록.xlsx", index=False, engine='openpyxl')

print("\n" + "=" * 60)
print("완료!")
print(f"- JSON: media_file_ids_extracted.json")
print(f"- 엑셀: 파일_ID_목록.xlsx")
print(f"\n총 {len(excel_rows)}개 파일 추출됨")

# 통계
print("\n=== 통계 ===")
for emotion, media in result_json.items():
    total = sum(len(files) for files in media.values())
    img = len(media.get('image', []))
    vid = len(media.get('video', []))
    ctx = len(media.get('context', []))
    print(f"{emotion}: {total}개 (이미지:{img}, 동영상:{vid}, 맥락:{ctx})")

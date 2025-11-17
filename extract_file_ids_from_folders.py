"""
구글 드라이브 공개 폴더에서 개별 파일 ID 추출
API 키를 사용하여 각 폴더의 파일 목록 가져오기
"""
import json
import requests
import sys

# API 키 입력받기
API_KEY = input("Google Drive API 키를 입력하세요: ")

def get_files_from_folder(folder_id, api_key):
    """
    Google Drive 폴더에서 파일 목록 가져오기
    """
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

        # 파일 ID만 추출
        return [f["id"] for f in files]

    except Exception as e:
        print(f"Error fetching folder {folder_id}: {e}")
        return []

def extract_all_file_ids(api_key):
    """
    media_files.json의 모든 폴더에서 파일 ID 추출
    """
    # media_files.json 읽기
    with open("media_files.json", "r", encoding="utf-8") as f:
        folder_data = json.load(f)

    result = {}

    for emotion, media_types in folder_data.items():
        print(f"\n처리 중: {emotion}")
        result[emotion] = {}

        for media_type, folder_list in media_types.items():
            if not folder_list or len(folder_list) == 0:
                result[emotion][media_type] = []
                print(f"  {media_type}: 폴더 없음")
                continue

            folder_id = folder_list[0]  # 첫 번째 폴더 ID
            print(f"  {media_type}: {folder_id}", end=" -> ")

            file_ids = get_files_from_folder(folder_id, api_key)
            result[emotion][media_type] = file_ids
            print(f"{len(file_ids)}개 파일")

    return result

if __name__ == "__main__":
    print("=" * 60)
    print("구글 드라이브 폴더에서 개별 파일 ID 추출")
    print("=" * 60)

    all_file_ids = extract_all_file_ids(API_KEY)

    # JSON 파일로 저장
    output_file = "media_file_ids_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_file_ids, f, ensure_ascii=False, indent=2)

    print(f"\n완료! 결과가 {output_file}에 저장되었습니다.")

    # 통계 출력
    print("\n=== 통계 ===")
    for emotion, media in all_file_ids.items():
        total = sum(len(files) for files in media.values())
        print(f"{emotion}: {total}개 파일 (이미지: {len(media['image'])}, 동영상: {len(media.get('video', []))}, 맥락: {len(media.get('context', []))})

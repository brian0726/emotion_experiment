"""
공개 구글 드라이브 폴더에서 파일 ID 추출하는 스크립트
API 키 없이 공개 폴더의 파일 목록을 크롤링
"""
import requests
import re
import json
from media_files import MEDIA_FILES as FOLDER_IDS

def get_files_from_public_folder(folder_id):
    """
    공개 구글 드라이브 폴더에서 파일 ID 목록 추출

    Args:
        folder_id: 구글 드라이브 폴더 ID

    Returns:
        파일 ID 리스트
    """
    try:
        # 구글 드라이브 폴더 페이지 가져오기
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # HTML에서 파일 ID 추출
        # 구글 드라이브는 동적으로 로드되므로 초기 데이터에서 추출
        content = response.text

        # 파일 ID 패턴 찾기 (일반적인 구글 드라이브 ID 형식)
        # ID는 보통 28-44자 길이의 영숫자 문자열
        file_id_pattern = r'"([a-zA-Z0-9_-]{28,44})"'
        potential_ids = re.findall(file_id_pattern, content)

        # 중복 제거 및 폴더 ID 제외
        file_ids = []
        seen = set([folder_id])  # 폴더 자체 ID는 제외

        for file_id in potential_ids:
            if file_id not in seen and len(file_id) >= 28:
                file_ids.append(file_id)
                seen.add(file_id)

        # 처음 20개 정도만 반환 (대부분 실제 파일 ID)
        return file_ids[:20] if file_ids else []

    except Exception as e:
        print(f"Error fetching folder {folder_id}: {e}")
        return []


def extract_all_file_ids():
    """
    모든 감정별 폴더에서 파일 ID 추출
    """
    result = {}

    for emotion, media_types in FOLDER_IDS.items():
        print(f"\n처리 중: {emotion}")
        result[emotion] = {}

        for media_type, folder_list in media_types.items():
            if not folder_list:
                result[emotion][media_type] = []
                continue

            folder_id = folder_list[0]  # 첫 번째 폴더 ID
            print(f"  {media_type}: {folder_id}")

            file_ids = get_files_from_public_folder(folder_id)
            result[emotion][media_type] = file_ids
            print(f"    -> {len(file_ids)}개 파일 발견")

    return result


if __name__ == "__main__":
    print("공개 구글 드라이브 폴더에서 파일 ID 추출 중...")
    print("=" * 60)

    all_file_ids = extract_all_file_ids()

    # JSON 파일로 저장
    output_file = "media_file_ids.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_file_ids, f, ensure_ascii=False, indent=2)

    print(f"\n완료! 결과가 {output_file}에 저장되었습니다.")

    # 통계 출력
    print("\n=== 통계 ===")
    for emotion, media in all_file_ids.items():
        total = sum(len(files) for files in media.values())
        print(f"{emotion}: {total}개 파일 (이미지: {len(media['image'])}, 동영상: {len(media.get('video', []))}, 맥락: {len(media.get('context', []))})")

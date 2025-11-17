"""
공개 구글 드라이브 폴더에서 파일 ID 추출 (API 키 불필요)
"""
import json
import subprocess
import re

def get_file_ids_from_folder(folder_id):
    """
    curl로 공개 폴더 페이지를 가져와서 파일 ID 추출
    """
    try:
        # curl로 폴더 페이지 가져오기
        cmd = f'curl -s "https://drive.google.com/drive/folders/{folder_id}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return []

        content = result.stdout

        # 파일 ID 패턴 찾기 (28-44자 길이)
        pattern = r'"([a-zA-Z0-9_-]{28,44})"'
        potential_ids = re.findall(pattern, content)

        # 중복 제거 및 필터링
        seen = set([folder_id])
        file_ids = []

        # API 키나 토큰 같은 것들 제외
        exclude_prefixes = ['AIzaSy', '6Lc4', '6PSdkF', 'A2ChQF', 'AA2YrT']

        for fid in potential_ids:
            if fid not in seen and len(fid) >= 28:
                # 제외 패턴 체크
                if not any(fid.startswith(prefix) for prefix in exclude_prefixes):
                    file_ids.append(fid)
                    seen.add(fid)

        # 상위 10개만 반환 (대부분 실제 파일 ID)
        return file_ids[:10]

    except Exception as e:
        print(f"Error: {e}")
        return []

def extract_all_file_ids():
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

            folder_id = folder_list[0]
            print(f"  {media_type}: {folder_id}", end=" -> ")

            file_ids = get_file_ids_from_folder(folder_id)
            result[emotion][media_type] = file_ids
            print(f"{len(file_ids)}개 파일")

    return result

if __name__ == "__main__":
    print("=" * 60)
    print("구글 드라이브 공개 폴더에서 파일 ID 추출 (API 키 불필요)")
    print("=" * 60)

    all_file_ids = extract_all_file_ids()

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
")

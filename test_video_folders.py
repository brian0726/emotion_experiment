"""
동영상 폴더에 실제로 파일이 있는지 테스트
"""
import requests

API_KEY = input("Google Drive API 키를 입력하세요: ").strip()

# 테스트할 동영상 폴더들
test_folders = {
    "즐거움": "16Uol3om5G2MLIcWPh25RRptsIxeWR3G5",
    "애원하는": "1L8N6J_mIO0f4tAb7YoLY8LWp2s2qSam7",
    "실망하는": "15oOTzsVi8b9PbSj_DKkLEDuJ09t-opy1",
}

for emotion, folder_id in test_folders.items():
    print(f"\n{emotion} 동영상 폴더 ({folder_id}):")

    url = "https://www.googleapis.com/drive/v3/files"
    params = {
        "q": f"'{folder_id}' in parents and trashed=false",
        "key": API_KEY,
        "fields": "files(id, name, mimeType)",
        "pageSize": 1000
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        files = data.get("files", [])

        print(f"  파일 개수: {len(files)}")
        if files:
            for f in files[:3]:  # 처음 3개만 출력
                print(f"    - {f['name']} ({f['mimeType']})")
        else:
            print("  파일이 없습니다!")

    except Exception as e:
        print(f"  에러: {e}")

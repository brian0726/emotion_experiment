"""
특정 폴더 하나만 테스트
"""
import requests

API_KEY = input("Google Drive API 키 입력: ").strip()

# 즐거움 동영상 폴더 (파일이 있다고 하신 폴더)
folder_id = "16Uol3om5G2MLIcWPh25RRptsIxeWR3G5"

url = "https://www.googleapis.com/drive/v3/files"
params = {
    "q": f"'{folder_id}' in parents and trashed=false",
    "key": API_KEY,
    "fields": "files(id, name, mimeType)",
    "pageSize": 1000
}

print(f"폴더 ID: {folder_id}")
print(f"요청 URL: {url}")
print(f"파라미터: {params}")
print()

response = requests.get(url, params=params, timeout=10)
print(f"응답 상태 코드: {response.status_code}")
print(f"응답 내용:")
print(response.text[:500])
print()

if response.status_code == 200:
    data = response.json()
    files = data.get("files", [])
    print(f"파일 개수: {len(files)}")
    for f in files:
        print(f"  - {f['name']}")
else:
    print("에러 발생!")

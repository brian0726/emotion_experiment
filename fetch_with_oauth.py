"""
OAuth 2.0으로 본인 계정 권한으로 파일 ID 추출
"""
import json
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd

# 권한 스코프
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_credentials():
    """OAuth 2.0 인증 후 credentials 반환"""
    creds = None

    # token.pickle 파일이 있으면 로드
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # 유효한 credentials가 없으면 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # credentials.json 파일이 필요합니다
            if not os.path.exists('credentials.json'):
                print("ERROR: credentials.json 파일이 필요합니다!")
                print("Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 만들어 다운로드하세요.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # credentials 저장
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_files_from_folder_oauth(folder_id, service):
    """OAuth로 폴더의 파일 목록 가져오기 (GIF, JPG, MP4만)"""
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)",
            pageSize=1000
        ).execute()

        all_files = results.get('files', [])

        # GIF, JPG, JPEG, MP4 파일만 필터링
        allowed_extensions = ['.gif', '.jpg', '.jpeg', '.mp4']
        allowed_mimetypes = ['image/gif', 'image/jpeg', 'video/mp4']

        filtered_files = []
        for f in all_files:
            name = f.get('name', '').lower()
            mime = f.get('mimeType', '')

            # 확장자 또는 MIME 타입으로 필터링
            if any(name.endswith(ext) for ext in allowed_extensions) or mime in allowed_mimetypes:
                filtered_files.append(f)

        return filtered_files

    except Exception as e:
        print(f"Error: {e}")
        return []

# OAuth 인증
print("Google 계정으로 로그인 중...")
creds = get_credentials()

if not creds:
    print("인증 실패!")
    exit(1)

# Drive API 서비스 생성
service = build('drive', 'v3', credentials=creds)

# media_files.json 읽기
with open("media_files.json", "r", encoding="utf-8") as f:
    folder_data = json.load(f)

excel_rows = []
result_json = {}

print("\n파일 ID 추출 중...")
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

        files = get_files_from_folder_oauth(folder_id, service)
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

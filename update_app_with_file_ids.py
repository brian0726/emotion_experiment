"""
app.py를 개별 파일 ID 방식으로 업데이트
"""
import json

# 새로운 파일 ID 데이터 로드
with open('media_files_with_file_ids.json', 'r', encoding='utf-8') as f:
    new_media_files = json.load(f)

# app.py 읽기
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. MEDIA_FILES 부분 찾아서 교체
media_files_str = json.dumps(new_media_files, ensure_ascii=False, indent=4)
media_files_python = "MEDIA_FILES = " + media_files_str.replace('    ', '    ')

# MEDIA_FILES 정의 부분 찾기
import re
pattern = r'MEDIA_FILES\s*=\s*\{[^}]+(?:\{[^}]+\}[^}]+)+\}'
new_content = re.sub(pattern, media_files_python, content, flags=re.DOTALL)

# 2. get_media_file 함수 교체
old_function = '''# Google Drive 미디어 파일 가져오기
def get_media_file(emotion, media_type='image'):
    """
    media_type: 'image', 'video', 'context'
    해당 감정의 폴더에서 랜덤하게 파일 하나를 선택

    Returns:
        파일 정보 딕셔너리 {"id": "...", "name": "...", "mimeType": "...", "url": "..."}
        또는 None
    """
    if emotion not in MEDIA_FILES:
        return None

    folders = MEDIA_FILES[emotion].get(media_type, [])
    if not folders:
        return None

    # 랜덤으로 폴더 1개 선택 (현재는 각 타입당 폴더가 1개씩)
    folder_id = random.choice(folders)

    # MIME 타입 필터 결정
    mime_type_prefix = None
    if media_type == 'image':
        mime_type_prefix = "image/"
    elif media_type == 'video':
        mime_type_prefix = "video/"

    # 폴더에서 랜덤 파일 가져오기
    file_info = get_random_file_from_folder(folder_id, mime_type_prefix)

    if file_info:
        # 임베드 가능한 URL 추가
        file_info['url'] = get_file_embed_url(file_info['id'], file_info.get('mimeType', ''))

    return file_info'''

new_function = '''# Google Drive 미디어 파일 가져오기
def get_media_file(emotion, media_type='image'):
    """
    media_type: 'image', 'video', 'context'
    해당 감정의 파일 ID 목록에서 랜덤하게 파일 하나를 선택

    Returns:
        파일 정보 딕셔너리 {"id": "...", "url": "..."}
        또는 None
    """
    if emotion not in MEDIA_FILES:
        return None

    file_ids = MEDIA_FILES[emotion].get(media_type, [])
    if not file_ids:
        return None

    # 랜덤으로 파일 ID 1개 선택
    file_id = random.choice(file_ids)

    # 직접 URL 생성 (API 호출 불필요)
    if media_type == 'video':
        url = f"https://drive.google.com/file/d/{file_id}/preview"
    else:  # image or context
        url = f"https://drive.google.com/uc?export=view&id={file_id}"

    return {
        'id': file_id,
        'url': url,
        'mimeType': 'video/mp4' if media_type == 'video' else 'image/jpeg'
    }'''

new_content = new_content.replace(old_function, new_function)

# 3. gdrive_utils import 제거
new_content = new_content.replace('from gdrive_utils import get_random_file_from_folder, get_file_embed_url\n', '')

# 저장
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("app.py 업데이트 완료!")
print("- MEDIA_FILES를 개별 파일 ID로 변경")
print("- get_media_file() 함수를 API 호출 없이 직접 URL 생성하도록 수정")
print("- gdrive_utils 의존성 제거")

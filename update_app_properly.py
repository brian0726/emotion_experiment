"""
app.py를 개별 파일 ID 방식으로 안전하게 업데이트
"""
import json
import re

# 새로운 파일 ID 데이터 로드
with open('media_file_ids_extracted.json', 'r', encoding='utf-8') as f:
    new_media_files = json.load(f)

# app.py 읽기
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. MEDIA_FILES 부분 찾아서 교체
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'MEDIA_FILES = {' in line:
        start_idx = i
    if start_idx is not None and line.strip() == '}' and 'MEDIA_FILES' in ''.join(lines[max(0, i-50):i]):
        end_idx = i
        break

if start_idx is not None and end_idx is not None:
    # 새로운 MEDIA_FILES 생성
    media_files_str = "MEDIA_FILES = " + json.dumps(new_media_files, ensure_ascii=False, indent=4) + "\n"

    # 교체
    new_lines = lines[:start_idx] + [media_files_str] + lines[end_idx+1:]
else:
    print("MEDIA_FILES를 찾을 수 없습니다!")
    exit(1)

# 2. get_media_file 함수 교체
content = ''.join(new_lines)

old_function_pattern = r'def get_media_file\(emotion, media_type=\'image\'\):.*?return file_info'
new_function = '''def get_media_file(emotion, media_type='image'):
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

content = re.sub(old_function_pattern, new_function, content, flags=re.DOTALL)

# 3. gdrive_utils import 제거
content = re.sub(r'from gdrive_utils import [^\n]+\n', '', content)

# 저장
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("app.py 업데이트 완료!")
print("- MEDIA_FILES를 개별 파일 ID로 변경")
print("- get_media_file() 함수를 API 호출 없이 직접 URL 생성하도록 수정")
print("- gdrive_utils 의존성 제거")

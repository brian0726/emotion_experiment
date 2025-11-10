"""
Google Drive API 유틸리티 함수들
폴더 내 파일 목록을 가져오고 랜덤하게 선택하는 기능
"""
import requests
import random
from typing import List, Optional
import streamlit as st

def get_files_from_folder(folder_id: str, api_key: Optional[str] = None) -> List[dict]:
    """
    Google Drive 폴더에서 파일 목록 가져오기

    Args:
        folder_id: Google Drive 폴더 ID
        api_key: Google Drive API 키 (선택사항)

    Returns:
        파일 정보 딕셔너리 리스트 [{"id": "...", "name": "...", "mimeType": "..."}, ...]
    """
    # API 키가 없으면 Streamlit secrets에서 가져오기 시도
    if api_key is None:
        try:
            api_key = st.secrets.get("GOOGLE_DRIVE_API_KEY", None)
        except:
            api_key = None

    if not api_key:
        # API 키가 없으면 빈 리스트 반환
        return []

    try:
        # Google Drive API v3 사용
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and trashed=false",
            "key": api_key,
            "fields": "files(id, name, mimeType, webContentLink, webViewLink)",
            "pageSize": 1000
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("files", [])

    except Exception as e:
        st.error(f"폴더에서 파일 목록을 가져오는 중 오류 발생: {str(e)}")
        return []


def get_random_file_from_folder(folder_id: str, mime_type_prefix: Optional[str] = None) -> Optional[dict]:
    """
    Google Drive 폴더에서 랜덤하게 파일 하나 선택

    Args:
        folder_id: Google Drive 폴더 ID
        mime_type_prefix: 파일 타입 필터 (예: "image/", "video/")

    Returns:
        선택된 파일 정보 딕셔너리 또는 None
    """
    files = get_files_from_folder(folder_id)

    if not files:
        return None

    # MIME 타입 필터링
    if mime_type_prefix:
        files = [f for f in files if f.get("mimeType", "").startswith(mime_type_prefix)]

    if not files:
        return None

    # 랜덤 선택
    return random.choice(files)


def get_file_direct_url(file_id: str) -> str:
    """
    Google Drive 파일 ID로 직접 다운로드/뷰 URL 생성

    Args:
        file_id: Google Drive 파일 ID

    Returns:
        직접 접근 가능한 URL
    """
    return f"https://drive.google.com/uc?export=view&id={file_id}"


def get_file_embed_url(file_id: str, mime_type: str = "") -> str:
    """
    Google Drive 파일을 임베드할 수 있는 URL 생성

    Args:
        file_id: Google Drive 파일 ID
        mime_type: 파일의 MIME 타입

    Returns:
        임베드 가능한 URL
    """
    if mime_type.startswith("video/"):
        # 동영상은 preview 모드 사용
        return f"https://drive.google.com/file/d/{file_id}/preview"
    else:
        # 이미지는 직접 다운로드 URL 사용
        return f"https://drive.google.com/uc?export=view&id={file_id}"


# 캐싱을 위한 함수 (성능 최적화)
@st.cache_data(ttl=3600)  # 1시간 캐싱
def get_files_from_folder_cached(folder_id: str) -> List[dict]:
    """
    캐싱된 버전의 get_files_from_folder
    같은 폴더를 반복 조회할 때 성능 향상
    """
    return get_files_from_folder(folder_id)

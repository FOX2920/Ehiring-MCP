import os
from dotenv import load_dotenv
from typing import List, Optional, Any, Dict
from fastmcp import FastMCP, Context


from datetime import datetime, date
import requests
from bs4 import BeautifulSoup
from time import time
import pdfplumber
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from pytz import timezone
import re
from html import unescape

load_dotenv()

mcp = FastMCP(
    name="base-hiring-assistant",
)

# Configuration - Load from .env file
BASE_API_KEY = os.getenv('BASE_API_KEY')
if not BASE_API_KEY:
    raise ValueError("BASE_API_KEY chưa được cấu hình trong file .env")

# Account API Key (optional) - để lấy thông tin users cho reviews
ACCOUNT_API_KEY = os.getenv('ACCOUNT_API_KEY', None)

# Cache configuration
CACHE_TTL = 300  # 5 phút cache
_cache = {
    'openings': {'data': None, 'timestamp': 0},
    'job_descriptions': {'data': None, 'timestamp': 0},
    'users_info': {'data': None, 'timestamp': 0}
}

# =================================================================
# Helper Functions
# =================================================================

def get_base_openings(api_key, use_cache=True):
    """Truy xuất vị trí tuyển dụng đang hoạt động từ Base API (có cache)"""
    current_time = time()
    if not api_key:
        raise Exception("BASE_API_KEY chưa được cấu hình")
    
    # Kiểm tra cache nếu được bật
    if use_cache and _cache['openings']['data'] is not None:
        if current_time - _cache['openings']['timestamp'] < CACHE_TTL:
            return _cache['openings']['data']
    
    url = "https://hiring.base.vn/publicapi/v2/opening/list"
    payload = {'access_token_v2': api_key}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến Base API: {e}")

    data = response.json()
    openings = data.get('openings', [])
    
    # Lọc vị trí với trạng thái '10' (đang hoạt động)
    filtered_openings = [
        {"id": opening['id'], "name": opening['name']}
        for opening in openings
        if opening.get('status') == '10'
    ]
    
    # Lưu vào cache
    if use_cache:
        _cache['openings'] = {'data': filtered_openings, 'timestamp': current_time}
    
    return filtered_openings

def get_job_descriptions(api_key, use_cache=True):
    """Truy xuất JD (Job Description) từ các vị trí tuyển dụng đang mở (có cache)"""
    current_time = time()
    if not api_key:
        raise Exception("BASE_API_KEY chưa được cấu hình")

    # Kiểm tra cache
    if use_cache and _cache['job_descriptions']['data'] is not None:
        if current_time - _cache['job_descriptions']['timestamp'] < CACHE_TTL:
            return _cache['job_descriptions']['data']
    
    url = "https://hiring.base.vn/publicapi/v2/opening/list"
    payload = {'access_token_v2': api_key}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến Base API: {e}")

    data = response.json()
    
    if 'openings' in data:
        openings = data['openings']
        results = []
        
        for opening in openings:
            if opening.get('status') == '10':  # Chỉ lấy vị trí đang mở
                html_content = opening.get('content', '')
                soup = BeautifulSoup(html_content, "html.parser")
                text_content = soup.get_text()
                
                if len(text_content) >= 10:  # Chỉ lấy JD có nội dung đủ dài
                    results.append({
                        "id": opening['id'],
                        "name": opening['name'],
                        "job_description": text_content.strip(),
                        "html_content": html_content
                    })
        
        if use_cache:
            _cache['job_descriptions'] = {'data': results, 'timestamp': current_time}
        
        return results
    return []

def extract_message(evaluations):
    """Trích xuất nội dung văn bản từ đánh giá HTML"""
    if isinstance(evaluations, list) and len(evaluations) > 0:
        raw_html = evaluations[0].get('content', '')
        soup = BeautifulSoup(raw_html, "html.parser")
        text = " ".join(soup.stripped_strings)
        return text
    return None

def remove_html_tags(text):
    """Bỏ HTML tags và chuyển đổi thành text thuần túy"""
    if not text:
        return ""
    # Chuyển các thẻ <br> thành xuống dòng
    text = re.sub(r'<br\s*/?>', '\n', text)
    # Bỏ tất cả các thẻ HTML còn lại
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape các ký tự HTML entities (&lt;, &gt;, &amp;, etc.)
    text = unescape(text)
    # Loại bỏ các khoảng trắng thừa
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def get_users_info(use_cache=True):
    """Lấy thông tin users từ Account API và map username -> name + title (có cache)"""
    if not ACCOUNT_API_KEY:
        return {}
    
    current_time = time()
    
    # Kiểm tra cache
    if use_cache and _cache['users_info']['data'] is not None:
        if current_time - _cache['users_info']['timestamp'] < CACHE_TTL:
            return _cache['users_info']['data']
    
    try:
        users_url = "https://account.base.vn/extapi/v1/users"
        users_payload = {'access_token_v2': ACCOUNT_API_KEY}
        users_response = requests.post(users_url, data=users_payload, timeout=10)
        users_response.raise_for_status()
        users_data = users_response.json()
        
        # Tạo dictionary để map username -> name + title
        username_to_info = {}
        if 'users' in users_data and isinstance(users_data['users'], list):
            for user in users_data['users']:
                username = user.get('username')
                name = user.get('name', '')
                title = user.get('title', '')
                if username:
                    # Nếu là Hoang Tran thì thay title thành CEO
                    if name == "Hoang Tran":
                        title = "CEO"
                    
                    # Kết hợp name và title
                    if title:
                        username_to_info[username] = {"name": name, "title": title}
                    else:
                        username_to_info[username] = {"name": name, "title": ""}
        
        # Lưu vào cache
        if use_cache:
            _cache['users_info'] = {'data': username_to_info, 'timestamp': current_time}
        
        return username_to_info
    except Exception as e:
        # Nếu có lỗi, trả về dict rỗng
        return {}

def process_evaluations(evaluations):
    """Xử lý evaluations và trả về danh sách reviews với đầy đủ thông tin (tên, chức danh, nội dung)"""
    if not isinstance(evaluations, list) or len(evaluations) == 0:
        return []
    
    # Lấy thông tin users
    username_to_info = get_users_info(use_cache=True)
    
    reviews = []
    for eval_item in evaluations:
        if 'content' in eval_item:
            # Bỏ HTML tags
            clean_content = remove_html_tags(eval_item.get('content', ''))
            
            # Lấy username và chuyển thành tên thật + chức danh
            username = eval_item.get('username')
            user_info = username_to_info.get(username, {}) if username else {}
            name = user_info.get('name', username) if user_info else (username if username else "N/A")
            title = user_info.get('title', '') if user_info else ''
            
            review = {
                "id": eval_item.get('id'),
                "name": name,
                "title": title,
                "content": clean_content
            }
            reviews.append(review)
    
    return reviews

def extract_text_from_pdf(url=None, file_bytes=None):
    """Trích xuất text từ PDF URL hoặc file bytes bằng pdfplumber"""
    pdf_file = None
    if file_bytes:
        pdf_file = file_bytes
    elif url:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            pdf_file = BytesIO(response.content)
        except Exception:
            return None
    else:
        return None
    
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Trang {page_num} ---\n"
                    text += page_text
        return text.strip() if text else None
    except Exception as e:
        return None

def extract_text_from_docx(file_bytes):
    """Trích xuất text từ DOCX file bytes"""
    if not DOCX_AVAILABLE:
        return None
    try:
        doc = Document(file_bytes)
        text = "\n".join([p.text for p in doc.paragraphs]).strip()
        return text if text else None
    except Exception as e:
        return None

def download_file_to_bytes(url):
    """Tải file từ URL và trả về BytesIO"""
    if not url:
        return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception:
        return None

def is_target_file(url, name):
    """Kiểm tra xem file có phải PDF/DOCX/DOC không"""
    if not url or not name:
        return False
    url_low = url.lower().split('?')[0]
    name_low = name.lower()
    return url_low.endswith(('.pdf', '.docx', '.doc')) or name_low.endswith(('.pdf', '.docx', '.doc'))

def find_files_in_html(html_content):
    """Tìm các file PDF/DOCX/DOC trong HTML content"""
    found = []
    if not html_content:
        return found
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            name = a.get_text().strip() or href.split('/')[-1]
            if is_target_file(href, name):
                found.append((href, name))
        return found
    except Exception:
        return found

def get_offer_letter(candidate_id, api_key):
    """Lấy offer letter từ messages API của ứng viên"""
    if not candidate_id or not api_key:
        return None
    
    try:
        url = "https://hiring.base.vn/publicapi/v2/candidate/messages"
        payload = {
            'access_token_v2': api_key,
            'id': candidate_id
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if not data or 'messages' not in data:
            return None
        
        messages = data['messages']
        if not messages:
            return None
        
        # Duyệt từ tin nhắn mới nhất về cũ nhất
        for msg in messages:
            # Ưu tiên tìm trong attachments
            priority_files = []
            if msg.get('has_attachment', 0) > 0:
                for att in msg.get('attachments', []):
                    url_att = att.get('src') or att.get('url') or att.get('org')
                    name_att = att.get('name', 'unknown')
                    if url_att and is_target_file(url_att, name_att):
                        priority_files.append((url_att, name_att))
            
            # Nếu không có trong attachments, tìm trong HTML content
            secondary_files = []
            if not priority_files:
                secondary_files = find_files_in_html(msg.get('content', ''))
            
            all_files = priority_files + secondary_files
            if not all_files:
                continue
            
            # Thử tải và trích xuất file đầu tiên tìm được
            for file_url, file_name in all_files:
                file_bytes = download_file_to_bytes(file_url)
                if not file_bytes:
                    continue
                
                ext = file_name.lower().split('.')[-1] if '.' in file_name else file_url.split('.')[-1].split('?')[0].lower()
                text = None
                
                if 'pdf' in ext:
                    text = extract_text_from_pdf(file_bytes=file_bytes)
                elif 'docx' in ext and DOCX_AVAILABLE:
                    text = extract_text_from_docx(file_bytes)
                elif 'doc' == ext:
                    text = None  # File .doc cũ, không hỗ trợ
                
                if text:
                    return {
                        "url": file_url,
                        "name": file_name,
                        "text": text
                    }
        
        return None
    except Exception as e:
        # Nếu có lỗi, trả về None (không làm gián đoạn flow chính)
        return None

def extract_text_from_cv_url(url):
    """Trích xuất text từ CV URL bằng pdfplumber hoặc python-docx"""
    if not url:
        return None
    
    try:
        # Detect extension from URL
        url_low = url.lower().split('?')[0]
        
        if url_low.endswith('.pdf'):
            return extract_text_from_pdf(url=url)
        elif url_low.endswith(('.docx', '.doc')):
             file_bytes = download_file_to_bytes(url)
             if file_bytes:
                 if url_low.endswith('.docx'):
                     return extract_text_from_docx(file_bytes)
                 # Note: .doc is still not supported by python-docx, but we try as fallback
                 # or simply return None if it fails in extract_text_from_docx
                 return extract_text_from_docx(file_bytes)
        
        # Fallback: try download and guess if no extension
        file_bytes = download_file_to_bytes(url)
        if file_bytes:
            # Try PDF first
            text = extract_text_from_pdf(file_bytes=file_bytes)
            if not text and DOCX_AVAILABLE:
                text = extract_text_from_docx(file_bytes)
            return text
            
        return None
    except Exception:
        return None

def find_opening_id_by_name(query_name, api_key, similarity_threshold=0.5):
    """Tìm opening_id gần nhất với query_name bằng cosine similarity"""
    openings = get_base_openings(api_key, use_cache=True)
    
    if not openings:
        return None, None, 0.0
    
    # Nếu tìm thấy chính xác theo id hoặc name
    exact_match = next((op for op in openings if op['id'] == query_name or op['name'] == query_name), None)
    if exact_match:
        return exact_match['id'], exact_match['name'], 1.0
    
    # Nếu không tìm thấy chính xác, dùng cosine similarity
    opening_names = [op['name'] for op in openings]
    
    if not opening_names:
        return None, None, 0.0
    
    # Vectorize các tên opening
    vectorizer = TfidfVectorizer()
    try:
        name_vectors = vectorizer.fit_transform(opening_names)
        query_vector = vectorizer.transform([query_name])
        
        # Tính cosine similarity
        similarities = cosine_similarity(query_vector, name_vectors).flatten()
        
        # Tìm index có similarity cao nhất
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        # Nếu similarity >= threshold, trả về opening đó
        if best_similarity >= similarity_threshold:
            best_opening = openings[best_idx]
            return best_opening['id'], best_opening['name'], float(best_similarity)
        else:
            return None, None, float(best_similarity)
    except Exception:
        # Nếu có lỗi trong vectorization, trả về None
        return None, None, 0.0

def find_candidate_by_name_in_opening(candidate_name, opening_id, api_key, similarity_threshold=0.5, filter_stages=None):
    """Tìm candidate_id dựa trên tên ứng viên trong một opening cụ thể bằng cosine similarity."""
    if not candidate_name or not opening_id:
        return None, 0.0
    
    # Lấy danh sách candidates của opening đó
    url = "https://hiring.base.vn/publicapi/v2/candidate/list"
    payload = {
        'access_token_v2': api_key,
        'opening_id': opening_id,
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return None, 0.0
    
    data = response.json()
    if 'candidates' not in data or not data['candidates']:
        return None, 0.0
    
    # Lọc theo stage nếu có filter_stages
    if filter_stages:
        filtered_candidates = []
        for candidate in data['candidates']:
            stage_name = candidate.get('stage_name', '')
            if stage_name and stage_name in filter_stages:
                filtered_candidates.append(candidate)
        
        if not filtered_candidates:
            return None, 0.0
    else:
        # Không lọc stage, lấy tất cả candidates
        filtered_candidates = data['candidates']
    
    # Tìm candidate bằng tên với cosine similarity trong danh sách đã lọc
    candidate_names = [c.get('name', '') for c in filtered_candidates if c.get('name')]
    
    if not candidate_names:
        return None, 0.0
    
    # Kiểm tra exact match trước
    exact_match = next((c for c in filtered_candidates if c.get('name') == candidate_name), None)
    if exact_match:
        return exact_match.get('id'), 1.0
    
    # Dùng cosine similarity để tìm candidate name gần nhất
    try:
        vectorizer = TfidfVectorizer()
        name_vectors = vectorizer.fit_transform(candidate_names)
        query_vector = vectorizer.transform([candidate_name])
        
        similarities = cosine_similarity(query_vector, name_vectors).flatten()
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        # Nếu similarity >= threshold, trả về candidate đó
        if best_similarity >= similarity_threshold:
            candidates_with_names = [c for c in filtered_candidates if c.get('name')]
            if best_idx < len(candidates_with_names):
                best_candidate = candidates_with_names[best_idx]
                return best_candidate.get('id'), float(best_similarity)
        
        return None, float(best_similarity)
    except Exception:
        return None, 0.0

def get_candidates_for_opening(opening_id, api_key, start_date=None, end_date=None, stage_name=None):
    """Truy xuất ứng viên cho một vị trí tuyển dụng cụ thể trong khoảng thời gian (luôn có cv_text)"""
    url = "https://hiring.base.vn/publicapi/v2/candidate/list"
    
    payload = {
        'access_token_v2': api_key,
        'opening_id': opening_id,
    }
    
    if start_date:
        payload['start_date'] = start_date.strftime('%Y-%m-%d') if isinstance(start_date, date) else start_date
    if end_date:
        payload['end_date'] = end_date.strftime('%Y-%m-%d') if isinstance(end_date, date) else end_date
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến Base API khi lấy ứng viên: {e}")

    data = response.json()
    if 'candidates' in data and data['candidates']:
        # Nếu có stage_name, tìm các stage name phù hợp bằng cosine similarity
        matching_stage_names = None
        if stage_name is not None:
            # Thu thập tất cả stage_name unique từ candidates
            all_stage_names = list(set([
                candidate.get('stage_name', '') 
                for candidate in data['candidates'] 
                if candidate.get('stage_name')
            ]))
            
            if not all_stage_names:
                # Nếu không có stage_name nào, lấy tất cả
                matching_stage_names = None
            else:
                # Kiểm tra exact match trước
                if stage_name in all_stage_names:
                    matching_stage_names = [stage_name]
                else:
                    # Dùng cosine similarity để tìm stage name gần nhất
                    try:
                        vectorizer = TfidfVectorizer()
                        stage_vectors = vectorizer.fit_transform(all_stage_names)
                        query_vector = vectorizer.transform([stage_name])
                        
                        similarities = cosine_similarity(query_vector, stage_vectors).flatten()
                        best_idx = np.argmax(similarities)
                        best_similarity = similarities[best_idx]
                        
                        # Nếu similarity >= 0.3, lấy stage name đó (ngưỡng thấp để bao quát hơn)
                        if best_similarity >= 0.3:
                            matching_stage_names = [all_stage_names[best_idx]]
                        else:
                            # Nếu không tìm thấy gì phù hợp, lấy tất cả
                            matching_stage_names = None
                    except Exception:
                        # Nếu có lỗi trong vectorization, lấy tất cả
                        matching_stage_names = None
        
        # Bước 1: Lọc ứng viên theo stage_name trước (chưa trích xuất cv_text để tiết kiệm request)
        filtered_candidates = []
        for candidate in data['candidates']:
            # Lọc theo stage_name nếu có matching_stage_names
            if matching_stage_names is not None:
                candidate_stage_name = candidate.get('stage_name', '')
                if candidate_stage_name not in matching_stage_names:
                    continue
            
            filtered_candidates.append(candidate)
        
        # Nếu số lượng ứng viên lọc được > 10, chỉ lấy những người cập nhật trong vòng 7 ngày gần đây
        if len(filtered_candidates) > 10:
            from datetime import timedelta
            seven_days_ago_ts = int((datetime.now() - timedelta(days=7)).timestamp())
            filtered_candidates = [
                c for c in filtered_candidates 
                if int(c.get('last_update', 0)) >= seven_days_ago_ts
            ]
        
        # Bước 2: Trích xuất cv_text chỉ cho các ứng viên đã được lọc
        candidates = []
        for candidate in filtered_candidates:
            cv_urls = candidate.get('cvs', [])
            cv_url = cv_urls[0] if isinstance(cv_urls, list) and len(cv_urls) > 0 else None
            
            # Chỉ trích xuất cv_text từ CV URL sau khi đã lọc xong (tiết kiệm request Gemini)
            cv_text = None
            if cv_url:
                cv_text = extract_text_from_cv_url(cv_url)
            
            # Xử lý evaluations để lấy reviews chi tiết
            reviews = process_evaluations(candidate.get('evaluations', []))
            # Giữ lại review cũ (text đơn giản) để tương thích ngược
            review = extract_message(candidate.get('evaluations', []))
            
            form_data = {}
            if 'form' in candidate and isinstance(candidate['form'], list):
                for item in candidate['form']:
                    if isinstance(item, dict) and 'id' in item and 'value' in item:
                        form_data[item['id']] = item['value']
            

            
            # Chuyển đổi last_update sang HCM timezone
            last_update_hcm = None
            last_update_ts = candidate.get('last_update')
            if last_update_ts:
                try:
                    timestamp = int(last_update_ts)
                    dt = datetime.fromtimestamp(timestamp, tz=timezone('UTC'))
                    dt_hcm = dt.astimezone(timezone('Asia/Ho_Chi_Minh'))
                    last_update_hcm = dt_hcm.isoformat()
                except (ValueError, TypeError, OSError):
                    pass
            
            candidate_info = {
                "id": candidate.get('id'),
                "name": candidate.get('name'),
                "email": candidate.get('email'),
                "phone": candidate.get('phone'),
                "gender": candidate.get('gender'),
                "cv_url": cv_url,
                "cv_text": cv_text,
                "review": review,  # Giữ lại để tương thích ngược
                "reviews": reviews,  # Danh sách reviews chi tiết với tên, chức danh, nội dung
                "form_data": form_data,
                "opening_id": opening_id,
                "stage_id": candidate.get('stage_id'),
                "stage_name": candidate.get('stage_name'),
                "last_update": last_update_hcm,
            }
            
            candidates.append(candidate_info)
        
        return candidates
    return []

def get_interviews(api_key, start_date=None, end_date=None, opening_id=None, filter_date=None):
    """Truy xuất lịch phỏng vấn từ Base API, chỉ trả về các trường quan trọng. Lọc dựa trên date của time_dt."""
    url = "https://hiring.base.vn/publicapi/v2/interview/list"
    
    payload = {
        'access_token_v2': api_key,
    }
    
    # Không truyền start_date/end_date vào payload API Base
    # Thay vào đó sẽ lọc dựa trên time_dt sau khi nhận dữ liệu
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến Base API khi lấy lịch phỏng vấn: {e}")

    data = response.json()
    if 'interviews' in data and data['interviews']:
        interviews = data['interviews']
        
        # Nếu có opening_id, lọc theo opening_id
        if opening_id:
            interviews = [
                interview for interview in interviews
                if interview.get('opening_id') == opening_id
            ]
        
        # Xử lý và chỉ lấy các trường quan trọng
        processed_interviews = []
        hcm_tz = timezone('Asia/Ho_Chi_Minh')
        
        # Chuyển đổi start_date và end_date thành date objects nếu có
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = start_date if isinstance(start_date, date) else datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date_obj = end_date if isinstance(end_date, date) else datetime.strptime(end_date, "%Y-%m-%d").date()
        
        for interview in interviews:
            # Chỉ lấy các trường quan trọng
            processed_interview = {
                'id': interview.get('id'),
                'candidate_id': interview.get('candidate_id'),
                'candidate_name': interview.get('candidate_name'),
                'opening_name': interview.get('opening_name'),
                'time_dt': None
            }
            
            # Chuyển đổi timestamp 'time' sang datetime với timezone Asia/Ho_Chi_Minh
            time_dt_date = None
            if 'time' in interview and interview.get('time'):
                try:
                    timestamp = int(interview['time'])
                    dt = datetime.fromtimestamp(timestamp, tz=timezone('UTC'))
                    dt_hcm = dt.astimezone(hcm_tz)
                    processed_interview['time_dt'] = dt_hcm.isoformat()
                    time_dt_date = dt_hcm.date()  # Lấy date để lọc
                except (ValueError, TypeError, OSError):
                    pass
            
            # Lọc dựa trên date của time_dt với filter_date (ưu tiên cao nhất)
            if filter_date:
                if time_dt_date is None or time_dt_date != filter_date:
                    continue  # Bỏ qua nếu không có time_dt hoặc date không khớp
            # Lọc dựa trên start_date và end_date của time_dt
            elif start_date_obj or end_date_obj:
                if time_dt_date is None:
                    continue  # Bỏ qua nếu không có time_dt
                if start_date_obj and time_dt_date < start_date_obj:
                    continue  # Bỏ qua nếu trước start_date
                if end_date_obj and time_dt_date > end_date_obj:
                    continue  # Bỏ qua nếu sau end_date
            
            processed_interviews.append(processed_interview)
        
        return processed_interviews
    
    return []



def get_opening_stages(opening_id, api_key):
    """Lấy danh sách tên các vòng (stages) của một opening từ Base API"""
    if not opening_id or not api_key:
        return []
    
    try:
        url = "https://hiring.base.vn/publicapi/v2/opening/get"
        payload = {
            'access_token_v2': api_key,
            'id': opening_id
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        
        # Trích xuất danh sách stages từ opening.stats.stages
        stages_list = result.get('opening', {}).get('stats', {}).get('stages', [])
        
        # Chỉ lấy tên của các stages
        stage_names = [stage.get('name', '') for stage in stages_list if stage.get('name')]
        
        return stage_names
    except Exception as e:
        # Nếu có lỗi, trả về list rỗng
        return []

def get_opening_content(opening_id, api_key):
    """Lấy nội dung chi tiết (JD) của một opening từ Base API"""
    if not opening_id or not api_key:
        return None
    
    try:
        url = "https://hiring.base.vn/publicapi/v2/opening/get"
        payload = {
            'access_token_v2': api_key,
            'id': opening_id
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        
        # Trích xuất content (JD)
        content = result.get('opening', {}).get('content')
        
        # Làm sạch HTML tags nếu cần, hoặc giữ nguyên tùy yêu cầu
        # Ở đây ta trả về raw content hoặc text đã làm sạch
        if content:
            return remove_html_tags(content)
            
        return None
    except Exception:
        return None

def get_candidate_details(candidate_id, api_key):
    """Lấy và xử lý dữ liệu chi tiết ứng viên từ API Base.vn, trả về JSON phẳng"""
    url = "https://hiring.base.vn/publicapi/v2/candidate/get"
    
    payload = {
        'access_token_v2': api_key,
        'id': candidate_id
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Lỗi kết nối đến Base API khi lấy chi tiết ứng viên: {e}")
    
    raw_response = response.json()
    
    # Kiểm tra API có trả về lỗi logic không (vd: 'code': 1 là thành công)
    if raw_response.get('code') != 1 or not raw_response.get('candidate'):
        raise Exception(f"Không tìm thấy ứng viên với ID '{candidate_id}'. {raw_response.get('message', '')}")
    
    # Lấy dữ liệu gốc của ứng viên
    candidate_data = raw_response.get('candidate', {})
    
    # Hàm trợ giúp để "làm phẳng" các danh sách lồng nhau
    def flatten_fields(field_list):
        """Chuyển đổi danh sách [{'id': 'key1', 'value': 'val1'}, ...] thành {'key1': 'val1', ...}"""
        flat_dict = {}
        if isinstance(field_list, list):
            for item in field_list:
                if isinstance(item, dict) and 'id' in item:
                    flat_dict[item['id']] = item.get('value')
        return flat_dict
    
    # Bắt đầu với các trường dữ liệu chính
    # Lấy opening info từ nhiều nguồn để đảm bảo có dữ liệu
    # Ưu tiên lấy từ candidate_data['opening_export'] (root level) theo hướng dẫn mới
    opening_export = candidate_data.get('opening_export', {})
    if not opening_export:
        # Fallback: thử tìm trong evaluations (cách cũ)
        evaluations = candidate_data.get('evaluations') or []
        opening_export = evaluations[0].get('opening_export', {}) if evaluations else {}
    
    # Thử lấy opening_name từ nhiều nguồn
    opening_name = (
        opening_export.get('name') or  # Từ opening_export.name
        candidate_data.get('title') or  # Từ title field
        None
    )
    
    # Nếu không có opening_name, thử tìm trong lịch phỏng vấn gần đây (fallback)
    if not opening_name:
        try:
            # Lấy danh sách interview (mặc định là gần đây)
            # Hàm get_interviews được định nghĩa sau, nhưng sẽ có sẵn khi hàm này được gọi
            interviews = get_interviews(api_key)
            
            # Tìm interview của candidate này
            candidate_id_str = str(candidate_data.get('id'))
            for interview in interviews:
                if str(interview.get('candidate_id')) == candidate_id_str:
                    interview_opening_name = interview.get('opening_name')
                    if interview_opening_name:
                        opening_name = interview_opening_name
                        break
        except Exception:
            pass
            
    # Đảm bảo opening_name không None
    if not opening_name:
        opening_name = ""
    
    # Thử lấy opening_id từ nhiều nguồn
    opening_id = (
        opening_export.get('id') or  # Từ opening_export.id
        ""  # Default to empty string instead of None
    )
    
    # Nếu không có opening_id nhưng có opening_name, thử tìm opening_id
    if not opening_id and opening_name:
        try:
            found_id, _, _ = find_opening_id_by_name(opening_name, api_key)
            if found_id:
                opening_id = found_id
        except:
            pass
    
    refined_data = {
        'id': candidate_data.get('id'),
        'ten': candidate_data.get('name'),
        'email': candidate_data.get('email'),
        'so_dien_thoai': candidate_data.get('phone'),
        
        # Sử dụng opening_name đã xử lý ở trên, đảm bảo không None
        'vi_tri_ung_tuyen': opening_name,
        
        # Sử dụng opening_id đã xử lý ở trên, đảm bảo không None
        'opening_id': opening_id,
        
        # Lấy stage_id và stage_name
        'stage_id': candidate_data.get('stage_id'),
        'stage_name': candidate_data.get('stage_name', candidate_data.get('status')),
        
        'nguon_ung_vien': candidate_data.get('source'),
        'ngay_sinh': candidate_data.get('dob'),
        'gioi_tinh': candidate_data.get('gender_text'),
        'dia_chi_hien_tai': candidate_data.get('address'),
        'cccd': candidate_data.get('ssn'),
        'cv_url': (candidate_data.get('cvs') or [None])[0]
    }
    
    # Xử lý và gộp dữ liệu từ 'fields' và 'form'
    field_data = flatten_fields(candidate_data.get('fields', []))
    form_data = flatten_fields(candidate_data.get('form', []))
    
    # Cập nhật vào dict chính
    refined_data.update(field_data)
    refined_data.update(form_data)
    
    # Xử lý evaluations để lấy reviews chi tiết
    reviews = process_evaluations(candidate_data.get('evaluations', []))
    refined_data['reviews'] = reviews
    
    return refined_data

# =================================================================
# MCP Tools
# =================================================================

@mcp.tool(
    name="get_job_description",
    description="Lấy JD (Job Description) theo opening_name hoặc opening_id.",
    tags={"hiring", "job", "description"},
    annotations={"readOnlyHint": True}
)
async def get_job_description(ctx: Context, opening_name_or_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Lấy JD (Job Description) theo opening_name hoặc opening_id. 
    Nếu không có tham số hoặc không tìm thấy, trả về tất cả các opening có status 10 (chỉ id và name).
    
    Args:
        opening_name_or_id: Tên hoặc ID của vị trí tuyển dụng. Bỏ trống để lấy tất cả các opening có status 10.
    """
    try:
        await ctx.info(f"Getting job description for: {opening_name_or_id}")

        # Lấy danh sách openings có status 10 (chỉ id và name)
        openings = get_base_openings(BASE_API_KEY, use_cache=True)
        
        # Nếu không có opening_name_or_id, trả về tất cả các opening có status 10 (chỉ id và name)
        if not opening_name_or_id:
            return {
                "success": True,
                "query": None,
                "message": "Trả về tất cả các opening có status 10.",
                "total_openings": len(openings),
                "openings": openings
            }
        
        # Tìm opening_id từ name hoặc id bằng cosine similarity
        opening_id, matched_name, similarity_score = find_opening_id_by_name(
            opening_name_or_id, 
            BASE_API_KEY
        )
        
        # Nếu không tìm thấy opening cụ thể, trả về tất cả các opening có status 10 (chỉ id và name)
        if not opening_id:
            return {
                "success": True,
                "query": opening_name_or_id,
                "message": f"Không tìm thấy vị trí phù hợp với '{opening_name_or_id}'. Trả về tất cả các opening có status 10.",
                "similarity_score": similarity_score,
                "total_openings": len(openings),
                "openings": openings
            }
        
        # Lấy JD (Job Description) để tìm JD cụ thể
        jds = get_job_descriptions(BASE_API_KEY, use_cache=True)
        jd = next((jd for jd in jds if jd['id'] == opening_id), None)
        
        if not jd:
            # Thử làm mới cache nếu không tìm thấy
            jds = get_job_descriptions(BASE_API_KEY, use_cache=False)
            jd = next((jd for jd in jds if jd['id'] == opening_id), None)
        
        # Nếu vẫn không tìm thấy JD cụ thể, trả về tất cả các opening có status 10 (chỉ id và name)
        if not jd:
            return {
                "success": True,
                "query": opening_name_or_id,
                "opening_id": opening_id,
                "opening_name": matched_name,
                "similarity_score": similarity_score,
                "message": f"Không tìm thấy JD cho vị trí '{opening_name_or_id}'. Trả về tất cả các opening có status 10.",
                "total_openings": len(openings),
                "openings": openings
            }
        
        # Lấy danh sách stages cho opening này
        stages = get_opening_stages(opening_id, BASE_API_KEY)
        
        return {
            "success": True,
            "query": opening_name_or_id,
            "opening_id": opening_id,
            "opening_name": matched_name,
            "similarity_score": similarity_score,
            "job_description": jd['job_description'],
            "stages": stages
        }
    except Exception as e:
        raise Exception(f"Lỗi khi lấy JD: {str(e)}")

@mcp.tool(
    name="get_candidates_by_opening",
    description="Lấy DANH SÁCH ứng viên (List/Screening). Dùng để lọc diện rộng, tìm kiếm tổng quát.",
    tags={"hiring", "candidate", "list"},
    annotations={"readOnlyHint": True}
)
async def get_candidates_by_opening(
    ctx: Context,
    opening_name_or_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    stage_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lấy DANH SÁCH ứng viên (List/Screening).
    Sử dụng tool này khi bạn muốn xem danh sách tổng quát, sàng lọc theo ngày hoặc trạng thái.
    
    Args:
        opening_name_or_id: Tên hoặc ID của vị trí tuyển dụng
        start_date: Ngày bắt đầu lọc ứng viên (YYYY-MM-DD). Bỏ trống để lấy tất cả.
        end_date: Ngày kết thúc lọc ứng viên (YYYY-MM-DD). Bỏ trống để lấy tất cả.
        stage_name: Lọc ứng viên theo stage name. Bỏ trống để lấy tất cả.
    """
    try:
        await ctx.info(f"Fetching candidates for: {opening_name_or_id}")

        start_date_obj, end_date_obj = None, None
        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
            raise ValueError("Ngày kết thúc phải sau ngày bắt đầu")
        
        # Tìm opening_id từ name hoặc id bằng cosine similarity
        opening_id, matched_name, similarity_score = find_opening_id_by_name(
            opening_name_or_id, 
            BASE_API_KEY
        )
        
        if not opening_id:
            raise Exception(f"Không tìm thấy vị trí phù hợp với '{opening_name_or_id}'. Similarity score cao nhất: {similarity_score:.2f}")
        
        candidates = get_candidates_for_opening(opening_id, BASE_API_KEY, start_date_obj, end_date_obj, stage_name)
        
        # Lấy JD (Job Description)
        jds = get_job_descriptions(BASE_API_KEY, use_cache=True)
        jd = next((jd for jd in jds if jd['id'] == opening_id), None)
        
        if not jd:
            # Thử làm mới cache nếu không tìm thấy
            jds = get_job_descriptions(BASE_API_KEY, use_cache=False)
            jd = next((jd for jd in jds if jd['id'] == opening_id), None)
        
        job_description = jd['job_description'] if jd else None
        
        return {
            "success": True,
            "query": opening_name_or_id,
            "opening_id": opening_id,
            "opening_name": matched_name,
            "similarity_score": similarity_score,
            "job_description": job_description,
            "total_candidates": len(candidates),
            "candidates": candidates
        }
    except ValueError as e:
        raise Exception(f"Định dạng ngày không hợp lệ: {str(e)}")
    except Exception as e:
        raise Exception(f"Lỗi khi lấy ứng viên: {str(e)}")

@mcp.tool(
    name="get_interviews_by_opening",
    description="Tra cứu LỊCH TRÌNH phỏng vấn (Schedule/Calendar).",
    tags={"hiring", "interview", "schedule"},
    annotations={"readOnlyHint": True}
)
async def get_interviews_by_opening(
    ctx: Context,
    opening_name_or_id: Optional[str] = None,
    date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tra cứu LỊCH TRÌNH phỏng vấn (Schedule/Calendar).
    Dùng tool này để xem ai sẽ phỏng vấn vào thời gian nào.
    
    Args:
        opening_name_or_id: Tên hoặc ID của vị trí tuyển dụng để lọc. Bỏ trống để lấy tất cả.
        date: Lấy lịch phỏng vấn cho 1 ngày cụ thể (YYYY-MM-DD). Nếu có tham số này, sẽ bỏ qua start_date và end_date.
        start_date: Ngày bắt đầu lọc lịch phỏng vấn (YYYY-MM-DD). Bỏ trống để lấy tất cả.
        end_date: Ngày kết thúc lọc lịch phỏng vấn (YYYY-MM-DD). Bỏ trống để lấy tất cả.
    """
    try:
        await ctx.info(f"Fetching interviews. Opening: {opening_name_or_id}, Date: {date}")

        filter_date_obj = None
        
        # Nếu có tham số date, dùng nó để lọc dựa trên time_dt
        if date:
            filter_date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        
        opening_id = None
        matched_name = None
        similarity_score = None
        
        # Nếu có opening_name_or_id, tìm opening_id bằng cosine similarity
        if opening_name_or_id:
            opening_id, matched_name, similarity_score = find_opening_id_by_name(
                opening_name_or_id,
                BASE_API_KEY
            )
            
            if not opening_id:
                # Nếu không tìm thấy, vẫn trả về tất cả interviews nhưng có thông báo
                opening_id = None
        
        # Lấy tất cả interviews và lọc dựa trên date của time_dt
        # Nếu có date, dùng filter_date; nếu không thì dùng start_date và end_date
        interviews = get_interviews(
            BASE_API_KEY, 
            start_date=start_date if not date else None,
            end_date=end_date if not date else None,
            opening_id=opening_id, 
            filter_date=filter_date_obj
        )
        
        return {
            "success": True,
            "query": opening_name_or_id,
            "date": date,
            "start_date": start_date if not date else None,
            "end_date": end_date if not date else None,
            "similarity_score": similarity_score,
            "total_interviews": len(interviews),
            "interviews": interviews
        }
    except ValueError as e:
        raise Exception(f"Định dạng ngày không hợp lệ: {str(e)}")
    except Exception as e:
        raise Exception(f"Lỗi khi lấy lịch phỏng vấn: {str(e)}")

@mcp.tool(
    name="get_candidate_details",
    description="Lấy CHI TIẾT và PHÂN TÍCH SÂU một ứng viên cụ thể (Deep Dive).",
    tags={"hiring", "candidate", "detail"},
    annotations={"readOnlyHint": True}
)
async def get_candidate_details_tool(
    ctx: Context,
    candidate_id: Optional[List[str]] = None,
    opening_name_or_id: Optional[str] = None,
    candidate_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lấy CHI TIẾT và PHÂN TÍCH SÂU một ứng viên cụ thể.
    Dùng tool này khi bạn ĐÃ CÓ tên hoặc ID ứng viên và muốn xem toàn bộ thông tin (CV full, đánh giá chi tiết).
    
    Args:
        candidate_id: ID của ứng viên hoặc list các ID (vd: ["123", "456", "789"])
        opening_name_or_id: Tên hoặc ID của vị trí tuyển dụng (bắt buộc nếu dùng candidate_name)
        candidate_name: Tên ứng viên hoặc nhiều tên phân cách bằng dấu phẩy (vd: "Nguyen Van A,Tran Thi B")
    """
    try:
        await ctx.info(f"Fetching details for candidate_id: {candidate_id}, names: {candidate_name} in opening: {opening_name_or_id}")

        # Parse candidate IDs - chấp nhận list hoặc single string
        candidate_ids = []
        if candidate_id:
            if isinstance(candidate_id, list):
                candidate_ids = [str(cid).strip() for cid in candidate_id if cid]
            else:
                # Fallback: nếu là string, coi như single ID
                candidate_ids = [str(candidate_id).strip()]
        
        # Parse candidate names nếu có (phân cách bằng dấu phẩy)
        candidate_names = []
        if candidate_name:
            candidate_names = [name.strip() for name in candidate_name.split(',') if name.strip()]
        
        # Validate input
        if not candidate_ids and not candidate_names:
            raise Exception("Phải cung cấp ít nhất một candidate_id hoặc candidate_name")
        
        if candidate_names and not opening_name_or_id:
            raise Exception("Phải cung cấp opening_name_or_id khi tìm bằng candidate_name")
        
        # Tìm opening_id nếu có opening_name_or_id
        opening_id = None
        opening_name_matched = None
        opening_similarity = None
        
        if opening_name_or_id:
            opening_id, opening_name_matched, opening_similarity = find_opening_id_by_name(
                opening_name_or_id,
                BASE_API_KEY
            )
            
            if not opening_id:
                raise Exception(f"Không tìm thấy vị trí phù hợp với '{opening_name_or_id}'. Similarity score cao nhất: {opening_similarity:.2f}")
        
        # Tìm candidate IDs từ candidate names nếu có
        if candidate_names and opening_id:
            for name in candidate_names:
                found_id, similarity = find_candidate_by_name_in_opening(
                    name,
                    opening_id,
                    BASE_API_KEY,
                    similarity_threshold=0.5,
                    filter_stages=None
                )
                
                if found_id:
                    candidate_ids.append(found_id)
        
        if not candidate_ids:
            raise Exception("Không tìm thấy ứng viên nào phù hợp")
        
        # Lấy thông tin chi tiết cho tất cả candidates
        all_candidates_data = []
        for cid in candidate_ids:
            try:
                candidate_data = get_candidate_details(cid, BASE_API_KEY)
                
                # Trích xuất cv_text từ cv_url nếu có
                cv_url = candidate_data.get('cv_url')
                if cv_url:
                    cv_text = extract_text_from_cv_url(cv_url)
                    candidate_data['cv_text'] = cv_text
                

                
                all_candidates_data.append(candidate_data)
            except Exception as e:
                # Nếu lỗi với một candidate, bỏ qua và tiếp tục
                continue
        
        if not all_candidates_data:
            raise Exception("Không thể lấy thông tin chi tiết cho bất kỳ ứng viên nào")
        
        # Nhóm candidates theo opening_id
        openings_map = {}
        for candidate_data in all_candidates_data:
            cand_opening_id = candidate_data.get('opening_id')
            cand_opening_name = candidate_data.get('vi_tri_ung_tuyen')
            
            # Tìm opening_id nếu chỉ có opening_name
            if not cand_opening_id and cand_opening_name:
                cand_opening_id, _, _ = find_opening_id_by_name(
                    cand_opening_name,
                    BASE_API_KEY
                )
            
            # Sử dụng opening_id hoặc opening_name làm key
            opening_key = cand_opening_id or cand_opening_name or "unknown"
            
            if opening_key not in openings_map:
                openings_map[opening_key] = {
                    'opening_id': cand_opening_id,
                    'opening_name': cand_opening_name,
                    'job_description': None,
                    'candidates': []
                }
            
            # Xóa các trường thừa khỏi candidate_data để đúng format README
            candidate_data_cleaned = {
                k: v for k, v in candidate_data.items() 
                if k not in ['job_description', 'opening_id', 'vi_tri_ung_tuyen']
            }
            openings_map[opening_key]['candidates'].append(candidate_data_cleaned)
        
        # Lấy JD cho mỗi opening
        for opening_key, opening_data in openings_map.items():
            if opening_data['opening_id']:
                # Dùng hàm get_opening_content mới để lấy JD chính xác theo ID
                jd_content = get_opening_content(opening_data['opening_id'], BASE_API_KEY)
                if jd_content:
                    opening_data['job_description'] = jd_content
                else:
                    # Nếu không tìm thấy JD, thử tìm trong cache cũ (fallback)
                    jds = get_job_descriptions(BASE_API_KEY, use_cache=True)
                    jd = next((jd for jd in jds if jd['id'] == opening_data['opening_id']), None)
                    if jd:
                        opening_data['job_description'] = jd['job_description']
        
        # Chuyển đổi sang list để dễ đọc hơn
        openings_list = list(openings_map.values())
        
        result = {
            "success": True,
            "total_candidates": len(all_candidates_data),
            "total_openings": len(openings_list),
            "openings": openings_list
        }
        
        # Thêm thông tin similarity nếu tìm bằng opening name
        if opening_similarity is not None:
            result["opening_similarity_score"] = opening_similarity
        
        return result
    except Exception as e:
        raise Exception(f"Lỗi khi lấy chi tiết ứng viên: {str(e)}")

@mcp.tool(
    name="get_offer_letter",
    description="Lấy offer letter của ứng viên. Có thể tìm bằng candidate_id, hoặc bằng opening_name_or_id + candidate_name.",
    tags={"hiring", "candidate", "offer"},
    annotations={"readOnlyHint": True}
)
async def get_offer_letter_tool(
    ctx: Context,
    candidate_id: Optional[str] = None,
    opening_name_or_id: Optional[str] = None,
    candidate_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Lấy offer letter của ứng viên. Có thể tìm bằng candidate_id, hoặc bằng opening_name_or_id + candidate_name (dùng cosine similarity). 
    Trả về tên ứng viên, vị trí ứng tuyển và nội dung offer letter.
    
    Args:
        candidate_id: ID của ứng viên. Bắt buộc nếu không có opening_name_or_id và candidate_name.
        opening_name_or_id: Tên hoặc ID của vị trí tuyển dụng để tìm kiếm bằng cosine similarity. Bắt buộc nếu không có candidate_id.
        candidate_name: Tên ứng viên để tìm kiếm bằng cosine similarity trong opening. Bắt buộc nếu không có candidate_id.
    """
    try:
        await ctx.info(f"Fetching offer letter. Candidate ID: {candidate_id}, Name: {candidate_name}")

        found_candidate_id = candidate_id
        
        # Nếu không có candidate_id, tìm thông qua opening và name
        if not found_candidate_id:
            if not opening_name_or_id or not candidate_name:
                raise Exception("Phải cung cấp candidate_id, hoặc cả opening_name_or_id và candidate_name")
            
            # Tìm opening_id
            opening_id, opening_name_matched, opening_similarity = find_opening_id_by_name(
                opening_name_or_id,
                BASE_API_KEY
            )
            
            if not opening_id:
                raise Exception(f"Không tìm thấy vị trí phù hợp với '{opening_name_or_id}'.")
            
            # Tìm candidate
            found_candidate_id, candidate_similarity = find_candidate_by_name_in_opening(
                candidate_name,
                opening_id,
                BASE_API_KEY,
                similarity_threshold=0.5
            )
            
            if not found_candidate_id:
                raise Exception(f"Không tìm thấy ứng viên phù hợp với tên '{candidate_name}' trong vị trí '{opening_name_matched}'.")
        
        # Gọi helper function để lấy offer letter
        offer_data = get_offer_letter(found_candidate_id, BASE_API_KEY)
        
        if not offer_data:
            return {
                "success": False,
                "message": f"Không tìm thấy offer letter cho ứng viên ID {found_candidate_id}"
            }
            
        return {
            "success": True,
            "data": offer_data
        }

    except Exception as e:
        raise Exception(f"Lỗi khi lấy offer letter: {str(e)}")

@mcp.tool(
    name="get_server_status",
    description="Kiểm tra trạng thái Base Hiring MCP server.",
    tags={"system", "status"},
    annotations={"readOnlyHint": True}
)
async def get_server_status(ctx: Context) -> Dict[str, str]:

    """Kiểm tra trạng thái Base Hiring MCP server."""
    return {
        "status": "running",
        "server": "Base Hiring Assistant MCP Server",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    mcp.run(transport="http", port=8000)

# Base Hiring Assistant MCP Server

A powerful Model Context Protocol (MCP) server for interacting with Base.vn Hiring API and Google Sheets to manage recruitment workflows, candidate data, and test results.

## 🚀 Features

- **Job Description Management**: Retrieve job descriptions and opening details
- **Candidate Management**: Search, filter, and retrieve candidate information with CV text extraction
- **Interview Scheduling**: Manage and query interview schedules
- **Test Results Integration**: Fetch test results from Google Sheets
- **Feedback Analysis**: Retrieve and analyze candidate feedback data
- **Offer Letter Management**: Extract offer letters from candidate messages
- **Smart Search**: Cosine similarity-based fuzzy matching for openings and candidates
- **CV Text Extraction**: Automatic CV parsing using pdfplumber and Google Gemini AI
- **Caching**: Built-in 5-minute cache for improved performance

## 📋 Prerequisites

- Python 3.8+
- Base.vn API access
- Google Gemini API key (for CV text extraction)
- Google Apps Script URL (optional, for test results)
- Base Account API key (optional, for user information)

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Ehiring-API
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
# Required
BASE_API_KEY=your_base_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional backup Gemini API keys (comma-separated)
GEMINI_API_KEY_DU_PHONG=key1,key2,key3

# Optional - for test results from Google Sheets
GOOGLE_SHEET_SCRIPT_URL=your_google_apps_script_url

# Optional - for user information in reviews
ACCOUNT_API_KEY=your_account_api_key
```

## 🎯 Usage

### Running the Server

```bash
python server.py
```

The server will start and listen for MCP requests.

### Running with FastMCP

```bash
fastmcp run server.py
```

## 📚 Available Tools

### 1. `get_job_description`

Retrieve job description by opening name or ID.

**Parameters:**
- `opening_name_or_id` (optional): Opening name or ID. Leave empty to get all active openings.

**Returns:**
- Job description text
- Opening details (id, name)
- List of recruitment stages
- Similarity score (if fuzzy matched)

**Example:**
```python
{
  "opening_name_or_id": "Backend Developer"
}
```

---

### 2. `get_candidates_by_opening`

Get all candidates for a specific opening with optional filters.

**Parameters:**
- `opening_name_or_id` (required): Opening name or ID
- `start_date` (optional): Filter start date (YYYY-MM-DD)
- `end_date` (optional): Filter end date (YYYY-MM-DD)
- `stage_name` (optional): Filter by recruitment stage

**Returns:**
- List of candidates with:
  - Basic info (name, email, phone, gender)
  - CV URL and extracted CV text
  - Reviews from recruiters
  - Form data
  - Test results from Google Sheets
  - Stage information

**Example:**
```python
{
  "opening_name_or_id": "Backend Developer",
  "stage_name": "Technical Interview",
  "start_date": "2025-01-01"
}
```

---

### 3. `get_interviews_by_opening`

Retrieve interview schedules with optional filters. Filtering is done client-side based on the `time_dt` field (interview time in Asia/Ho_Chi_Minh timezone).

**Parameters:**
- `opening_name_or_id` (optional): Opening name or ID
- `date` (optional): Specific date (YYYY-MM-DD). If provided, only interviews on this exact date will be returned.
- `start_date` (optional): Filter start date (YYYY-MM-DD). Returns interviews from this date onwards.
- `end_date` (optional): Filter end date (YYYY-MM-DD). Returns interviews up to and including this date.

**Note:** If `date` is provided, it takes priority and `start_date`/`end_date` are ignored.

**Returns:**
- List of interviews with:
  - Interview ID
  - Candidate information
  - Opening name
  - Interview time (`time_dt` in ISO format, Asia/Ho_Chi_Minh timezone)

**Example:**
```python
{
  "opening_name_or_id": "Backend Developer",
  "date": "2025-11-22"
}
```

**Example with date range:**
```python
{
  "opening_name_or_id": "Backend Developer",
  "start_date": "2025-11-20",
  "end_date": "2025-11-25"
}
```

---

### 4. `get_candidate_details`

Get detailed information about one or more candidates. Supports batch queries with results grouped by opening/job position.

**Parameters:**
- `candidate_id` (optional): Direct candidate ID or list of IDs (e.g., `["123", "456", "789"]`)
- `opening_name_or_id` (optional): Opening name or ID (required if using candidate_name)
- `candidate_name` (optional): Candidate name or multiple names separated by commas (e.g., "Nguyen Van A,Tran Thi B")

**Returns:**
- Results grouped by opening/job position
- Each opening contains:
  - `opening_id`: Opening ID
  - `opening_name`: Opening name
  - `job_description`: Job description for this opening
  - `candidates`: Array of candidate details (without duplicated JD)
    - Complete candidate profile
    - Reviews with reviewer names and titles
    - All form fields (flattened)
    - Test results
    - CV text (extracted)

**Example (single candidate):**
```python
{
  "opening_name_or_id": "Backend Developer",
  "candidate_name": "Nguyen Van A"
}
```

**Example (multiple candidates by ID):**
```python
{
  "candidate_id": ["123", "456", "789"]
}
```

**Example (multiple candidates by name in one opening):**
```python
{
  "opening_name_or_id": "Backend Developer",
  "candidate_name": "Nguyen Van A,Tran Thi B,Le Van C"
}
```

**Response format:**
```json
{
  "success": true,
  "total_candidates": 3,
  "total_openings": 2,
  "openings": [
    {
      "opening_id": "9162",
      "opening_name": "Backend Developer",
      "job_description": "...",
      "candidates": [
        {
          "id": "123",
          "ten": "Nguyen Van A",
          "email": "...",
          "cv_text": "...",
          "reviews": [...],
          "test_results": [...]
        },
        {
          "id": "456",
          "ten": "Tran Thi B",
          "..."
        }
      ]
    },
    {
      "opening_id": "9163",
      "opening_name": "Frontend Developer",
      "job_description": "...",
      "candidates": [
        {
          "id": "789",
          "ten": "Le Van C",
          "..."
        }
      ]
    }
  ]
}
```

---

### 5. `get_offer_letter`

Extract offer letter from candidate messages.

**Parameters:**
- `candidate_id` (optional): Direct candidate ID
- `opening_name_or_id` (optional): Opening name or ID (required if using candidate_name)
- `candidate_name` (optional): Candidate name for fuzzy search

**Returns:**
- Offer letter text (extracted from PDF/DOCX)
- File URL and name
- Candidate and opening information

**Example:**
```python
{
  "candidate_id": "12345"
}
```

---

### 6. `get_feedback_data`

Retrieve feedback data from Google Sheets in structured format.

**Parameters:** None

**Returns:**
- Feedback data in format:
```json
{
  "success": true,
  "total_questions": 5,
  "data": {
    "Question 1 text": {
      "Candidate Name 1": "Answer 1",
      "Candidate Name 2": "Answer 2"
    },
    "Question 2 text": {
      "Candidate Name 1": "Answer 1"
    }
  }
}
```

---

### 7. `get_server_status`

Check server health and version.

**Parameters:** None

**Returns:**
```json
{
  "status": "running",
  "server": "Base Hiring Assistant MCP Server",
  "version": "1.0.0"
}
```

## 🔌 Available Resources

### `base-hiring://openings/list`

Returns a formatted list of all active job openings with their recruitment stages.

**Example Output:**
```
Danh sách các vị trí tuyển dụng đang hoạt động:

- ID: 9162, Tên: Backend Developer
  Các vòng: CV Screening, Phone Interview, Technical Test, Final Interview

- ID: 9163, Tên: Frontend Developer
  Các vòng: CV Screening, Technical Test, HR Interview
```

## 🛠️ Key Features Explained

### Smart Fuzzy Matching

The server uses TF-IDF vectorization and cosine similarity to match:
- Opening names (threshold: 0.5)
- Candidate names (threshold: 0.5)
- Stage names (threshold: 0.3)
- Test names (threshold: 0.5)

This allows flexible queries like "Backend Dev" matching "Backend Developer".

### CV Text Extraction

The server automatically extracts text from candidate CVs using:
1. **Primary**: pdfplumber (fast, local)
2. **Fallback**: Google Gemini AI (for complex PDFs)
3. **Backup API Keys**: Automatic rotation on rate limits

### Caching System

Built-in 5-minute cache for:
- Active openings list
- Job descriptions
- User information

Reduces API calls and improves response time.

### Review Processing

Automatically enriches reviews with:
- Reviewer's full name
- Reviewer's job title
- Clean text (HTML tags removed)

## 📝 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_API_KEY` | ✅ Yes | Base.vn API access token |
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for CV extraction |
| `GEMINI_API_KEY_DU_PHONG` | ❌ No | Backup Gemini API keys (comma-separated) |
| `GOOGLE_SHEET_SCRIPT_URL` | ❌ No | Google Apps Script URL for test results |
| `ACCOUNT_API_KEY` | ❌ No | Base Account API key for user info |

## 🔍 Error Handling

The server includes comprehensive error handling:
- Invalid date formats
- Missing required parameters
- API connection failures
- Rate limit handling with automatic API key rotation
- Graceful fallbacks for optional features

## 📊 Response Format

All tools return structured JSON responses with:
- `success`: Boolean indicating operation status
- `message`: Human-readable status message
- `data`: Requested data
- Additional metadata (similarity scores, counts, etc.)

## 🤝 Integration with Google Sheets

The server can integrate with Google Sheets for test results and feedback:

1. Deploy a Google Apps Script as a web app
2. Implement endpoints for:
   - `read_data` action with optional `filters`
3. Set the script URL in `GOOGLE_SHEET_SCRIPT_URL`

Expected Google Sheets columns:
- `candidate_id`
- `Tên ứng viên` (Candidate Name)
- `Tên bài test` (Test Name)
- `Score`
- `Time`
- `Link`
- `test content`
- `Công việc ứng tuyển` (Applied Position)

## 🐛 Debugging

Enable debug mode by checking logs for:
- Cache hit/miss information
- API request/response details
- Similarity matching scores
- CV extraction method used

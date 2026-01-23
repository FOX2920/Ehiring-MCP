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
- **CV Text Extraction**: Automatic CV parsing using pdfplumber
- **Caching**: Built-in 5-minute cache for improved performance

## 📋 Prerequisites

- Python 3.8+
- Base.vn API access
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

# Required - for test results from Google Sheets
GOOGLE_SHEET_SCRIPT_URL=your_google_apps_script_url

# Required - for user information in reviews
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

## ☁️ Deployment (FastMCP Cloud)

> The fastest way to deploy your MCP server

[FastMCP Cloud](https://fastmcp.cloud) is a managed platform for hosting MCP servers, built by the FastMCP team. While the FastMCP framework will always be fully open-source, we created FastMCP Cloud to solve the deployment challenges we've seen developers face. Our goal is to provide the absolute fastest way to make your MCP server available to LLM clients like Claude and Cursor.

FastMCP Cloud is a young product and we welcome your feedback. Please join our [Discord](https://discord.com/invite/aGsSC3yDF4) to share your thoughts and ideas, and you can expect to see new features and improvements every week.

> [!NOTE]
> FastMCP Cloud supports both **FastMCP 2.0** servers and also **FastMCP 1.0** servers that were created with the official MCP Python SDK.

> [!TIP]
> FastMCP Cloud is completely free while in beta!

### Prerequisites

To use FastMCP Cloud, you'll need a [GitHub](https://github.com) account. In addition, you'll need a GitHub repo that contains a FastMCP server instance. If you don't want to create one yet, you can proceed to [step 1](#step-1-create-a-project) and use the FastMCP Cloud quickstart repo.

Your repo can be public or private, but must include at least a Python file that contains a FastMCP server instance.

> [!TIP]
> To ensure your file is compatible with FastMCP Cloud, you can run `fastmcp inspect <file.py:server_object>` to see what FastMCP Cloud will see when it runs your server.

If you have a `requirements.txt` or `pyproject.toml` in the repo, FastMCP Cloud will automatically detect your server's dependencies and install them for you. Note that your file *can* have an `if __name__ == "__main__"` block, but it will be ignored by FastMCP Cloud.

For example, a minimal server file might look like:

```python
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

### Getting Started

There are just three steps to deploying a server to FastMCP Cloud:

#### Step 1: Create a Project

Visit [fastmcp.cloud](https://fastmcp.cloud) and sign in with your GitHub account. Then, create a project. Each project corresponds to a GitHub repo, and you can create one from either your own repo or using the FastMCP Cloud quickstart repo.

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=a98be26fc2265a8b74476d1747287e53" alt="FastMCP Cloud Quickstart Screen" width="800" />

Next, you'll be prompted to configure your project.

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=4c221cd0734a6fd7b634970ac0aff73a" alt="FastMCP Cloud Configuration Screen" width="800" />

The configuration screen lets you specify:

* **Name**: The name of your project. This will be used to generate a unique URL for your server.
* **Entrypoint**: The Python file containing your FastMCP server (e.g., `echo.py`). This field has the same syntax as the `fastmcp run` command, for example `echo.py:my_server` to specify a specific object in the file.
* **Authentication**: If disabled, your server is open to the public. If enabled, only other members of your FastMCP Cloud organization will be able to connect.

Note that FastMCP Cloud will automatically detect yours server's Python dependencies from either a `requirements.txt` or `pyproject.toml` file.

#### Step 2: Deploy Your Server

Once you configure your project, FastMCP Cloud will:

1. Clone the repository
2. Build your FastMCP server
3. Deploy it to a unique URL
4. Make it immediately available for connections

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=cdb7389c54a0d9d7853807b4bf996d63" alt="FastMCP Cloud Deployment Screen" width="800" />

FastMCP Cloud will monitor your repo and redeploy your server whenever you push a change to the `main` branch. In addition, FastMCP Cloud will build and deploy servers for every PR your open, hosting them on unique URLs, so you can test changes before updating your production server.

#### Step 3: Connect to Your Server

Once your server is deployed, it will be accessible at a URL like:

```
https://your-project-name.fastmcp.app/mcp
```

You should be able to connect to it as soon as you see the deployment succeed! FastMCP Cloud provides instant connection options for popular LLM clients:

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=ec716be49f8e43028eb872ff3ac95624" alt="FastMCP Cloud Connection Screen" width="800" />

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
| `BASE_API_KEY` | ✅ Yes | Access token of the Base Ehiring platform in Base.vn |
| `GOOGLE_SHEET_SCRIPT_URL` | ✅ Yes | Google Apps Script URL for test results |
| `ACCOUNT_API_KEY` | ✅ Yes | Access token of the Base Account platform in Base.vn |

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

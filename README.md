# Base Hiring Assistant MCP Server

A powerful Model Context Protocol (MCP) server for interacting with Base.vn Hiring API to manage recruitment workflows, candidate data, and interview schedules.

## 🚀 Features

- **Job Description (JD)**: Retrieve job descriptions and opening details ("Tra cứu").
- **Candidate Listing**: Search, filter, and list candidates ("Sàng lọc diện rộng").
- **Deep Dive**: Retrieve detailed candidate information including CV text and reviews ("Chi tiết & Phân tích sâu").
- **Interview Scheduling**: Manage and query interview schedules ("Lịch trình").
- **Offer Management**: Extract offer letters ("Giai đoạn Offer").
- **Smart Search**: Cosine similarity-based fuzzy matching for openings and candidates.
- **Context Awareness**: Built with FastMCP Context for enhanced logging and dependency injection.

## 📋 Prerequisites

- Python 3.10+
- Base.vn API access
- Base Account API key (optional, for user information enriched reviews)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/FOX2920/Ehiring-MCP.git
cd Ehiring-MCP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
# Required - Base Ehiring Platform Key
BASE_API_KEY=your_base_api_key_here

# Optional - For enriched reviewer info (names/titles)
ACCOUNT_API_KEY=your_account_api_key
```

## 🎯 Usage

### Running the Server

```bash
# Debug/Dev mode
python server.py

# Production mode with FastMCP
fastmcp run server.py
```

The server will start on port 8000 (HTTP transport).

## 📚 Available Tools

See [tool_guide.md](tool_guide.md) for detailed validation rules and scenarios.

### 1. `get_job_description` (TRA CỨU JD)
**Intent**: Use when you need to understand the role requirements, skills, or benefits. **DO NOT** use this to find candidates.
- **Inputs**: `opening_name_or_id` (optional).

### 2. `get_candidates_by_opening` (DANH SÁCH & SÀNG LỌC)
**Intent**: Use for **BROAD SCREENING**. Returns a list of candidates. Ideal for filtering by date (`start_date`, `end_date`) or stage (`stage_name`).
- **Inputs**: `opening_name_or_id` (Required), filters.

### 3. `get_candidate_details` (CHI TIẾT & PHÂN TÍCH SÂU)
**Intent**: Use for **DEEP DIVE** analysis. Use this when you *already have* a specific candidate in mind (ID or Name) and need their full profile, CV text, and detailed reviews.
- **Inputs**: `candidate_id` OR (`opening_name_or_id` + `candidate_name`).

### 4. `get_interviews_by_opening` (LỊCH TRÌNH)
**Intent**: Use for checking the **CALENDAR** or schedule. Who is interviewing when?
- **Inputs**: `date` (specific day) or range.

### 5. `get_offer_letter` (OFFER)
**Intent**: Use only during the **OFFER/CLOSING** stage to retrieve offer documents.
- **Inputs**: `candidate_id` OR ID/Name pair.

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_API_KEY` | ✅ Yes | Access token of the Base Ehiring platform in Base.vn |
| `ACCOUNT_API_KEY` | ⚠️ Optional | Access token of the Base Account platform (for reviewer names) |

## 🤝 Contributing

This project uses **FastMCP** for its server implementation.
- `server.py`: Main entry point.
- `tool_guide.md`: Detailed tool documentation.
- `context.md`: Guide on FastMCP Context usage.

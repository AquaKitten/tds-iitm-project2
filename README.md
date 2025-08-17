# Data Analyst Agent API

A production-ready FastAPI microservice that processes questions and attached data files using LLMs plus standard Python data science tooling.

## Usage

POST requests to `/api/` with:

- `questions.txt` (required)
- Zero or more data files (e.g., CSV)

### Example

```bash
curl "http://localhost:8000/api/" \
  -F "questions.txt=@questions.txt" \
  -F "data.csv=@mydata.csv"

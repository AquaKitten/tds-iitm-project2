# Data Analyst Agent API

A production-ready FastAPI microservice that processes questions and attached data files using LLMs plus standard Python data science tooling.

## Usage

POST requests to `/api/` with:

- `questions.txt` (required)
- Zero or more data files (e.g., CSV)

### Example

```bash
### Example

curl "http://localhost:8000/api/"
-F "questions.txt=@questions.txt"
-F "data.csv=@mydata.csv"

## Deployment

docker build -t data-analyst-agent .
docker run -e OPENAI_API_KEY=sk-... -p 8000:8000 data-analyst-age
undefined

import io
import base64
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# For environment variable-based OpenAI key setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

@app.post("/api/")
async def analyze(
    questions: UploadFile = File(...),
    files: Optional[List[UploadFile]] = File(None)
):
    # Read questions
    try:
        q_lines = (await questions.read()).decode().strip().splitlines()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid questions.txt"})
    # Load data files
    filemap = {}
    if files:
        for f in files:
            data = await f.read()
            filemap[f.filename] = data

    results = []
    for qi, q in enumerate(q_lines, 1):
        try:
            file_names = list(filemap.keys())
            context = ""
            # Example: parse CSVs
            csv_data = {n: pd.read_csv(io.BytesIO(filemap[n]))
                        for n in file_names if n.lower().endswith(".csv")}
            # Compose prompt
            prompt = f"""You are a data analyst. Task: {q}
Files attached: {file_names}
If relevant, describe your reasoning. If a plot/chart is appropriate, note that.
If input files are ambiguous or missing, answer as best as possible.
"""
            # LLM answer
            answer = ""
            try:
                resp = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    timeout=55
                )
                answer = resp.choices[0].message.content
            except Exception as e:
                answer = f"Could not generate answer via LLM: {e}"

            # Optional: Generate chart if question asks
            viz_data = None
            if ("plot" in q.lower() or "chart" in q.lower() or "visualiz" in q.lower()) and csv_data:
                try:
                    # Simple demo: first CSV scatter plot
                    df = next(iter(csv_data.values()))
                    cols = df.select_dtypes("number").columns
                    if len(cols) >= 2:
                        fig, ax = plt.subplots()
                        ax.scatter(df[cols[0]], df[cols[1]])
                        ax.set_xlabel(cols)
                        ax.set_ylabel(cols[1])
                        ax.set_title("Auto-generated scatter plot")
                        buf = io.BytesIO()
                        plt.savefig(buf, format="png"); plt.close(fig)
                        viz_data = "data:image/png;base64," + base64.b64encode(buf.getbuffer()).decode()
                except Exception:
                    viz_data = None
            
            # Confidence (fixed for demo, TODO: implement scoring function)
            conf = 0.88 if answer else 0.5

            results.append([qi, answer, conf, viz_data])
        except Exception as exc:
            results.append([qi, f"Error processing question: {exc}", 0.2, None])

    return results

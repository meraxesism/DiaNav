from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Dict
from dianav_data import parse_dtc_txt
import re

app = FastAPI()

# Load DTC index at startup
try:
    DTC_INDEX = parse_dtc_txt("SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.txt")
except FileNotFoundError:
    # Use sample data if real data not available
    DTC_INDEX = parse_dtc_txt("sample_dtc_data.txt")

class QueryRequest(BaseModel):
    query: str

def find_dtc_code_in_query(query: str):
    # Look for DTC code patterns (e.g., B1087, B155A-01, etc.)
    match = re.search(r"([A-Z][0-9A-Z]{3,}-?\d{0,2})", query)
    if match:
        return match.group(1)
    return None

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/query")
def query_dianav(request: QueryRequest):
    dtc_code = find_dtc_code_in_query(request.query)
    if dtc_code and dtc_code in DTC_INDEX:
        dtc = DTC_INDEX[dtc_code]
        conversational = f"Here is the information for DTC {dtc['dtc_code_line']}. Please see the structured details below."
        structured = dtc['full_block']
    else:
        conversational = "Sorry, I could not find a matching DTC code in your query."
        structured = "No structured data found."
    return {
        "conversational": conversational,
        "structured": structured
    }




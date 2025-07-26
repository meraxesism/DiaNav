from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from dianav_data import parse_dtc_txt, extract_image_from_pdf
import re
import os
import base64

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React development server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PDF and data file paths
PDF_PATH = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.pdf"
TXT_PATH = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.txt"
SAMPLE_PATH = "sample_dtc_data.txt"

# Load DTC index at startup with PDF for image extraction
try:
    if os.path.exists(PDF_PATH) and os.path.exists(TXT_PATH):
        DTC_INDEX = parse_dtc_txt(TXT_PATH, PDF_PATH)
        print(f"Loaded DTC data with PDF image extraction support")
    else:
        DTC_INDEX = parse_dtc_txt(SAMPLE_PATH)
        print(f"Loaded sample DTC data (PDF not available)")
except Exception as e:
    print(f"Error loading DTC data: {e}")
    DTC_INDEX = parse_dtc_txt(SAMPLE_PATH)

class QueryRequest(BaseModel):
    query: str

class ImageResponse(BaseModel):
    image_data: str
    description: str
    page_num: int

def find_dtc_code_in_query(query: str):
    # Look for DTC code patterns (e.g., B1087, B155A-01, etc.)
    match = re.search(r"([A-Z][0-9A-Z]{3,}-?\d{0,2})", query)
    if match:
        return match.group(1)
    return None

@app.get("/health")
def health_check():
    return {"status": "ok", "dtc_count": len(DTC_INDEX)}

@app.post("/query")
def query_dianav(request: QueryRequest):
    dtc_code = find_dtc_code_in_query(request.query)
    
    if dtc_code and dtc_code in DTC_INDEX:
        dtc = DTC_INDEX[dtc_code]
        conversational = f"Here is the information for DTC {dtc['dtc_code_line']}. Please see the structured details and diagnostic images below."
        structured = dtc['full_block']
        
        # Extract images if available
        images = []
        if dtc.get('images') and os.path.exists(PDF_PATH):
            for img_ref in dtc['images']:
                try:
                    # Extract image from PDF
                    image_data = extract_image_from_pdf(PDF_PATH, img_ref['page_num'])
                    if image_data:
                        images.append({
                            'image_data': image_data,
                            'description': img_ref['description'],
                            'page_num': img_ref['page_num']
                        })
                except Exception as e:
                    print(f"Error extracting image for DTC {dtc_code}: {e}")
        
        return {
            "conversational": conversational,
            "structured": structured,
            "images": images,
            "has_images": len(images) > 0
        }
    else:
        conversational = "Sorry, I could not find a matching DTC code in your query."
        structured = "No structured data found."
        return {
            "conversational": conversational,
            "structured": structured,
            "images": [],
            "has_images": False
        }

@app.get("/dtc/{dtc_code}")
def get_dtc_info(dtc_code: str):
    """Get detailed information for a specific DTC code"""
    if dtc_code in DTC_INDEX:
        dtc = DTC_INDEX[dtc_code]
        
        # Extract images if available
        images = []
        if dtc.get('images') and os.path.exists(PDF_PATH):
            for img_ref in dtc['images']:
                try:
                    image_data = extract_image_from_pdf(PDF_PATH, img_ref['page_num'])
                    if image_data:
                        images.append({
                            'image_data': image_data,
                            'description': img_ref['description'],
                            'page_num': img_ref['page_num']
                        })
                except Exception as e:
                    print(f"Error extracting image for DTC {dtc_code}: {e}")
        
        return {
            "dtc_code": dtc_code,
            "dtc_code_line": dtc['dtc_code_line'],
            "block": dtc['block'],
            "full_block": dtc['full_block'],
            "images": images,
            "image_references": dtc.get('image_references', [])
        }
    else:
        raise HTTPException(status_code=404, detail=f"DTC code {dtc_code} not found")

@app.get("/dtc-list")
def get_dtc_list():
    """Get list of all available DTC codes"""
    return {
        "dtc_codes": list(DTC_INDEX.keys()),
        "total_count": len(DTC_INDEX)
    }

@app.get("/extract-image/{page_num}")
def extract_image_from_page(page_num: int):
    """Extract image from a specific page of the PDF"""
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    try:
        image_data = extract_image_from_pdf(PDF_PATH, page_num)
        if image_data:
            return {
                "image_data": image_data,
                "page_num": page_num,
                "description": f"Diagnostic diagram from page {page_num + 1}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"No image found on page {page_num}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




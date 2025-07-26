import re
import os
import fitz  # PyMuPDF
from typing import Dict, Any, List, Optional
from PIL import Image
import io
import base64
import warnings

# SECURITY WARNING: This module handles confidential automotive diagnostic data
# All images are processed in memory only and never saved to disk

DTC_BLOCK_PATTERN = re.compile(r"DTC_Code: (.+?)\n(.*?)\n\*{10,}", re.DOTALL)
IMAGE_REF_PATTERN = re.compile(r"Image extracted from bbox: <a href='([^']+)'>Click to view image</a>")

class ImageExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        # SECURITY: No image caching to disk - all processing in memory only
        
    def open_pdf(self):
        """Open the PDF document"""
        try:
            self.doc = fitz.open(self.pdf_path)
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False
    
    def extract_image_from_page(self, page_num: int, bbox: tuple) -> Optional[str]:
        """Extract image from specific page and bounding box - IN MEMORY ONLY"""
        if not self.doc:
            return None
            
        try:
            page = self.doc[page_num]
            # Extract the image from the bounding box
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=bbox)
            img_data = pix.tobytes("png")
            
            # Convert to base64 for web display - NO DISK STORAGE
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return f"data:image/png;base64,{img_base64}"
        except Exception as e:
            print(f"Error extracting image: {e}")
            return None
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()

def parse_image_references(block: str) -> List[Dict[str, Any]]:
    """Parse image references from a DTC block"""
    images = []
    for match in IMAGE_REF_PATTERN.finditer(block):
        image_path = match.group(1)
        # Extract page number from path (e.g., page8, page11, etc.)
        page_match = re.search(r'page(\d+)', image_path)
        if page_match:
            page_num = int(page_match.group(1)) - 1  # Convert to 0-based index
            images.append({
                'path': image_path,
                'page_num': page_num,
                'description': f"Diagnostic diagram from page {page_num + 1}"
            })
    return images

def parse_dtc_txt(txt_path: str, pdf_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse the DTC .txt file and return a dict indexed by DTC code.
    Optionally extract images from PDF if provided.
    
    SECURITY: All image processing is done in memory only.
    """
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    dtc_index = {}
    image_extractor = None
    
    # Initialize image extractor if PDF is provided
    if pdf_path and os.path.exists(pdf_path):
        image_extractor = ImageExtractor(pdf_path)
        image_extractor.open_pdf()
    
    for match in DTC_BLOCK_PATTERN.finditer(content):
        dtc_code_line = match.group(1).strip()
        block = match.group(2).strip()
        
        # Extract just the DTC code (e.g., B1087, B155A-01, etc.)
        dtc_code = dtc_code_line.split()[0]
        
        # Parse image references
        images = parse_image_references(block)
        
        # Extract images from PDF if available - IN MEMORY ONLY
        extracted_images = []
        if image_extractor and images:
            for img_ref in images:
                # Images are processed in memory and never saved to disk
                extracted_images.append({
                    'description': img_ref['description'],
                    'placeholder': True,  # Indicates we need to extract from PDF
                    'page_num': img_ref['page_num']
                })
        
        dtc_index[dtc_code] = {
            'dtc_code_line': dtc_code_line,
            'block': block,
            'full_block': f"DTC_Code: {dtc_code_line}\n{block}",
            'images': extracted_images,
            'image_references': images
        }
    
    # Clean up image extractor
    if image_extractor:
        image_extractor.close()
    
    return dtc_index

def extract_image_from_pdf(pdf_path: str, page_num: int, bbox: tuple = None) -> Optional[str]:
    """
    Extract a specific image from the PDF - IN MEMORY ONLY.
    If bbox is not provided, extracts the first image found on the page.
    
    SECURITY: This function never saves images to disk.
    All processing is done in memory and returned as base64 data.
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        if bbox:
            # Extract from specific bounding box
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=bbox)
        else:
            # Extract all images from the page
            image_list = page.get_images()
            if image_list:
                # Get the first image
                img_index = 0
                xref = image_list[img_index][0]
                pix = fitz.Pixmap(doc, xref)
            else:
                return None
        
        img_data = pix.tobytes("png")
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        doc.close()
        
        # Return as data URL - NO DISK STORAGE
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error extracting image from PDF: {e}")
        return None

# SECURITY WARNING
warnings.warn(
    "This module handles confidential automotive diagnostic data. "
    "All images are processed in memory only and never saved to disk.",
    UserWarning
) 
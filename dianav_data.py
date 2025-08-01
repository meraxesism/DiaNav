import re
import os
import json
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
    def __init__(self, pdf_path: str, json_path: str = None):
        self.pdf_path = pdf_path
        self.json_path = json_path
        self.doc = None
        self.json_data = None
        # SECURITY: No image caching to disk - all processing in memory only
        
    def open_pdf(self):
        """Open the PDF document"""
        try:
            self.doc = fitz.open(self.pdf_path)
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False
    
    def load_json_data(self):
        """Load the JSON file containing bounding box coordinates"""
        if not self.json_path or not os.path.exists(self.json_path):
            return False
            
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.json_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            return False
    
    def get_image_bbox_for_node(self, node_num: str, page_num: int, image_num: str = "1") -> tuple:
        """
        Get the bounding box coordinates and label for a specific node, page, and image number.
        This function now properly handles the relationship between TXT file references and JSON data.
        """
        if not self.json_data:
            return None, None
            
        # Convert page_num to 1-based (JSON uses 1-based page numbers)
        json_page = page_num + 1
        
        # Find all image entries for this node and page
        node_images = []
        for item in self.json_data:
            if (item.get('label', '').startswith('Image, Node') and 
                item.get('nodeLabel') == f'Node {node_num}' and 
                item.get('page') == json_page):
                
                bbox = item.get('BBox')
                if bbox and len(bbox) == 4:
                    node_images.append({
                        'bbox': (bbox[0], bbox[1], bbox[2], bbox[3]),
                        'label': item.get('label', ''),
                        'id': item.get('id', 0)
                    })
        
        # Sort by ID to ensure consistent ordering
        node_images.sort(key=lambda x: x['id'])
        
        # Convert image_num to 0-based index
        try:
            image_index = int(image_num) - 1
            if 0 <= image_index < len(node_images):
                return node_images[image_index]['bbox'], node_images[image_index]['label']
        except (ValueError, IndexError):
            pass
        
        # If no exact match found, return the first image for this node/page
        if node_images:
            return node_images[0]['bbox'], node_images[0]['label']
        
        return None, None
    
    def is_valid_diagnostic_image(self, bbox: tuple, page_width: float, page_height: float, label: str = None) -> bool:
        """
        Validate if the bounding box contains a valid diagnostic image.
        Filters out logos, headers, footers, and other unwanted elements.
        """
        if not bbox or len(bbox) != 4:
            return False
            
        x0, y0, x1, y1 = bbox
        width = x1 - x0
        height = y1 - y0
        
        # DEBUG: Print details for troubleshooting
        print(f"DEBUG: Checking image - Label: {label}, BBox: {bbox}, Size: {width}x{height}")
        
        # STRICT FILTERING: Only accept elements explicitly labeled as "Image, Node X"
        if label and not label.startswith("Image, Node"):
            print(f"DEBUG: Rejected - Not labeled as Image, Node")
            return False
            
        # Skip if dimensions are too small (likely icons/logos)
        if width < 100 or height < 100:
            print(f"DEBUG: Rejected - Too small: {width}x{height}")
            return False
            
        # Skip if dimensions are too large (likely full-page headers/footers)
        if width > page_width * 0.9 or height > page_height * 0.9:
            print(f"DEBUG: Rejected - Too large: {width}x{height} vs page {page_width}x{page_height}")
            return False
            
        # Calculate aspect ratio
        aspect_ratio = width / height if height > 0 else 0
        
        # Diagnostic images should be reasonably proportioned
        if aspect_ratio < 0.3 or aspect_ratio > 2.0:
            print(f"DEBUG: Rejected - Bad aspect ratio: {aspect_ratio}")
            return False
            
        # POSITION FILTERING: 
        # - Must not be in top 10% of page (header/logo area)
        # - Must not be in bottom 10% of page (footer area)
        # - Must not be in leftmost 5% of page (margin/logo area)
        # - Must not be in rightmost 5% of page (margin area)
        if (y0 < page_height * 0.1 or 
            y1 > page_height * 0.9 or 
            x0 < page_width * 0.05 or 
            x1 > page_width * 0.95):
            print(f"DEBUG: Rejected - Bad position: y0={y0}, y1={y1}, x0={x0}, x1={x1}")
            print(f"DEBUG: Position limits: y0>{page_height*0.1}, y1<{page_height*0.9}, x0>{page_width*0.05}, x1<{page_width*0.95}")
            return False
            
        # Check if image is reasonably sized
        image_area = width * height
        page_area = page_width * page_height
        area_ratio = image_area / page_area
        
        # Should be between 5% and 60% of page area (increased from 50% to 60%)
        if area_ratio < 0.05 or area_ratio > 0.6:
            print(f"DEBUG: Rejected - Bad area ratio: {area_ratio}")
            return False
            
        print(f"DEBUG: ACCEPTED - Image passed all filters")
        return True
    
    def extract_image_from_bbox(self, page_num: int, bbox: tuple, label: str = None) -> Optional[str]:
        """Extract image from specific page and bounding box - IN MEMORY ONLY"""
        if not self.doc:
            return None
            
        try:
            page = self.doc[page_num]
            
            # Get page dimensions for validation
            page_rect = page.rect
            page_width = page_rect.width
            page_height = page_rect.height
            
            # For debugging: Extract without filtering to see what's actually there
            if label and "Node 1" in label:
                print(f"DEBUG: Extracting Node 1 image without filtering - bbox: {bbox}")
                print(f"DEBUG: Page dimensions: {page_width}x{page_height}")
            
            # For Node 1, adjust the bounding box to exclude the header area with TATA logo
            if label and "Node 1" in label:
                print(f"DEBUG: Adjusting bbox for Node 1 to exclude header")
                x0, y0, x1, y1 = bbox
                # Move the top boundary down to exclude the header area (approximately 150 pixels from top)
                # This should crop out the TATA logo while preserving more of the diagnostic image
                adjusted_bbox = (x0, max(y0, 150), x1, y1)
                print(f"DEBUG: Original bbox: {bbox}, Adjusted bbox: {adjusted_bbox}")
                bbox = adjusted_bbox
            else:
                # Validate the bounding box with label information
                if not self.is_valid_diagnostic_image(bbox, page_width, page_height, label):
                    print(f"DEBUG: Image validation failed for {label}")
                    return None
            
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
    """Parse image references from a DTC block with improved precision"""
    images = []
    
    for match in IMAGE_REF_PATTERN.finditer(block):
        image_path = match.group(1)
        
        # Extract page number from path (e.g., page8, page11, etc.)
        page_match = re.search(r'page(\d+)', image_path)
        if page_match:
            page_num = int(page_match.group(1)) - 1  # Convert to 0-based index
            
            # Extract node and image info for better identification
            # Pattern: Node 1_image2.png -> node_num=1, image_num=2
            node_match = re.search(r'Node (\d+)_image(\d+)', image_path)
            if node_match:
                node_num = node_match.group(1)
                image_num = node_match.group(2)
                
                # Only include images that are explicitly referenced in the TXT file
                # This ensures we only extract images that are meant to be shown
                images.append({
                    'path': image_path,
                    'page_num': page_num,
                    'node_num': node_num,
                    'image_num': image_num,
                    'description': f"Diagnostic diagram from page {page_num + 1}, Node {node_num} (Image {image_num})"
                })
    
    return images

def parse_dtc_txt(txt_path: str, pdf_path: Optional[str] = None, json_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse the DTC .txt file and return a dict indexed by DTC code.
    Optionally extract images from PDF if provided, using JSON bounding box data.
    
    SECURITY: All image processing is done in memory only.
    """
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    dtc_index = {}
    image_extractor = None
    
    # Initialize image extractor if PDF and JSON are provided
    if pdf_path and os.path.exists(pdf_path):
        image_extractor = ImageExtractor(pdf_path, json_path)
        image_extractor.open_pdf()
        image_extractor.load_json_data()
    
    # Find all DTC blocks
    all_matches = list(DTC_BLOCK_PATTERN.finditer(content))
    
    for match in all_matches:
        dtc_code_line = match.group(1).strip()
        block = match.group(2).strip()
        
        # Extract the full DTC code line and clean it up
        # e.g., "B155A – 01:- General Electrical Failure..." should become "B155A-01"
        
        # Fix encoding issues first
        dtc_code = dtc_code_line.replace('â', '–')  # Fix en dash encoding
        dtc_code = dtc_code.replace('–', '-')  # Convert en dash to regular dash
        
        # Handle cases where there are spaces and colons in the DTC code
        # e.g., "B155A – 01:-" should become "B155A-01"
        dtc_code = re.sub(r'\s+', '', dtc_code)  # Remove all spaces
        dtc_code = re.sub(r':-.*$', '', dtc_code)  # Remove ":--" and everything after
        dtc_code = re.sub(r':.*$', '', dtc_code)  # Remove ":" and everything after
        
        # Remove any remaining trailing punctuation or extra characters
        dtc_code = re.sub(r'[^\w\-]', '', dtc_code)
        
        # Parse image references
        images = parse_image_references(block)
        
        # Debug: Check if this is B1087 and what images we found
        if dtc_code == "B1087":
            print(f"B1087 DEBUG: Found {len(images)} image references")
            for img in images:
                print(f"B1087 DEBUG: Image ref - {img}")
            
            # Debug the extraction process for B1087
            if image_extractor and images:
                for img_ref in images:
                    print(f"B1087 DEBUG: Looking for Node {img_ref['node_num']} Image {img_ref['image_num']} on page {img_ref['page_num'] + 1}")
                    bbox, label = image_extractor.get_image_bbox_for_node(
                        img_ref['node_num'], 
                        img_ref['page_num'],
                        img_ref['image_num']
                    )
                    print(f"B1087 DEBUG: Found bbox: {bbox}, label: {label}")
                    
                    if bbox and label:
                        print(f"B1087 DEBUG: Extracting image with bbox {bbox}")
                        image_data = image_extractor.extract_image_from_bbox(
                            img_ref['page_num'], 
                            bbox,
                            label
                        )
                        if image_data:
                            print(f"B1087 DEBUG: Successfully extracted image (length: {len(image_data)})")
                        else:
                            print(f"B1087 DEBUG: Failed to extract image")
                    else:
                        print(f"B1087 DEBUG: No bbox/label found")
        
        # Extract images from PDF if available - IN MEMORY ONLY
        extracted_images = []
        
        if image_extractor and images:
            for img_ref in images:
                # Get bounding box and label from JSON data
                bbox, label = image_extractor.get_image_bbox_for_node(
                    img_ref['node_num'], 
                    img_ref['page_num'],
                    img_ref['image_num']
                )
                
                if bbox and label:
                    # Extract image using precise bounding box and label validation
                    image_data = image_extractor.extract_image_from_bbox(
                        img_ref['page_num'], 
                        bbox,
                        label
                    )
                    if image_data:
                        extracted_images.append({
                            'image_data': image_data,
                            'description': img_ref['description'],
                            'page_num': img_ref['page_num']
                        })
        
        # Store the DTC data with extracted images
        dtc_index[dtc_code] = {
            'code': dtc_code,
            'full_code': dtc_code_line,
            'content': block,
            'images': extracted_images,  # Now contains actual image data
            'image_references': images   # Keep original references for debugging
        }
    
    # Close the image extractor
    if image_extractor:
        image_extractor.close()
    
    return dtc_index

def extract_image_from_pdf(pdf_path: str, page_num: int, bbox: tuple = None) -> Optional[str]:
    """
    Legacy function for backward compatibility.
    Extracts an image from a specific page and bounding box.
    """
    try:
        doc = fitz.open(pdf_path)
        page = doc[page_num]
        
        if bbox:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=bbox)
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        
        img_data = pix.tobytes("png")
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        doc.close()
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"Error extracting image: {e}")
        return None

# SECURITY WARNING
warnings.warn(
    "This module handles confidential automotive diagnostic data. "
    "All images are processed in memory only and never saved to disk.",
    UserWarning
) 
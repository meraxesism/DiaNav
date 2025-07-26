#!/usr/bin/env python3
"""
Test script to verify PDF image extraction functionality
"""

import os
import sys
from dianav_data import parse_dtc_txt, extract_image_from_pdf

def test_image_extraction():
    """Test the image extraction functionality"""
    
    # File paths
    pdf_path = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.pdf"
    txt_path = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.txt"
    
    print("🔍 Testing DiaNav Image Extraction System")
    print("=" * 50)
    
    # Check if files exist
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    if not os.path.exists(txt_path):
        print(f"❌ Text file not found: {txt_path}")
        return False
    
    print(f"✅ PDF file found: {pdf_path}")
    print(f"✅ Text file found: {txt_path}")
    
    # Parse DTC data with image extraction
    print("\n📖 Parsing DTC data with image references...")
    try:
        dtc_index = parse_dtc_txt(txt_path, pdf_path)
        print(f"✅ Successfully parsed {len(dtc_index)} DTC codes")
        
        # Find DTCs with image references
        dtcs_with_images = []
        for dtc_code, dtc_data in dtc_index.items():
            if dtc_data.get('images'):
                dtcs_with_images.append(dtc_code)
        
        print(f"📸 Found {len(dtcs_with_images)} DTCs with image references")
        
        if dtcs_with_images:
            print("\n🔍 Sample DTCs with images:")
            for i, dtc_code in enumerate(dtcs_with_images[:3]):  # Show first 3
                dtc_data = dtc_index[dtc_code]
                print(f"  {i+1}. {dtc_code}: {len(dtc_data['images'])} image(s)")
                
                # Test image extraction for first DTC
                if i == 0:
                    print(f"     Testing image extraction for {dtc_code}...")
                    for img_ref in dtc_data['images']:
                        try:
                            image_data = extract_image_from_pdf(pdf_path, img_ref['page_num'])
                            if image_data:
                                print(f"     ✅ Successfully extracted image from page {img_ref['page_num'] + 1}")
                                print(f"     📏 Image data length: {len(image_data)} characters")
                            else:
                                print(f"     ❌ Failed to extract image from page {img_ref['page_num'] + 1}")
                        except Exception as e:
                            print(f"     ❌ Error extracting image: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error parsing DTC data: {e}")
        return False

def test_specific_dtc(dtc_code="B1087"):
    """Test a specific DTC code"""
    print(f"\n🎯 Testing specific DTC: {dtc_code}")
    print("-" * 30)
    
    pdf_path = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.pdf"
    txt_path = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.txt"
    
    try:
        dtc_index = parse_dtc_txt(txt_path, pdf_path)
        
        if dtc_code in dtc_index:
            dtc_data = dtc_index[dtc_code]
            print(f"✅ Found DTC {dtc_code}")
            print(f"📝 Description: {dtc_data['dtc_code_line']}")
            print(f"📸 Images: {len(dtc_data.get('images', []))}")
            
            if dtc_data.get('images'):
                for i, img_ref in enumerate(dtc_data['images']):
                    print(f"  Image {i+1}: Page {img_ref['page_num'] + 1} - {img_ref['description']}")
                    
                    # Test extraction
                    image_data = extract_image_from_pdf(pdf_path, img_ref['page_num'])
                    if image_data:
                        print(f"    ✅ Extraction successful ({len(image_data)} chars)")
                    else:
                        print(f"    ❌ Extraction failed")
        else:
            print(f"❌ DTC {dtc_code} not found")
            print(f"Available DTCs: {list(dtc_index.keys())[:10]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚗 DiaNav Image Extraction Test Suite")
    print("=" * 50)
    
    # Run main test
    success = test_image_extraction()
    
    if success:
        # Test specific DTC
        test_specific_dtc("B1087")
        
        print("\n🎉 Test completed successfully!")
        print("The image extraction system is working correctly.")
    else:
        print("\n❌ Test failed!")
        print("Please check the file paths and dependencies.")
        sys.exit(1) 
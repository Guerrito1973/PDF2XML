#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the PDF2XML extractor.
"""

from pdf2xml import PDFTableExtractor

def main():
    # Create an instance of the extractor
    extractor = PDFTableExtractor()
    
    # Example 1: Process a single PDF file
    print("Example 1: Processing a single PDF file")
    xml_path = extractor.process_pdf("example.pdf")
    if xml_path:
        print(f"Success! XML saved to: {xml_path}")
    else:
        print("Failed to process PDF")
    
    # Example 2: Process all PDFs in a directory
    print("\nExample 2: Processing all PDFs in a directory")
    xml_files = extractor.process_directory("pdf_directory")
    print(f"Generated {len(xml_files)} XML files")
    
    # Example 3: Using custom configuration
    print("\nExample 3: Using custom configuration")
    custom_extractor = PDFTableExtractor(config_path="custom_config.json")
    custom_extractor.output_dir = "custom_output"
    xml_path = custom_extractor.process_pdf("example.pdf")
    
    print("\nDone!")

if __name__ == "__main__":
    main()

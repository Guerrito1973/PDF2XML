#!/usr/bin/env python3
"""
PDF Table Extractor
Extracts tables from PDF files between specific section markers and converts to XML.
Handles multi-page tables while preserving row integrity.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import logging

try:
    import pdfplumber
    import pikepdf
    from lxml import etree
except ImportError as e:
    print(f"Error: Required library not installed. Please run: pip install -r requirements.txt")
    print(f"Missing: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFTableExtractor:
    """Extract tables from PDF files between section markers."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the extractor with configuration."""
        self.config = self._load_config(config_path)
        self.start_marker = self.config.get("section_start_marker", "HISTORIAL CURSOS ClÍNICOS")
        self.end_marker = self.config.get("section_end_marker", "Constantes")
        self.output_dir = self.config.get("output_directory", "output")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Config file not found: {config_path}. Using defaults.")
                return {}
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def remove_pdf_protection(self, pdf_path: str, output_path: str) -> bool:
        """
        Remove protection from PDF file using pikepdf.
        
        Args:
            pdf_path: Path to the protected PDF
            output_path: Path to save unprotected PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Removing protection from: {pdf_path}")
            with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                pdf.save(output_path)
            logger.info(f"Saved unprotected PDF to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error removing PDF protection: {e}")
            # If no protection or other issue, try to copy the file
            try:
                import shutil
                shutil.copy2(pdf_path, output_path)
                logger.info("PDF copied (may not have been protected)")
                return True
            except Exception as copy_error:
                logger.error(f"Error copying PDF: {copy_error}")
                return False
    
    def find_section_boundaries(self, pdf) -> Tuple[Optional[int], Optional[int]]:
        """
        Find the page numbers where the section starts and ends.
        
        Args:
            pdf: pdfplumber PDF object
            
        Returns:
            Tuple of (start_page_index, end_page_index) or (None, None) if not found
        """
        start_page = None
        end_page = None
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # Check for start marker
                if start_page is None and self.start_marker in text:
                    start_page = i
                    logger.info(f"Found start marker on page {i + 1}")
                
                # Check for end marker (only after start marker is found)
                if start_page is not None and self.end_marker in text:
                    end_page = i
                    logger.info(f"Found end marker on page {i + 1}")
                    break
        
        return start_page, end_page
    
    def extract_tables_from_section(self, pdf, start_page: int, end_page: Optional[int]) -> List[List[List[str]]]:
        """
        Extract tables from the specified section.
        
        Args:
            pdf: pdfplumber PDF object
            start_page: Starting page index
            end_page: Ending page index (None for end of document)
            
        Returns:
            List of tables, where each table is a list of rows
        """
        all_tables = []
        
        # Determine the range of pages to process
        if end_page is None:
            end_page = len(pdf.pages) - 1
        
        logger.info(f"Extracting tables from pages {start_page + 1} to {end_page + 1}")
        
        # Track if we're in a multi-page table
        current_table_rows = []
        
        for page_num in range(start_page, end_page + 1):
            page = pdf.pages[page_num]
            
            # Extract tables from the page
            tables = page.extract_tables()
            
            if tables:
                for table in tables:
                    if table:
                        # Clean the table (remove None values, empty rows)
                        cleaned_table = []
                        for row in table:
                            if row and any(cell for cell in row if cell):
                                # Clean each cell
                                cleaned_row = [str(cell).strip() if cell else "" for cell in row]
                                cleaned_table.append(cleaned_row)
                        
                        if cleaned_table:
                            # Check if this might be a continuation of a previous table
                            # by looking at the number of columns
                            if current_table_rows and len(cleaned_table[0]) == len(current_table_rows[-1]):
                                # Likely a continuation - append rows
                                logger.info(f"Page {page_num + 1}: Continuing table from previous page")
                                current_table_rows.extend(cleaned_table)
                            else:
                                # New table or different structure
                                if current_table_rows:
                                    all_tables.append(current_table_rows)
                                current_table_rows = cleaned_table
                                logger.info(f"Page {page_num + 1}: Found new table with {len(cleaned_table)} rows")
            else:
                # No table found on this page
                # If we have accumulated rows, this might be the end of the table
                if current_table_rows:
                    logger.info(f"Page {page_num + 1}: No table found, but have accumulated {len(current_table_rows)} rows")
        
        # Don't forget the last table
        if current_table_rows:
            all_tables.append(current_table_rows)
        
        logger.info(f"Total tables extracted: {len(all_tables)}")
        return all_tables
    
    def tables_to_xml(self, tables: List[List[List[str]]], pdf_name: str) -> etree.Element:
        """
        Convert tables to XML format.
        
        Args:
            tables: List of tables to convert
            pdf_name: Name of the source PDF file
            
        Returns:
            XML root element
        """
        root = etree.Element("document")
        root.set("source", pdf_name)
        root.set("section_start", self.start_marker)
        root.set("section_end", self.end_marker)
        
        for table_idx, table in enumerate(tables):
            table_elem = etree.SubElement(root, "table")
            table_elem.set("id", str(table_idx + 1))
            table_elem.set("rows", str(len(table)))
            
            # Assume first row is header if it exists
            if table:
                header_row = table[0]
                header_elem = etree.SubElement(table_elem, "header")
                for col_idx, cell in enumerate(header_row):
                    col_elem = etree.SubElement(header_elem, "column")
                    col_elem.set("index", str(col_idx + 1))
                    col_elem.text = cell
                
                # Process data rows
                data_elem = etree.SubElement(table_elem, "data")
                for row_idx, row in enumerate(table[1:], start=1):
                    row_elem = etree.SubElement(data_elem, "row")
                    row_elem.set("index", str(row_idx))
                    
                    for col_idx, cell in enumerate(row):
                        cell_elem = etree.SubElement(row_elem, "cell")
                        cell_elem.set("column", str(col_idx + 1))
                        if col_idx < len(header_row):
                            cell_elem.set("name", header_row[col_idx])
                        cell_elem.text = cell
        
        return root
    
    def process_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Process a single PDF file and extract tables to XML.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Path to the generated XML file or None if failed
        """
        try:
            pdf_path = Path(pdf_path).resolve()
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return None
            
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Create output directory
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Remove PDF protection
            temp_pdf = Path(self.output_dir) / f"temp_{pdf_path.name}"
            if not self.remove_pdf_protection(str(pdf_path), str(temp_pdf)):
                logger.error("Failed to remove PDF protection")
                return None
            
            # Open the unprotected PDF
            with pdfplumber.open(str(temp_pdf)) as pdf:
                logger.info(f"PDF opened successfully. Total pages: {len(pdf.pages)}")
                
                # Find section boundaries
                start_page, end_page = self.find_section_boundaries(pdf)
                
                if start_page is None:
                    logger.error(f"Start marker '{self.start_marker}' not found in PDF")
                    return None
                
                # Extract tables from the section
                tables = self.extract_tables_from_section(pdf, start_page, end_page)
                
                if not tables:
                    logger.warning("No tables found in the specified section")
                    return None
                
                # Convert to XML
                xml_root = self.tables_to_xml(tables, pdf_path.name)
                
                # Save XML file
                output_xml = Path(self.output_dir) / f"{pdf_path.stem}.xml"
                tree = etree.ElementTree(xml_root)
                tree.write(
                    str(output_xml),
                    pretty_print=True,
                    xml_declaration=True,
                    encoding='utf-8'
                )
                
                logger.info(f"XML saved to: {output_xml}")
                
                # Clean up temp file
                try:
                    temp_pdf.unlink()
                except Exception as e:
                    logger.warning(f"Could not delete temp file: {e}")
                
                return str(output_xml)
        
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}", exc_info=True)
            return None
    
    def process_directory(self, directory_path: str) -> List[str]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory_path: Path to the directory containing PDF files
            
        Returns:
            List of paths to generated XML files
        """
        directory = Path(directory_path).resolve()
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found or not a directory: {directory}")
            return []
        
        pdf_files = list(directory.glob("*.pdf")) + list(directory.glob("*.PDF"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in: {directory}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        xml_files = []
        for pdf_file in pdf_files:
            logger.info(f"\n{'='*60}")
            xml_path = self.process_pdf(str(pdf_file))
            if xml_path:
                xml_files.append(xml_path)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing complete. Generated {len(xml_files)} XML files.")
        return xml_files


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract tables from PDF files and convert to XML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single PDF file
  python pdf2xml.py input.pdf
  
  # Process all PDFs in a directory
  python pdf2xml.py --directory /path/to/pdfs
  
  # Use custom configuration
  python pdf2xml.py --config custom_config.json input.pdf
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Path to PDF file or directory (required if --directory not specified)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        help='Process all PDF files in the specified directory'
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory for XML files (overrides config)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Check if input is provided
    if not args.input and not args.directory:
        parser.print_help()
        print("\nError: Please provide either an input file or use --directory option")
        sys.exit(1)
    
    # Initialize extractor
    extractor = PDFTableExtractor(args.config)
    
    # Override output directory if specified
    if args.output:
        extractor.output_dir = args.output
    
    # Process based on input type
    try:
        if args.directory:
            # Process directory
            xml_files = extractor.process_directory(args.directory)
            if xml_files:
                print(f"\nSuccess! Generated {len(xml_files)} XML files in '{extractor.output_dir}'")
            else:
                print("\nNo XML files were generated. Check the logs for errors.")
                sys.exit(1)
        else:
            # Check if input is a file or directory
            input_path = Path(args.input)
            if input_path.is_dir():
                xml_files = extractor.process_directory(args.input)
                if xml_files:
                    print(f"\nSuccess! Generated {len(xml_files)} XML files in '{extractor.output_dir}'")
                else:
                    print("\nNo XML files were generated. Check the logs for errors.")
                    sys.exit(1)
            else:
                # Process single file
                xml_path = extractor.process_pdf(args.input)
                if xml_path:
                    print(f"\nSuccess! XML file generated: {xml_path}")
                else:
                    print("\nFailed to process PDF. Check the logs for errors.")
                    sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

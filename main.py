#!/usr/bin/env python3
"""
BookmarkMaster - A tool for optimizing and organizing browser bookmarks.
This script orchestrates the entire process from reading bookmarks to generating optimized output.
"""

import logging
from pathlib import Path
from typing import List, Dict
import json

from src.extraction.extract_bookmarks import extract_bookmarks
from src.optimization.optimize_bookmarks import BookmarkOptimizer
from src.generation.generate_html import generate_html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_bookmarks(
    input_file: Path,
    output_json: Path,
    output_html: Path,
    organized_json: Path
) -> None:
    """
    Process bookmarks through the entire pipeline:
    1. Extract bookmarks from HTML
    2. Optimize organization using domain clustering
    3. Generate organized HTML output
    """
    try:
        # Step 1: Extract bookmarks from HTML
        logger.info(f"Reading bookmarks from {input_file}")
        bookmarks = extract_bookmarks(input_file)
        logger.info(f"Extracted {len(bookmarks)} bookmarks")
        
        # Save raw bookmarks to JSON
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(bookmarks, indent=4), encoding='utf-8')
        logger.info(f"Saved raw bookmarks to {output_json}")
        
        # Step 2: Optimize bookmarks using domain clustering
        optimizer = BookmarkOptimizer(bookmarks)
        organized = optimizer.suggest_organization()
        
        # Save organized bookmarks
        organized_json.parent.mkdir(parents=True, exist_ok=True)
        organized_json.write_text(json.dumps(organized, indent=4), encoding='utf-8')
        logger.info(f"Saved organized bookmarks to {organized_json}")
        
        # Step 3: Generate HTML output
        generate_html(organized, output_html)
        logger.info(f"Generated HTML output at {output_html}")
        
        # Print summary
        print("\nProcessing Summary:")
        print("==================")
        print(f"Total Bookmarks: {len(bookmarks)}")
        print(f"Total Categories: {len(organized)}")
        print(f"Input File: {input_file}")
        print(f"Output Files:")
        print(f"  - Raw JSON: {output_json}")
        print(f"  - Organized JSON: {organized_json}")
        print(f"  - HTML: {output_html}")
        
    except Exception as e:
        logger.error(f"Error processing bookmarks: {e}")
        raise

def main() -> None:
    """Main function to run the bookmark optimization process."""
    # Define paths
    base_dir = Path(__file__).parent
    input_file = base_dir / "data/input/bookmarks_3_23_25.html"
    output_json = base_dir / "data/output/bookmarks.json"
    organized_json = base_dir / "data/output/organized_bookmarks.json"
    output_html = base_dir / "data/output/organized_bookmarks.html"
    
    # Process bookmarks
    process_bookmarks(input_file, output_json, output_html, organized_json)

if __name__ == "__main__":
    main() 
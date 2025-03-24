#!/usr/bin/env python3
"""
BookmarkMaster - A tool for optimizing and organizing browser bookmarks.
This script orchestrates the entire process from reading bookmarks to generating optimized output.
"""

import logging
from pathlib import Path
from typing import List, Dict
import json

from src.extraction.extract_bookmarks import extract_bookmarks, BookmarkStats
from src.optimization.optimize_bookmarks import BookmarkOptimizer
from src.generation.generate_html import generate_html
from config import INPUT_FILE, OUTPUT_JSON, OUTPUT_HTML, ORGANIZED_JSON

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Only show the message, no timestamp or level
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
        bookmarks = extract_bookmarks(input_file)
        
        # Calculate statistics using BookmarkStats
        stats = BookmarkStats()
        stats.calculate_statistics(bookmarks)
        original_folders = len(stats.stats['folders'])
        
        # Save raw bookmarks to JSON
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(bookmarks, indent=4), encoding='utf-8')
        
        # Step 2: Optimize bookmarks using domain clustering
        optimizer = BookmarkOptimizer(bookmarks)
        organized = optimizer.suggest_organization()
        
        # Save organized bookmarks
        organized_json.parent.mkdir(parents=True, exist_ok=True)
        organized_json.write_text(json.dumps(organized, indent=4), encoding='utf-8')
        
        # Step 3: Generate HTML output
        generate_html(organized, output_html)
        
        # Print summary
        print("\nProcessing Summary:")
        print("==================")
        print(f"Total Bookmarks: {len(bookmarks)}")
        print(f"Original Folders: {original_folders}")
        print(f"Maximum Folder Depth: {stats.stats['max_depth']}")
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
    # Process bookmarks using configuration paths
    process_bookmarks(INPUT_FILE, OUTPUT_JSON, OUTPUT_HTML, ORGANIZED_JSON)

if __name__ == "__main__":
    main() 
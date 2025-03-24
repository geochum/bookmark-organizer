#!/usr/bin/env python3
"""
HTML generation tool for organized bookmarks.
Converts organized bookmarks into a browser-compatible HTML format.
"""

import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

from config import ORGANIZED_JSON, OUTPUT_HTML

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Only show the message, no timestamp or level
)
logger = logging.getLogger(__name__)

def generate_html(organized_bookmarks: Dict, output_file: Path) -> None:
    """Generate an HTML file with the organized bookmarks."""
    try:
        # Get current timestamp
        current_timestamp = str(int(datetime.now().timestamp()))
        
        # Count bookmarks
        def count_bookmarks(folder: Dict, seen_urls: set = None) -> int:
            if seen_urls is None:
                seen_urls = set()
            
            total = 0
            # Count bookmarks in current folder
            for bookmark in folder['bookmarks']:
                url = bookmark.get('url', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    total += 1
            
            # Count bookmarks in subfolders
            for subfolder in folder['subfolders'].values():
                total += count_bookmarks(subfolder, seen_urls)
            
            return total
        
        total_bookmarks = count_bookmarks(organized_bookmarks)
        bookmarks_bar_count = len(organized_bookmarks['subfolders']['Bookmarks Bar']['bookmarks'])
        
        logger.info("\nHTML Generation Summary:")
        logger.info(f"Total Bookmarks: {total_bookmarks}")
        logger.info(f"Bookmarks in Bookmarks Bar: {bookmarks_bar_count}")
        logger.info(f"Total Folders: {len(organized_bookmarks['subfolders'])}")
        
        # Create HTML content
        html_content = """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
        """
        
        def process_folder(folder: Dict, is_bookmarks_bar: bool = False) -> str:
            """Process a folder and its contents recursively."""
            folder_html = ""
            
            # Add folder header
            if folder['name'] != "root":
                folder_html += f"""
                <DT><H3 ADD_DATE="{folder.get('add_date', current_timestamp)}" LAST_MODIFIED="{folder.get('last_modified', current_timestamp)}"{" PERSONAL_TOOLBAR_FOLDER=\"true\"" if is_bookmarks_bar else ""}>{folder['name']}</H3>
                <DL><p>
                """
            
            # Add bookmarks
            for bookmark in sorted(folder['bookmarks'], key=lambda x: x.get('title', '').lower()):
                folder_html += f"""
                <DT><A HREF="{bookmark['url']}" ADD_DATE="{bookmark.get('add_date', current_timestamp)}" LAST_MODIFIED="{bookmark.get('last_modified', current_timestamp)}" ICON="{bookmark.get('icon', '')}">{bookmark['title']}</A>
                """
            
            # Process subfolders
            for subfolder in sorted(folder['subfolders'].values(), key=lambda x: x['name'].lower()):
                folder_html += process_folder(subfolder, subfolder['name'] == "Bookmarks Bar")
            
            # Close folder
            if folder['name'] != "root":
                folder_html += "</DL><p>\n"
            
            return folder_html
        
        # Process the root folder
        html_content += process_folder(organized_bookmarks)
        
        # Close root DL
        html_content += "</DL><p>\n"
        
        # Save to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
        
    except Exception as e:
        logger.error(f"Error generating HTML: {e}")
        raise

def main() -> None:
    """Main function to generate HTML from organized bookmarks."""
    logger.info(f"Reading organized bookmarks from {ORGANIZED_JSON}")
    try:
        organized_bookmarks = json.loads(ORGANIZED_JSON.read_text())
        logger.info(f"Read organized bookmarks")
        
        # Generate HTML directly from the organized structure
        generate_html(organized_bookmarks, OUTPUT_HTML)
        
    except Exception as e:
        logger.error(f"Error generating HTML: {e}")
        raise

if __name__ == "__main__":
    main() 
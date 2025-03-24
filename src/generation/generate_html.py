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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_html(organized_bookmarks: List[Dict], output_file: Path) -> None:
    """Generate an HTML file with the organized bookmarks."""
    try:
        # Get current timestamp
        current_timestamp = str(int(datetime.now().timestamp()))
        
        # Create HTML content
        html_content = """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
        <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
        <TITLE>Bookmarks</TITLE>
        <H1>Bookmarks</H1>
        <DL><p>
        """
        
        # First add Bookmarks Bar
        html_content += f"""
        <DT><H3 ADD_DATE="{current_timestamp}" LAST_MODIFIED="{current_timestamp}" PERSONAL_TOOLBAR_FOLDER="true">Bookmarks Bar</H3>
        <DL><p>
        """
        
        # Collect unique folder paths and their bookmarks
        folder_bookmarks = {}
        unique_folder_paths = set()
        
        for bookmark in organized_bookmarks:
            folder_path = bookmark.get('folder_path', ['Uncategorized'])
            if folder_path[0] == 'Bookmarks Bar':
                if 'Bookmarks Bar' not in folder_bookmarks:
                    folder_bookmarks['Bookmarks Bar'] = []
                folder_bookmarks['Bookmarks Bar'].append(bookmark)
            else:
                # Store the full path for later use
                full_path = '/'.join(folder_path)
                unique_folder_paths.add(full_path)
                if full_path not in folder_bookmarks:
                    folder_bookmarks[full_path] = []
                folder_bookmarks[full_path].append(bookmark)
        
        # Add bookmarks in Bookmarks Bar
        if 'Bookmarks Bar' in folder_bookmarks:
            for bookmark in sorted(folder_bookmarks['Bookmarks Bar'], key=lambda x: x.get('title', '').lower()):
                html_content += f"""
                <DT><A HREF="{bookmark['url']}" ADD_DATE="{bookmark['add_date']}" LAST_MODIFIED="{bookmark['last_modified']}" ICON="{bookmark['icon']}">{bookmark['title']}</A>
                """
        html_content += """
        </DL><p>
        """
        
        # Helper function to generate HTML for nested folders
        def generate_nested_folders(folder_path: List[str], bookmarks: List[Dict], indent="    "):
            if not folder_path:
                return ""
            
            folder_html = ""
            current_folder = folder_path[0]
            
            # Add folder header with timestamps
            folder_html += f"""
            {indent}<DT><H3 ADD_DATE="{current_timestamp}" LAST_MODIFIED="{current_timestamp}">{current_folder}</H3>
            {indent}<DL><p>
            """
            
            # If this is the last folder in the path, add bookmarks
            if len(folder_path) == 1:
                for bookmark in sorted(bookmarks, key=lambda x: x.get('title', '').lower()):
                    folder_html += f"""
                    {indent}    <DT><A HREF="{bookmark['url']}" ADD_DATE="{bookmark['add_date']}" LAST_MODIFIED="{bookmark['last_modified']}" ICON="{bookmark['icon']}">{bookmark['title']}</A>
                    """
            
            folder_html += f"""
            {indent}</DL><p>
            """
            return folder_html
        
        # Process all other folders using unique paths
        for folder_path in sorted(unique_folder_paths):
            path_parts = folder_path.split('/')
            html_content += generate_nested_folders(path_parts, folder_bookmarks[folder_path])
        
        html_content += """
        </DL><p>
        """
        
        # Save to file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content, encoding='utf-8')
        logger.info(f"Generated HTML file at {output_file}")
        
    except Exception as e:
        logger.error(f"Error generating HTML: {e}")
        raise

def main() -> None:
    """Main function to generate HTML from organized bookmarks."""
    input_file = Path("data/output/organized_bookmarks.json")
    output_file = Path("data/output/organized_bookmarks.html")
    
    logger.info(f"Reading organized bookmarks from {input_file}")
    try:
        organized_bookmarks = json.loads(input_file.read_text())
        logger.info(f"Read organized bookmarks")
        
        # Generate HTML directly from the organized structure
        generate_html(organized_bookmarks, output_file)
        
    except Exception as e:
        logger.error(f"Error generating HTML: {e}")
        raise

if __name__ == "__main__":
    main() 
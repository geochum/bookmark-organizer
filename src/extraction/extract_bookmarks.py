#!/usr/bin/env python3
"""
Bookmark extraction and analysis tool.
Extracts bookmarks from an HTML file and provides detailed statistics about the bookmarks.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union, Optional
from bs4 import BeautifulSoup, Tag
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime

from config import INPUT_FILE, OUTPUT_JSON

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type aliases
BookmarkType = Dict[str, Union[str, List[str]]]
StatisticsType = Dict[str, Union[int, Set[str], defaultdict, Optional[Tuple[str, int]]]]

class BookmarkStats:
    """Class to handle bookmark statistics calculation and printing."""
    
    def __init__(self) -> None:
        self.stats: StatisticsType = {
            'total_folders': 0,
            'total_bookmarks': 0,
            'bookmarks_with_icons': 0,
            'domains': defaultdict(int),
            'folders': set(),
            'oldest_bookmark': None,
            'newest_bookmark': None,
            'folder_counts': defaultdict(int),
            'max_depth': 0
        }

    def calculate_statistics(self, bookmarks: List[BookmarkType]) -> None:
        """Calculate various statistics about the bookmarks."""
        for bookmark in bookmarks:
            if bookmark.get('type') == 'bookmark':
                self._process_bookmark(bookmark)
            
        logger.info(f"Processed {self.stats['total_bookmarks']} bookmarks in {len(self.stats['folders'])} folders")

    def _process_bookmark(self, bookmark: BookmarkType) -> None:
        """Process a single bookmark for statistics."""
        self.stats['total_bookmarks'] += 1
        
        if bookmark.get('icon'):
            self.stats['bookmarks_with_icons'] += 1
        
        # Count domains
        try:
            domain = urlparse(bookmark['url']).netloc
            self.stats['domains'][domain] += 1
        except:
            self.stats['domains']['invalid_url'] += 1
        
        # Track folder counts
        if bookmark.get('folder_path'):
            folder_path = bookmark['folder_path']
            if isinstance(folder_path, list):
                folder_path = '/'.join(folder_path)
            self.stats['folder_counts'][folder_path] += 1
            self.stats['folders'].add(folder_path)
            self.stats['max_depth'] = max(self.stats['max_depth'], 
                                        len(bookmark['folder_path']) if isinstance(bookmark['folder_path'], list) 
                                        else len(folder_path.split('/')))
        
        # Track dates
        try:
            date = int(bookmark['add_date'])
            if not self.stats['oldest_bookmark'] or date < self.stats['oldest_bookmark'][1]:
                self.stats['oldest_bookmark'] = (bookmark['title'], date)
            if not self.stats['newest_bookmark'] or date > self.stats['newest_bookmark'][1]:
                self.stats['newest_bookmark'] = (bookmark['title'], date)
        except (ValueError, TypeError, KeyError):
            pass

    def print_statistics(self) -> None:
        """Print the calculated statistics in a readable format."""
        print("\nBookmark Statistics:")
        self._print_general_stats()
        self._print_date_range()
        self._print_top_domains()
        self._print_top_folders()

    def _print_general_stats(self) -> None:
        """Print general bookmark statistics."""
        total_bookmarks = self.stats['total_bookmarks']
        print(f"Total Bookmarks: {total_bookmarks:,}")
        print(f"Total Folders: {self.stats['total_folders']:,}")
        print(f"Bookmarks with Icons: {self.stats['bookmarks_with_icons']:,} "
              f"({(self.stats['bookmarks_with_icons']/total_bookmarks*100):.1f}%)")
        print(f"Bookmarks without Icons: {total_bookmarks - self.stats['bookmarks_with_icons']:,} "
              f"({((total_bookmarks - self.stats['bookmarks_with_icons'])/total_bookmarks*100):.1f}%)")
        print(f"Maximum Folder Depth: {self.stats['max_depth']:,}")
        print(f"Total Unique Domains: {len(self.stats['domains']):,}")

    def _print_date_range(self) -> None:
        """Print bookmark date range information."""
        print("\nDate Range:")
        for bookmark_type, bookmark_info in [
            ("Oldest", self.stats['oldest_bookmark']),
            ("Newest", self.stats['newest_bookmark'])
        ]:
            if bookmark_info:
                date = datetime.fromtimestamp(bookmark_info[1])
                print(f"{bookmark_type} Bookmark: {bookmark_info[0]}")
                print(f"Added on: {date.strftime('%Y-%m-%d')}")

    def _print_top_domains(self) -> None:
        """Print top 10 domains by bookmark count."""
        print("\nTop 10 Domains:")
        sorted_domains = sorted(self.stats['domains'].items(), key=lambda x: x[1], reverse=True)
        for domain, count in sorted_domains[:10]:
            percentage = (count / self.stats['total_bookmarks']) * 100
            print(f"  {domain}: {count:,} bookmarks ({percentage:.1f}%)")

    def _print_top_folders(self) -> None:
        """Print top 10 folders by bookmark count."""
        print("\nTop 10 Folders by Number of Bookmarks:")
        sorted_folders = sorted(self.stats['folder_counts'].items(), key=lambda x: x[1], reverse=True)
        for folder, count in sorted_folders[:10]:
            percentage = (count / self.stats['total_bookmarks']) * 100
            print(f"  {folder}: {count:,} bookmarks ({percentage:.1f}%)")

def get_folder_path(entry: Tag) -> List[str]:
    """Extract the folder path for a bookmark entry."""
    folder_path = []
    current = entry
    while current:
        if current.name == 'dl':
            parent_dt = current.find_previous_sibling('dt')
            if parent_dt:
                h3 = parent_dt.find('h3')
                if h3 and h3.string:
                    folder_path.insert(0, h3.string.strip())
        current = current.parent
    return folder_path

def extract_bookmarks(input_file: Path) -> List[Dict]:
    """Extract bookmarks from an HTML file."""
    try:
        # Read the HTML file
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, "lxml")
        
        # Find all bookmark entries
        bookmark_entries = soup.find_all("dt")
        
        bookmarks = []
        for entry in bookmark_entries:
            # Skip folder entries
            if entry.find("h3"):
                continue
                
            # Get the bookmark link
            link = entry.find("a")
            if not link:
                continue
                
            # Extract bookmark data
            bookmark = {
                "title": link.get_text(),
                "url": link.get("href", ""),
                "add_date": link.get("add_date", ""),
                "last_modified": link.get("last_modified", ""),
                "icon": link.get("icon", ""),
                "folder_path": get_folder_path(entry)
            }
            
            bookmarks.append(bookmark)
        
        logger.info(f"Extracted {len(bookmarks)} bookmarks from {input_file}")
        return bookmarks
        
    except Exception as e:
        logger.error(f"Error processing bookmarks: {e}")
        raise

def main() -> None:
    """Main function to process bookmarks and generate statistics."""
    logger.info(f"Reading bookmarks from {INPUT_FILE}")
    try:
        # Extract bookmarks and gather statistics
        bookmarks = extract_bookmarks(INPUT_FILE)
        
        # Calculate and print statistics
        stats = BookmarkStats()
        stats.stats['total_folders'] = len(set(bookmark['folder_path'] for bookmark in bookmarks if isinstance(bookmark['folder_path'], list)))
        stats.stats['domains'] = defaultdict(int, {urlparse(bookmark['url']).netloc for bookmark in bookmarks if isinstance(bookmark['url'], str)})
        stats.calculate_statistics(bookmarks)
        stats.print_statistics()
        
        # Save to JSON
        OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_JSON.write_text(json.dumps(bookmarks, indent=4), encoding="utf-8")
        logger.info(f"Successfully wrote bookmarks to {OUTPUT_JSON}")
        
    except Exception as e:
        logger.error(f"Error processing bookmarks: {e}")
        raise

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Bookmark optimization tool.
Analyzes bookmarks from JSON and suggests improved organization using domain-based clustering.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from urllib.parse import urlparse
import re
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BookmarkOptimizer:
    """Class to analyze and suggest optimized bookmark organization using domain clustering."""
    
    def __init__(self, bookmarks: List[Dict]) -> None:
        self.bookmarks = bookmarks
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=1000,  # Reduced from 2000 to focus on more important terms
            token_pattern=r'(?u)\b[a-zA-Z][a-zA-Z]+\b',  # Only words with 2+ letters
            ngram_range=(1, 2),  # Include bigrams for better context
            min_df=2,  # Term must appear in at least 2 documents
            max_df=0.8  # Ignore terms that appear in more than 80% of documents
        )
        
    def _extract_domain_features(self) -> Tuple[List[str], Dict[str, List[Dict]]]:
        """Extract domain-based features from bookmarks."""
        features = []
        domain_bookmarks = defaultdict(list)
        
        for bookmark in self.bookmarks:
            url = bookmark.get('url', '')
            try:
                domain = urlparse(url).netloc
                # Remove common prefixes and suffixes
                domain = re.sub(r'^www\.|\.com$|\.org$|\.net$|\.edu$|\.gov$', '', domain)
                domain_bookmarks[domain].append(bookmark)
                
                # Create feature text from domain, title, and folder path
                title = bookmark.get('title', '')
                folder_path = ' '.join(bookmark.get('folder_path', []))
                features.append(f"{domain} {title} {folder_path}")
            except:
                # Handle invalid URLs
                features.append("")
        
        return features, domain_bookmarks
    
    def _cluster_bookmarks(self, features: List[str], n_clusters: int = 10) -> List[int]:
        """Cluster bookmarks based on domain and title similarity."""
        # Create TF-IDF vectors
        try:
            vectors = self.vectorizer.fit_transform(features)
            
            # Perform clustering with Euclidean distance
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                metric='euclidean',
                linkage='ward'
            )
            clusters = clustering.fit_predict(vectors.toarray())
            
            return clusters
        except Exception as e:
            logger.warning(f"Clustering failed: {e}. Using domain-based grouping instead.")
            return self._fallback_domain_clustering(features)
    
    def _fallback_domain_clustering(self, features: List[str]) -> List[int]:
        """Fallback method using simple domain-based grouping."""
        # Group domains by their main category
        domain_categories = {
            'google': 0, 'gmail': 0, 'youtube': 0,  # Google services
            'github': 1, 'gitlab': 1, 'bitbucket': 1,  # Code hosting
            'amazon': 2, 'ebay': 2, 'walmart': 2,  # Shopping
            'facebook': 3, 'instagram': 3, 'twitter': 3,  # Social media
            'linkedin': 4, 'indeed': 4, 'glassdoor': 4,  # Professional
            'stackoverflow': 5, 'stackexchange': 5, 'quora': 5,  # Q&A
            'reddit': 6, 'pinterest': 6, 'tumblr': 6,  # Social content
            'dropbox': 7, 'onedrive': 7, 'box': 7,  # Cloud storage
            'netflix': 8, 'spotify': 8, 'hulu': 8,  # Entertainment
            'wikipedia': 9, 'scholar': 9, 'research': 9,  # Education/Research
            'news': 10, 'reuters': 10, 'bloomberg': 10,  # News
            'weather': 11, 'maps': 11, 'calendar': 11,  # Utilities
            'bank': 12, 'paypal': 12, 'venmo': 12,  # Finance
            'health': 13, 'medical': 13, 'fitness': 13,  # Health
            'travel': 14, 'booking': 14, 'airline': 14,  # Travel
            'default': 15  # Default category
        }
        
        clusters = []
        for feature in features:
            domain = feature.split()[0] if feature else "unknown"
            # Try to find a matching category
            category = 15  # Default category
            for key, value in domain_categories.items():
                if key in domain.lower():
                    category = value
                    break
            clusters.append(category)
        
        return clusters
    
    def _generate_cluster_name(self, bookmarks: List[Dict]) -> str:
        """Generate a meaningful name for a cluster based on its bookmarks."""
        # Extract all text from titles, domains, and folder paths
        text = []
        domains = defaultdict(int)
        folder_paths = defaultdict(int)
        
        for bookmark in bookmarks:
            # Add title words
            title = bookmark.get('title', '').lower()
            text.extend(title.split())
            
            # Count domains
            try:
                domain = urlparse(bookmark.get('url', '')).netloc
                domain = re.sub(r'^www\.|\.com$|\.org$|\.net$|\.edu$|\.gov$', '', domain)
                domains[domain] += 1
            except:
                continue
            
            # Count folder paths
            for folder in bookmark.get('folder_path', []):
                folder_paths[folder.lower()] += 1
        
        # Common words to exclude
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'must', 'can', 'your', 'my', 'our', 'their', 'his', 'her', 'its', 'com',
            'org', 'net', 'edu', 'gov', 'io', 'www', 'home', 'page', 'site', 'official', 'website'
        }
        
        # Find most common words
        word_counts = defaultdict(int)
        for word in text:
            if word not in common_words and len(word) > 2:
                word_counts[word] += 1
        
        # Get top words by frequency
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Try to use folder path as category if it's common enough
        most_common_folder = max(folder_paths.items(), key=lambda x: x[1]) if folder_paths else None
        if most_common_folder and most_common_folder[1] >= len(bookmarks) * 0.4:  # If folder appears in 40% of bookmarks
            return most_common_folder[0].capitalize()
        
        if top_words:
            # Use most common word as primary category
            primary = top_words[0][0].capitalize()
            
            # Add secondary words if they're different enough and occur frequently enough
            secondary = []
            primary_count = top_words[0][1]
            for word, count in top_words[1:]:
                if (word not in primary.lower() and 
                    count >= primary_count * 0.4):  # Only include if frequency is at least 40% of primary
                    secondary.append(word.capitalize())
            
            if secondary:
                return f"{primary} & {' & '.join(secondary)}"
            return primary
        else:
            # Fallback to most common domain
            return max(domains.items(), key=lambda x: x[1])[0].capitalize() if domains else "Other"
    
    def _is_frequently_used(self, bookmark: Dict) -> bool:
        """Determine if a bookmark is frequently used based on various factors."""
        # Check if it's in the Bookmarks Bar folder
        if bookmark.get('folder_path') and 'Bookmarks bar' in bookmark['folder_path']:
            return True
            
        # Check if it's a class-related link
        title = bookmark.get('title', '').lower()
        url = bookmark.get('url', '').lower()
        class_keywords = {'canvas', 'class', 'lecture', 'homework', 'assignment', 'course', 'syllabus'}
        if any(keyword in title or keyword in url for keyword in class_keywords):
            return True
            
        # Check if it's a frequently used tool
        tool_domains = {'google.com', 'gmail.com', 'github.com', 'stackoverflow.com', 'wikipedia.org'}
        try:
            domain = urlparse(url).netloc
            if domain in tool_domains:
                return True
        except:
            pass
            
        return False

    def suggest_organization(self) -> List[Dict]:
        """Generate optimized organization that preserves original folder structure."""
        organized_bookmarks = []
        
        # Process each bookmark
        for bookmark in self.bookmarks:
            # Get the folder path
            folder_path = bookmark.get('folder_path', [])
            if not folder_path:
                folder_path = ['Uncategorized']
            
            # If it's frequently used, add to Bookmarks Bar
            if self._is_frequently_used(bookmark):
                bookmark_copy = bookmark.copy()
                bookmark_copy['folder_path'] = ['Bookmarks Bar']
                organized_bookmarks.append(bookmark_copy)
            
            # Always add to original folder structure
            bookmark_copy = bookmark.copy()
            organized_bookmarks.append(bookmark_copy)
        
        return organized_bookmarks

    def save_organization(self, organized: List[Dict], output_file: Path) -> None:
        """Save the organized bookmarks to a JSON file preserving folder structure."""
        # Save the flat list directly
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(organized, indent=4), encoding='utf-8')
        logger.info(f"Saved organized bookmarks to {output_file}")

    def print_suggestions(self, organized: List[Dict]) -> None:
        """Print the optimized bookmark organization."""
        print("\nOptimized Bookmark Organization:")
        print("==============================")
        
        # Group bookmarks by folder
        folder_bookmarks = defaultdict(list)
        for bookmark in organized:
            folder_path = bookmark.get('folder_path', ['Uncategorized'])
            folder = '/'.join(folder_path)
            folder_bookmarks[folder].append(bookmark)
        
        # Print bookmarks by folder
        for folder, bookmarks in sorted(folder_bookmarks.items()):
            print(f"\n{folder}:")
            print("-" * len(folder))
            for bookmark in sorted(bookmarks, key=lambda x: x.get('title', '').lower()):
                print(f"  - {bookmark['title']}")

def main() -> None:
    """Main function to optimize bookmark organization."""
    input_file = Path("data/output/bookmarks.json")
    output_file = Path("data/output/organized_bookmarks.json")
    
    logger.info(f"Reading bookmarks from {input_file}")
    try:
        bookmarks = json.loads(input_file.read_text())
        logger.info(f"Read {len(bookmarks)} bookmarks")
        
        # Create optimizer and generate suggestions
        optimizer = BookmarkOptimizer(bookmarks)
        organized = optimizer.suggest_organization()
        
        # Save organized bookmarks
        optimizer.save_organization(organized, output_file)
        
        # Print suggestions
        optimizer.print_suggestions(organized)
        
    except Exception as e:
        logger.error(f"Error optimizing bookmarks: {e}")
        raise

if __name__ == "__main__":
    main() 
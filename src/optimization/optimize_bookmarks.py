#!/usr/bin/env python3
"""
Bookmark optimization tool.
Analyzes bookmarks from JSON and suggests improved organization using domain-based clustering.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Union
from collections import defaultdict
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
from urllib.parse import urlparse
import re
import math

from config import (
    TFIDF_PARAMS, N_CLUSTERS, CLUSTERING_METRIC, CLUSTERING_LINKAGE,
    DOMAIN_CATEGORIES, COMMON_WORDS, FOLDER_PATH_THRESHOLD,
    SECONDARY_WORD_THRESHOLD, TOOL_DOMAINS, CLASS_KEYWORDS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Only show the message, no timestamp or level
)
logger = logging.getLogger(__name__)

class FolderNode:
    """Represents a folder in the bookmark hierarchy."""
    def __init__(self, name: str, add_date: str = "", last_modified: str = ""):
        self.name = name
        self.add_date = add_date
        self.last_modified = last_modified
        self.bookmarks: List[Dict] = []
        self.subfolders: Dict[str, FolderNode] = {}
    
    def add_bookmark(self, bookmark: Dict) -> None:
        """Add a bookmark to this folder."""
        self.bookmarks.append(bookmark)
    
    def get_subfolder(self, name: str) -> 'FolderNode':
        """Get or create a subfolder with the given name."""
        if name not in self.subfolders:
            self.subfolders[name] = FolderNode(name)
        return self.subfolders[name]
    
    def count_bookmarks(self) -> int:
        """Count total number of bookmarks in this folder and all subfolders."""
        total = len(self.bookmarks)  # Count bookmarks in current folder
        for subfolder in self.subfolders.values():
            total += subfolder.count_bookmarks()  # Add bookmarks from subfolders
        return total
    
    def count_folders(self) -> int:
        """Count total number of folders including this folder and all subfolders."""
        total = 1  # Count this folder
        for subfolder in self.subfolders.values():
            total += subfolder.count_folders()  # Add folders from subfolders
        return total
    
    def to_dict(self) -> Dict:
        """Convert the folder node to a dictionary for JSON serialization."""
        return {
            'name': self.name,
            'add_date': self.add_date,
            'last_modified': self.last_modified,
            'bookmarks': self.bookmarks,
            'subfolders': {name: folder.to_dict() for name, folder in self.subfolders.items()}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FolderNode':
        """Create a folder node from a dictionary."""
        node = cls(data['name'], data['add_date'], data['last_modified'])
        node.bookmarks = data['bookmarks']
        node.subfolders = {
            name: cls.from_dict(folder_data)
            for name, folder_data in data['subfolders'].items()
        }
        return node

class BookmarkOptimizer:
    """Class to analyze and suggest optimized bookmark organization using domain clustering."""
    
    def __init__(self, bookmarks: List[Dict]) -> None:
        self.bookmarks = bookmarks
        self.vectorizer = TfidfVectorizer(**TFIDF_PARAMS)
        
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
    
    def _cluster_bookmarks(self, features: List[str], n_clusters: int = N_CLUSTERS) -> List[int]:
        """Cluster bookmarks based on domain and title similarity."""
        # Create TF-IDF vectors
        try:
            vectors = self.vectorizer.fit_transform(features)
            
            # Perform clustering with Euclidean distance
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                metric=CLUSTERING_METRIC,
                linkage=CLUSTERING_LINKAGE
            )
            clusters = clustering.fit_predict(vectors.toarray())
            
            return clusters
        except Exception as e:
            logger.warning(f"Clustering failed: {e}. Using domain-based grouping instead.")
            return self._fallback_domain_clustering(features)
    
    def _fallback_domain_clustering(self, features: List[str]) -> List[int]:
        """Fallback method using simple domain-based grouping."""
        clusters = []
        for feature in features:
            domain = feature.split()[0] if feature else "unknown"
            # Try to find a matching category
            category = DOMAIN_CATEGORIES['default']
            for key, value in DOMAIN_CATEGORIES.items():
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
        
        # Find most common words
        word_counts = defaultdict(int)
        for word in text:
            if word not in COMMON_WORDS and len(word) > 2:
                word_counts[word] += 1
        
        # Get top words by frequency
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Try to use folder path as category if it's common enough
        most_common_folder = max(folder_paths.items(), key=lambda x: x[1]) if folder_paths else None
        if most_common_folder and most_common_folder[1] >= len(bookmarks) * FOLDER_PATH_THRESHOLD:
            return most_common_folder[0].capitalize()
        
        if top_words:
            # Use most common word as primary category
            primary = top_words[0][0].capitalize()
            
            # Add secondary words if they're different enough and occur frequently enough
            secondary = []
            primary_count = top_words[0][1]
            for word, count in top_words[1:]:
                if (word not in primary.lower() and 
                    count >= primary_count * SECONDARY_WORD_THRESHOLD):
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
        
        # Only consider class-related links if they're from specific domains
        if any(keyword in title or keyword in url for keyword in CLASS_KEYWORDS):
            try:
                domain = urlparse(url).netloc
                if domain in TOOL_DOMAINS:
                    return True
            except:
                pass
            
        # Check if it's a frequently used tool
        try:
            domain = urlparse(url).netloc
            if domain in TOOL_DOMAINS:
                return True
        except:
            pass
            
        return False

    def suggest_organization(self) -> Dict:
        """Generate optimized organization using content-based clustering."""
        # Create root folder
        root = FolderNode("root")
        bookmarks_bar = FolderNode("Bookmarks Bar")
        root.subfolders["Bookmarks Bar"] = bookmarks_bar
        
        # Track seen URLs to handle duplicates
        seen_urls = set()
        total_unique_bookmarks = 0
        
        # First pass: Extract features and prepare for clustering
        features = []
        bookmarks_to_cluster = []
        
        for bookmark in self.bookmarks:
            url = bookmark.get('url', '')
            
            # Skip if we've seen this URL before
            if url in seen_urls:
                logger.debug(f"Skipping duplicate bookmark: {bookmark.get('title', '')} ({url})")
                continue
            seen_urls.add(url)
            total_unique_bookmarks += 1
            
            # Create feature text from title, domain, and original folder path
            title = bookmark.get('title', '').lower()
            try:
                domain = urlparse(url).netloc
                domain = re.sub(r'^www\.|\.com$|\.org$|\.net$|\.edu$|\.gov$', '', domain)
            except:
                domain = ''
            
            # Add original folder path to features
            folder_path = ' '.join(bookmark.get('folder_path', []))
            
            # Create feature text
            feature_text = f"{title} {domain} {folder_path}"
            features.append(feature_text)
            bookmarks_to_cluster.append(bookmark)
        
        # Perform clustering to group similar bookmarks
        try:
            # Create TF-IDF vectors
            vectors = self.vectorizer.fit_transform(features)
            
            # Perform clustering
            clustering = AgglomerativeClustering(
                n_clusters=min(10, len(bookmarks_to_cluster)),  # Limit to 10 clusters or less
                metric=CLUSTERING_METRIC,
                linkage=CLUSTERING_LINKAGE
            )
            clusters = clustering.fit_predict(vectors.toarray())
            
            # Group bookmarks by cluster
            cluster_bookmarks = defaultdict(list)
            for bookmark, cluster_id in zip(bookmarks_to_cluster, clusters):
                cluster_bookmarks[cluster_id].append(bookmark)
            
            # Create folders based on clusters
            for cluster_id, bookmarks in cluster_bookmarks.items():
                # Generate folder name based on cluster content
                folder_name = self._generate_cluster_name(bookmarks)
                
                # Create folder and add bookmarks
                folder = root.get_subfolder(folder_name)
                for bookmark in bookmarks:
                    folder.add_bookmark(bookmark.copy())
            
        except Exception as e:
            logger.warning(f"Clustering failed: {e}. Using domain-based grouping instead.")
            # Fallback to domain-based grouping
            domain_folders = defaultdict(list)
            for bookmark in bookmarks_to_cluster:
                try:
                    domain = urlparse(bookmark.get('url', '')).netloc
                    domain = re.sub(r'^www\.|\.com$|\.org$|\.net$|\.edu$|\.gov$', '', domain)
                    domain_folders[domain].append(bookmark)
                except:
                    domain_folders['Other'].append(bookmark)
            
            # Create folders based on domains
            for domain, bookmarks in domain_folders.items():
                folder = root.get_subfolder(domain.capitalize())
                for bookmark in bookmarks:
                    folder.add_bookmark(bookmark.copy())
        
        # Second pass: Add frequently used bookmarks to Bookmarks Bar
        bookmarks_bar_urls = set()
        for bookmark in self.bookmarks:
            url = bookmark.get('url', '')
            
            # Skip if we've seen this URL in Bookmarks Bar
            if url in bookmarks_bar_urls:
                continue
                
            if self._is_frequently_used(bookmark):
                bookmarks_bar_urls.add(url)
                bookmark_copy = bookmark.copy()
                bookmarks_bar.add_bookmark(bookmark_copy)
        
        # Log summary of duplicate removal and bookmark counts
        total_bookmarks = len(self.bookmarks)
        if total_bookmarks != total_unique_bookmarks:
            logger.info(f"Removed {total_bookmarks - total_unique_bookmarks} duplicate bookmarks")
        
        # Log bookmark counts by folder
        logger.info("\nBookmark Counts:")
        logger.info(f"Total Bookmarks: {total_bookmarks}")
        logger.info(f"Unique Bookmarks: {total_unique_bookmarks}")
        logger.info(f"Bookmarks in Bookmarks Bar: {len(bookmarks_bar.bookmarks)}")
        logger.info(f"Total Folders: {root.count_folders()}")
        
        return root.to_dict()

    def save_organization(self, organized: Dict, output_file: Path) -> None:
        """Save the organized bookmarks to a JSON file preserving folder structure."""
        # Save the tree structure directly
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(organized, indent=4), encoding='utf-8')
        logger.info(f"Saved organized bookmarks to {output_file}")

    def print_suggestions(self, organized: Dict) -> None:
        """Print the optimized bookmark organization."""
        print("\nOptimized Bookmark Organization:")
        print("==============================")
        
        def print_folder(folder: Dict, level: int = 0) -> None:
            indent = "  " * level
            print(f"{indent}{folder['name']}:")
            for bookmark in sorted(folder['bookmarks'], key=lambda x: x.get('title', '').lower()):
                print(f"{indent}  - {bookmark['title']}")
            for subfolder in sorted(folder['subfolders'].values(), key=lambda x: x['name'].lower()):
                print_folder(subfolder, level + 1)
        
        print_folder(organized)

def main() -> None:
    """Main function to optimize bookmark organization."""
    from config import INPUT_FILE, OUTPUT_JSON, ORGANIZED_JSON
    
    logger.info(f"Reading bookmarks from {INPUT_FILE}")
    try:
        bookmarks = json.loads(INPUT_FILE.read_text())
        logger.info(f"Read {len(bookmarks)} bookmarks")
        
        # Create optimizer and generate suggestions
        optimizer = BookmarkOptimizer(bookmarks)
        organized = optimizer.suggest_organization()
        
        # Save organized bookmarks
        optimizer.save_organization(organized, ORGANIZED_JSON)
        
        # Print suggestions
        optimizer.print_suggestions(organized)
        
    except Exception as e:
        logger.error(f"Error optimizing bookmarks: {e}")
        raise

if __name__ == "__main__":
    main() 
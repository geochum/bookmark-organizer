"""
Configuration file for BookmarkMaster.
Contains all configurable parameters and file paths.
"""

from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent
INPUT_FILE = BASE_DIR / "data/input/bookmarks_3_23_25.html"
OUTPUT_JSON = BASE_DIR / "data/output/bookmarks.json"
ORGANIZED_JSON = BASE_DIR / "data/output/organized_bookmarks.json"
OUTPUT_HTML = BASE_DIR / "data/output/organized_bookmarks.html"

# TF-IDF Vectorizer parameters
TFIDF_PARAMS = {
    'stop_words': 'english',
    'max_features': 1000,
    'token_pattern': r'(?u)\b[a-zA-Z][a-zA-Z]+\b',
    'ngram_range': (1, 2),
    'min_df': 2,
    'max_df': 0.8
}

# Clustering parameters
N_CLUSTERS = 10
CLUSTERING_METRIC = 'euclidean'
CLUSTERING_LINKAGE = 'ward'

# Domain categories for fallback clustering
DOMAIN_CATEGORIES = {
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

# Common words to exclude from cluster naming
COMMON_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may',
    'might', 'must', 'can', 'your', 'my', 'our', 'their', 'his', 'her', 'its', 'com',
    'org', 'net', 'edu', 'gov', 'io', 'www', 'home', 'page', 'site', 'official', 'website'
}

# Thresholds
FOLDER_PATH_THRESHOLD = 0.4  # 40% threshold for folder path frequency
SECONDARY_WORD_THRESHOLD = 0.4  # 40% threshold for secondary word frequency

# Frequently used tool domains
TOOL_DOMAINS = {
    'google.com', 'gmail.com', 'github.com', 'stackoverflow.com', 'wikipedia.org'
}

# Class-related keywords
CLASS_KEYWORDS = {
    'canvas', 'class', 'lecture', 'homework', 'assignment', 'course', 'syllabus'
} 
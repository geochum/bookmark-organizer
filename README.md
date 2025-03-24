# BookmarkMaster

A Python tool that helps organize and optimize your browser bookmarks by analyzing their content and suggesting an improved structure.

## Features

- Analyzes bookmark content using TF-IDF and clustering
- Preserves original folder structure while optimizing organization
- Moves frequently used bookmarks to the Bookmarks Bar
- Generates browser-compatible HTML output
- Supports nested folder structures
- Configurable parameters for fine-tuning the optimization process

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/geochum/bookmark-organizer.git
   cd bookmark-organizer
   ```

2. Create the required directory structure:
   ```bash
   mkdir -p data/input data/output
   ```

3. Add your bookmarks file to `data/input/`
   - Export your bookmarks from your browser as HTML
   - Place the exported file in the `data/input/` directory
   - Update the `INPUT_FILE` path in `config.py` if your file has a different name

4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The tool's behavior can be customized by modifying `config.py`. Key configuration options include:

- File paths for input and output files
- TF-IDF vectorizer parameters for text analysis
- Clustering parameters for bookmark grouping
- Domain categories for fallback clustering
- Thresholds for folder path and word frequency
- Frequently used tool domains and class-related keywords

Example configuration:
```python
# TF-IDF parameters
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
```

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. The script will:
   - Process your bookmarks from the input file
   - Generate optimized organization
   - Save the results in `data/output/organized_bookmarks.json`
   - Generate a browser-compatible HTML file in `data/output/organized_bookmarks.html`

3. Import the generated HTML file back into your browser to apply the new organization

## Project Structure

```
bookmark-organizer/
├── config.py              # Configuration parameters
├── data/
│   ├── input/            # Place your input bookmarks file here
│   └── output/           # Generated files will be saved here
├── src/
│   ├── extraction/       # Bookmark extraction from HTML
│   │   └── extract_bookmarks.py
│   ├── optimization/     # Core optimization logic
│   │   └── optimize_bookmarks.py
│   └── generation/       # HTML generation
│       └── generate_html.py
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Dependencies

- Python 3.x
- scikit-learn
- numpy
- pandas
- beautifulsoup4
- lxml

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 
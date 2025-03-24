# Bookmark Organizer

A Python tool that helps organize and optimize your browser bookmarks by analyzing their content and suggesting an improved structure.

## Features

- Analyzes bookmark content using TF-IDF and clustering
- Preserves original folder structure while optimizing organization
- Moves frequently used bookmarks to the Bookmarks Bar
- Generates browser-compatible HTML output
- Supports nested folder structures

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

4. Install required Python packages:
   ```bash
   pip install -r requirements.txt
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
├── data/
│   ├── input/          # Place your input bookmarks file here
│   └── output/         # Generated files will be saved here
├── src/
│   ├── optimization/   # Core optimization logic
│   └── utils/         # Utility functions
├── main.py            # Main entry point
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Dependencies

- Python 3.x
- scikit-learn
- numpy
- pandas

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 
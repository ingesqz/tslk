# TSLK Swimming Club Records

A comprehensive system for managing and displaying swimming club records for TS&LK (Trondheim Svømmeklubb & Livredning).

## Overview

This project processes swimming competition data and generates a modern web interface to display club records, statistics, and best performances across all events and categories.

## Features

- **Club Records Display**: Shows top 10 results for each swimming event
- **Best Swimmers Overview**: Displays top performers across all events
- **Multi-language Support**: Norwegian and English interfaces
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Filtering**: Filter by event and gender
- **Modern UI**: Clean, professional design matching TSLK branding

## Project Structure

```
KRAI/
├── www/                    # Web interface files
│   ├── index.html         # Main website (generated)
│   ├── generate_website.py # Website generator script
│   └── logo.png           # TSLK logo
├── EndResult/             # Processed competition data (top 10 results)
├── Statistics/            # Complete statistics data
├── Rawdata/              # Raw competition data from medley.no
└── *.py                  # Data processing scripts
```

## Data Sources

- **medley.no**: Primary source for competition results
- **Manual entries**: Historical data not available in medley.no
- **FINA-2024**: Points calculation system

## Setup and Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ingesqz/tslk.git
   cd tslk
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate the website**:
   ```bash
   cd www
   python3 generate_website.py
   ```

4. **Run the local server**:
   ```bash
   python3 -m http.server 8000
   ```

5. **Open in browser**: Navigate to `http://localhost:8000`

## Usage

### Website Interface

- **Default View**: Shows top 10 best swimmers (men and women) across all events
- **Event Filtering**: Select specific events to view detailed results
- **Gender Filtering**: Filter by men's or women's results
- **Navigation**: Click the TSLK logo to return to the best swimmers overview

### Data Processing

- **Update Results**: Add new competition data to the `Rawdata/` folder
- **Process Data**: Run processing scripts to update statistics
- **Regenerate Website**: Run `generate_website.py` to update the web interface

## Technical Details

- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Backend**: Python 3.x with pandas for data processing
- **Data Format**: Excel files (.xlsx) for structured data storage
- **Responsive Design**: Mobile-first approach with modern CSS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Contact

For questions or issues related to the swimming club records:
- Email: ingesqz@gmail.com
- Club: TS&LK (Trondheim Svømmeklubb & Livredning)

## License

This project is maintained by TS&LK for internal club use.

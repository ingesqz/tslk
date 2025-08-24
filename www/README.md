# TSLK - Klubbrekorder Website

This website displays swimming club records for TSLK (Trondheim Svømmeklubb) with bilingual support for Norwegian and English, plus comprehensive statistics.

## Features

- **Bilingual Support**: Norwegian (default) and English languages
- **Language Switcher**: Easy toggle between languages in the header
- **Interactive Filtering**: Filter results by Event, Pool Length, and Gender
- **Required Selections**: All three filters must be selected before results are shown
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Results update automatically when filters change
- **Last Updated Information**: Shows when the data was last updated
- **Statistics Page**: Comprehensive overview with charts and analytics based on ALL data
- **Performance Optimized**: Website displays top 10 results for fast loading, statistics use complete datasets

## Files

- `index.html` - The main records page (shows top 10 results)
- `statistics.html` - Comprehensive statistics and analytics page (based on all data)
- `logo.png` - TSLK logo
- `generate_website.py` - Script to regenerate the website from Excel data

## Data Structure

The system uses two sets of Excel files for optimal performance and comprehensive analytics:

### Display Files (`../EndResult/`)
- **Purpose**: Fast website display
- **Content**: Top 10 results per category (Male 25m, Male 50m, Female 25m, Female 50m)
- **Performance**: Optimized for quick loading and responsive user experience
- **Usage**: Used by the main website for filtered results

### Statistics Files (`../Statistics/`)
- **Purpose**: Comprehensive analytics and statistics
- **Content**: ALL available data per category
- **Accuracy**: Complete datasets for accurate statistical analysis
- **Usage**: Used by the statistics page for charts, graphs, and detailed breakdowns

## How to Update

1. **Update the data**: Run the main processing script to update both display and statistics files
   ```bash
   python3 process_all_events.py
   ```
   This creates:
   - `EndResult/*.xlsx` files (top 10 for display)
   - `Statistics/*_statistics.xlsx` files (all data for statistics)

2. **Regenerate the website**: Run the website generation script
   ```bash
   python3 www/generate_website.py
   ```
   Or use the convenience script:
   ```bash
   python3 update_website.py
   ```

3. **The website will automatically**: 
   - Load top 10 data from the EndResult folder for fast display
   - Load all data from the Statistics folder for comprehensive statistics
   - Get the latest update time from grdRanking files
   - Generate both index.html and statistics.html files

## Usage

### Records Page (index.html)
1. Open `index.html` in a web browser
2. **Choose language**: Use the language switcher (Norsk/English) in the header
3. **Navigate**: Use the navigation buttons to switch between Records and Statistics
4. **Select all three filters** to see results:
   - **Øvelse/Event**: Choose a specific event (required)
   - **Basseng/Pool**: Choose 25m or 50m pool (required)
   - **Kjønn/Gender**: Choose Menn/Men or Kvinner/Women swimmers (required)
5. **Results will only appear** after all three filters are selected
6. Results display in tables showing **top 10 performers**:
   - Rank (#)
   - Name (Navn/Name)
   - Time (Tid/Time)
   - Points (Poeng/Points)
   - Date (Dato/Date)
   - Location (Sted/Location)

### Statistics Page (statistics.html)
1. Click "Statistikk" button in the header or open `statistics.html` directly
2. **Overview Cards**: See total events, swimmers, and gender distribution (based on ALL data)
3. **Participation Chart**: Bar chart showing participation by event (complete datasets)
4. **Pool Distribution**: Comparison of 25m vs 50m pool usage (all swimmers)
5. **Gender Distribution**: Pie chart showing male vs female participation (complete data)
6. **Detailed Table**: Complete breakdown by event, pool, and gender (all participants)

## Statistics Features

### Summary Statistics (Based on ALL Data)
- **Total Events**: Number of swimming events available
- **Total Swimmers**: Total number of unique swimmers across all events (6,392+ swimmers)
- **Male/Female Count**: Gender distribution of all participants

### Visual Analytics (Complete Datasets)
- **Participation by Event**: Bar chart showing most popular events (all participants)
- **Pool Distribution**: Comparison of 25m vs 50m pool usage (complete data)
- **Gender Distribution**: Pie chart showing male vs female ratio (all swimmers)

### Detailed Breakdown (All Participants)
- **Event-by-Event Analysis**: Complete table with all statistics
- **Pool and Gender Split**: Detailed breakdown for each category
- **Sorted by Popularity**: Events ranked by total participation

## Performance Benefits

### Website Display (Top 10)
- **Fast Loading**: Only 10 results per category load quickly
- **Responsive**: Smooth user experience with instant filtering
- **Mobile Friendly**: Optimized for smaller screens and slower connections
- **Efficient**: Minimal data transfer for better performance

### Statistics Page (All Data)
- **Comprehensive**: Complete picture of club participation
- **Accurate**: Real statistics based on all available data
- **Detailed**: Full breakdowns and analytics
- **Insightful**: Better understanding of club activities and trends

## Language Support

### Norwegian (Default)
- **Title**: TSLK - Klubbrekorder / TSLK - Statistikk
- **Filters**: Øvelse, Basseng, Kjønn
- **Options**: Alle øvelser, Alle basseng, Alle kjønn, Menn, Kvinner
- **Table Headers**: Navn, Tid, Poeng, Dato, Sted
- **Messages**: Norwegian error and instruction messages

### English
- **Title**: TSLK - Club Records / TSLK - Statistics
- **Filters**: Event, Pool, Gender
- **Options**: All events, All pools, All genders, Men, Women
- **Table Headers**: Name, Time, Points, Date, Location
- **Messages**: English error and instruction messages

## Technical Details

- **Data Source**: 
  - Display: Excel files in the `../EndResult/` folder (top 10)
  - Statistics: Excel files in the `../Statistics/` folder (all data)
- **Update Time**: Automatically detects the latest modification time from grdRanking files
- **Responsive**: CSS media queries ensure good display on all devices
- **No Server Required**: Works as a static website
- **Filter Logic**: All three filters must be selected for results to display
- **Language System**: Client-side JavaScript with translation objects
- **Accessibility**: Proper HTML lang attributes for screen readers
- **Charts**: CSS-based visualizations (no external dependencies)

## Browser Compatibility

- Chrome, Firefox, Safari, Edge (modern versions)
- Mobile browsers (iOS Safari, Chrome Mobile) 
import pandas as pd
import os
import json
from datetime import datetime
import glob

def get_file_creation_date(file_path):
    """Get the creation date of a file."""
    stat = os.stat(file_path)
    return datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M')

def load_all_results():
    """Load all results from Excel files in EndResult folder (top 10 for website display)."""
    all_data = {}
    
    # Get all Excel files in EndResult folder
    endresult_folder = os.path.join("..", "EndResult")
    if not os.path.exists(endresult_folder):
        print(f"EndResult folder not found: {endresult_folder}")
        return {}
    
    excel_files = glob.glob(os.path.join(endresult_folder, "*.xlsx"))
    
    for file_path in excel_files:
        try:
            # Get event name from filename
            event_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(file_path)
            event_data = {}
            
            for sheet_name in excel_file.sheet_names:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert DataFrame to list of dictionaries for JSON serialization
                if not df.empty:
                    data_list = df.to_dict('records')
                    event_data[sheet_name] = data_list
                    
                    # Print summary for debugging
                    print(f"Loaded {event_name}: {len(data_list)} {sheet_name}")
                else:
                    event_data[sheet_name] = []
                    print(f"Loaded {event_name}: 0 {sheet_name}")
            
            all_data[event_name] = event_data
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    return all_data

def load_statistics_data():
    """Load all results from Statistics folder (all data for statistics page)."""
    all_data = {}
    
    # Get all Excel files in Statistics folder
    statistics_folder = os.path.join("..", "Statistics")
    if not os.path.exists(statistics_folder):
        print(f"Statistics folder not found: {statistics_folder}")
        return {}
    
    excel_files = glob.glob(os.path.join(statistics_folder, "*_statistics.xlsx"))
    
    for file_path in excel_files:
        try:
            # Get event name from filename (remove _statistics suffix)
            event_name = os.path.splitext(os.path.basename(file_path))[0].replace("_statistics", "")
            
            # Read all sheets from the Excel file
            excel_file = pd.ExcelFile(file_path)
            event_data = {}
            
            for sheet_name in excel_file.sheet_names:
                # Read the sheet
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Convert DataFrame to list of dictionaries for JSON serialization
                if not df.empty:
                    data_list = df.to_dict('records')
                    event_data[sheet_name] = data_list
                else:
                    event_data[sheet_name] = []
            
            all_data[event_name] = event_data
            
        except Exception as e:
            print(f"Error loading statistics file {file_path}: {e}")
            continue
    
    return all_data

def get_latest_file_date():
    """Get the latest modification date from grdRanking files."""
    rawdata_folder = "../Rawdata"
    grd_files = glob.glob(os.path.join(rawdata_folder, "grdRanking*.xlsx"))
    
    if not grd_files:
        return datetime.now().strftime('%d.%m.%Y')
    
    # Filter out temporary files (starting with ~$) to ensure correct date
    grd_files = [f for f in grd_files if not os.path.basename(f).startswith('~$')]
    
    if not grd_files:
        return datetime.now().strftime('%d.%m.%Y')
    
    # Get the latest modification time (more reliable than creation time)
    latest_time = max(os.path.getmtime(f) for f in grd_files)
    return datetime.fromtimestamp(latest_time).strftime('%d.%m.%Y')

def generate_statistics_page(statistics_data, latest_date):
    """Generate a statistics page with comprehensive data overview."""
    
    # Calculate statistics
    total_events = len(statistics_data)
    total_swimmers = 0
    event_stats = {}
    pool_stats = {'25m': 0, '50m': 0}
    gender_stats = {'Male': 0, 'Female': 0}
    
    for event_name, event_data in statistics_data.items():
        event_total = 0
        event_male_25m = len(event_data.get('Male_25m', []))
        event_male_50m = len(event_data.get('Male_50m', []))
        event_female_25m = len(event_data.get('Female_25m', []))
        event_female_50m = len(event_data.get('Female_50m', []))
        
        event_total = event_male_25m + event_male_50m + event_female_25m + event_female_50m
        total_swimmers += event_total
        
        event_stats[event_name] = {
            'total': event_total,
            'male_25m': event_male_25m,
            'male_50m': event_male_50m,
            'female_25m': event_female_25m,
            'female_50m': event_female_50m
        }
        
        pool_stats['25m'] += event_male_25m + event_female_25m
        pool_stats['50m'] += event_male_50m + event_female_50m
        gender_stats['Male'] += event_male_25m + event_male_50m
        gender_stats['Female'] += event_female_25m + event_female_50m
    
    # Sort events using the same logic as the main page
    def sort_events(event_name):
        """Sort events by length first, then by type in specified order."""
        # Extract length (number before 'm')
        import re
        length_match = re.search(r'(\d+)m', event_name)
        if length_match:
            length = int(length_match.group(1))
        else:
            length = 0
        
        # Define type order (lower number = higher priority)
        type_order = {
            'butterfly': 1,
            'rygg': 2,
            'bryst': 3,
            'fri': 4,
            'medley': 5
        }
        
        # Find the type in the event name
        event_lower = event_name.lower()
        event_type = 6  # Default for unknown types
        
        for type_name, order in type_order.items():
            if type_name in event_lower:
                event_type = order
                break
        
        return (length, event_type)
    
    # Sort events by length and type (same as main page)
    sorted_events = sorted(event_stats.items(), key=lambda x: sort_events(x[0]))
    
    # Create top 10 lists across all events and pools
    all_male_results = []
    all_female_results = []
    
    for event_name, event_data in statistics_data.items():
        # Add male results
        for category in ['Male_25m', 'Male_50m']:
            if category in event_data:
                for result in event_data[category]:
                    result_copy = result.copy()
                    result_copy['Event'] = event_name
                    result_copy['Pool'] = '25m' if category == 'Male_25m' else '50m'
                    all_male_results.append(result_copy)
        
        # Add female results
        for category in ['Female_25m', 'Female_50m']:
            if category in event_data:
                for result in event_data[category]:
                    result_copy = result.copy()
                    result_copy['Event'] = event_name
                    result_copy['Pool'] = '25m' if category == 'Female_25m' else '50m'
                    all_female_results.append(result_copy)
    
    # Sort by points (highest first) and take top 10
    all_male_results.sort(key=lambda x: x.get('Poeng', 0), reverse=True)
    all_female_results.sort(key=lambda x: x.get('Poeng', 0), reverse=True)
    
    top_10_male = all_male_results[:10]
    top_10_female = all_female_results[:10]
    
    stats_html = f"""<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSLK - Statistikk</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }}
        
        .header {{
            background: #52a2d6;
            color: white;
            padding: 20px 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 15px;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            position: relative;
        }}
        
        .logo {{
            width: 80px;
            height: 80px;
            object-fit: contain;
            border: 3px solid #52a2d6;
            border-radius: 10px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 300;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .nav-buttons {{
            position: absolute;
            top: 0;
            right: 20px;
            display: flex;
            gap: 10px;
        }}
        
        .nav-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            text-decoration: none;
            transition: all 0.3s;
        }}
        
        .nav-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .stats-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #52a2d6;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            font-size: 1.1em;
            color: #666;
            font-weight: 600;
        }}
        
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .chart-title {{
            font-size: 1.5em;
            font-weight: 600;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .bar-chart {{
            height: 300px;
            display: flex;
            align-items: end;
            gap: 4px;
            padding: 20px 0 40px 0;
            overflow-x: auto;
            min-width: 100%;
        }}
        
        .bar {{
            flex: 1;
            background: #52a2d6;
            border-radius: 4px 4px 0 0;
            position: relative;
            min-width: 25px;
        }}
        
        .bar-label {{
            position: absolute;
            bottom: -35px;
            left: 50%;
            transform: translateX(-50%) rotate(-45deg);
            font-size: 0.7em;
            color: #666;
            white-space: nowrap;
            transform-origin: center;
        }}
        
        .bar-value {{
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.9em;
            font-weight: bold;
            color: #52a2d6;
        }}
        
        .pie-chart {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            margin: 0 auto;
            position: relative;
            background: conic-gradient(
                #52a2d6 0deg {gender_stats['Male'] / (gender_stats['Male'] + gender_stats['Female']) * 360}deg,
                #ff6b6b {gender_stats['Male'] / (gender_stats['Male'] + gender_stats['Female']) * 360}deg 360deg
            );
        }}
        
        .pie-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #333;
        }}
        
        .pie-legend {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }}
        
        .top-results-grid {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .top-results-table {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .points-cell {{
            font-weight: bold;
            color: #52a2d6;
        }}
        
        .events-table {{
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .table-header {{
            background: #52a2d6;
            color: white;
            padding: 15px 20px;
            font-size: 1.2em;
            font-weight: 600;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .total-cell {{
            font-weight: bold;
            color: #52a2d6;
        }}
        
        .last-updated {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-style: italic;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        @media (max-width: 768px) {{
            .header-content {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .nav-buttons {{
                position: static;
                margin-top: 10px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
            
            .top-results-grid {{
                flex-direction: column;
            }}
            
            .bar-chart {{
                height: 150px;
            }}
            
            th, td {{
                padding: 8px 10px;
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <img src="logo.png" alt="TSLK Logo" class="logo">
            <h1>TS&LK - Statistikk</h1>
            <div class="nav-buttons">
                <a href="index.html" class="nav-btn">Rekorder</a>
                <a href="statistics.html" class="nav-btn">Statistikk</a>
            </div>
        </div>
    </div>
    
    <div class="stats-container">
        <!-- Summary Statistics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_swimmers}</div>
                <div class="stat-label">Totalt Svømmere</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{gender_stats['Male']}</div>
                <div class="stat-label">Menn</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{gender_stats['Female']}</div>
                <div class="stat-label">Kvinner</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="chart-container">
            <div class="chart-title">Deltakelse per Øvelse</div>
            <div class="bar-chart">
                {''.join(f'''
                <div class="bar" style="height: {min(180, event[1]['total'] / max([e[1]['total'] for e in sorted_events]) * 180)}px">
                    <div class="bar-value">{event[1]['total']}</div>
                    <div class="bar-label">{event[0]}</div>
                </div>''' for event in sorted_events)}
            </div>
        </div>
        

        
        <!-- Top 10 Results Tables -->
        <div class="top-results-grid">
            <div class="top-results-table">
                <div class="table-header">Topp 10 resultat - uansett øvelse og basseng - Menn</div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Navn</th>
                            <th>Øvelse</th>
                            <th>Basseng</th>
                            <th>Tid</th>
                            <th>Poeng</th>
                            <th>Dato</th>
                            <th>Sted</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''
                        <tr>
                            <td>{i+1}</td>
                            <td>{result.get('Name', '')}</td>
                            <td>{result.get('Event', '')}</td>
                            <td>{result.get('Pool', '')}</td>
                            <td>{result.get('Tid', '')}</td>
                            <td class="points-cell">{result.get('Poeng', '')}</td>
                            <td>{result.get('Dato', '')}</td>
                            <td>{result.get('Sted', '')}</td>
                        </tr>''' for i, result in enumerate(top_10_male))}
                    </tbody>
                </table>
            </div>
            
            <div class="top-results-table">
                <div class="table-header">Topp 10 resultat - uansett øvelse og basseng - Kvinner</div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Navn</th>
                            <th>Øvelse</th>
                            <th>Basseng</th>
                            <th>Tid</th>
                            <th>Poeng</th>
                            <th>Dato</th>
                            <th>Sted</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(f'''
                        <tr>
                            <td>{i+1}</td>
                            <td>{result.get('Name', '')}</td>
                            <td>{result.get('Event', '')}</td>
                            <td>{result.get('Pool', '')}</td>
                            <td>{result.get('Tid', '')}</td>
                            <td class="points-cell">{result.get('Poeng', '')}</td>
                            <td>{result.get('Dato', '')}</td>
                            <td>{result.get('Sted', '')}</td>
                        </tr>''' for i, result in enumerate(top_10_female))}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Events Table -->
        <div class="events-table">
            <div class="table-header">Detaljert Oversikt per Øvelse</div>
            <table>
                <thead>
                    <tr>
                        <th>Øvelse</th>
                        <th>Menn 25m</th>
                        <th>Menn 50m</th>
                        <th>Kvinner 25m</th>
                        <th>Kvinner 50m</th>
                        <th>Totalt</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''
                    <tr>
                        <td>{event[0]}</td>
                        <td>{event[1]['male_25m']}</td>
                        <td>{event[1]['male_50m']}</td>
                        <td>{event[1]['female_25m']}</td>
                        <td>{event[1]['female_50m']}</td>
                        <td class="total-cell">{event[1]['total']}</td>
                    </tr>''' for event in sorted_events)}
                </tbody>
            </table>
        </div>
        
        <div class="last-updated">
            Sist oppdatert: {latest_date}
        </div>
    </div>
</body>
</html>"""
    
    return stats_html

def generate_html():
    """Generate the HTML file."""
    # Load data for website display (top 10)
    all_data = load_all_results()
    
    # Load data for statistics (all data)
    statistics_data = load_statistics_data()
    
    latest_date = get_latest_file_date()
    
    # Get unique events and sort them by length and type
    events = list(all_data.keys())
    
    def sort_events(event_name):
        """Sort events by length first, then by type in specified order."""
        # Extract length (number before 'm')
        import re
        length_match = re.search(r'(\d+)m', event_name)
        if length_match:
            length = int(length_match.group(1))
        else:
            length = 0
        
        # Define type order (lower number = higher priority)
        type_order = {
            'butterfly': 1,
            'rygg': 2,
            'bryst': 3,
            'fri': 4,
            'medley': 5
        }
        
        # Find the type in the event name
        event_lower = event_name.lower()
        event_type = 6  # Default for unknown types
        
        for type_name, order in type_order.items():
            if type_name in event_lower:
                event_type = order
                break
        
        return (length, event_type)
    
    # Sort events by length and type
    events.sort(key=sort_events)
    
    # Generate main page
    html_content = f"""<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TSLK - Klubbrekorder</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #ffffff;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .header {{
            background: #ffffff;
            color: #2c3e50;
            padding: 20px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .logo {{
            height: 70px;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        
        .header h1 {{
            font-size: 1.45em;
            font-weight: 600;
            color: #2c3e50;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            line-height: 1.25;
        }}
        
        .main-title-updated {{
            font-size: 0.75em;
            font-weight: 400;
            color: #6c757d;
            margin-top: 2px;
        }}
        
        .header-subtext {{
            font-size: 1em;
            color: #6c757d;
            line-height: 1.6;
            max-width: 100%;
        }}
        
        .read-more-link, .read-less-link {{
            color: #007bff;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .read-more-link:hover, .read-less-link:hover {{
            text-decoration: underline;
        }}
        
        .header-main {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            position: relative;
        }}
        
        .header h1 {{
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            text-align: center;
        }}
        
        .language-switcher {{
            display: flex;
            gap: 4px;
            position: absolute;
            top: 10px;
            right: 10px;
        }}
        
        .flag-btn {{
            background: none;
            border: 1px solid #dee2e6;
            padding: 4px 6px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 16px;
            line-height: 1;
        }}
        
        .flag-btn:hover {{
            border-color: #007bff;
            transform: scale(1.1);
        }}
        
        .flag-btn.active {{
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
        }}
        

        
        .nav-buttons {{
            display: flex;
            gap: 15px;
        }}
        
        .nav-btn {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            color: #6c757d;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
            text-decoration: none;
            transition: all 0.2s;
        }}
        
        .nav-btn:hover {{
            background: #e9ecef;
            border-color: #adb5bd;
        }}
        
        .filters {{
            background: #f8f9fa;
            padding: 15px;
            margin: 0 auto 20px;
            max-width: 1200px;
            border-radius: 0 0 8px 8px;
            border: 1px solid #e9ecef;
            border-top: none;
            display: flex;
            gap: 20px;
            align-items: center;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: row;
            gap: 10px;
            align-items: center;
        }}
        
        .filter-group label {{
            font-weight: 600;
            color: #495057;
            font-size: 0.9em;
            white-space: nowrap;
        }}
        
        .filter-group select {{
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 0.9em;
            background: white;
            transition: border-color 0.2s, box-shadow 0.2s;
            min-width: 180px;
        }}
        
        .filter-group select:focus {{
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
        }}
        
        .radio-group {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}
        
        .radio-label {{
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 0.9em;
            color: #495057;
            transition: color 0.2s;
        }}
        
        .radio-label:hover {{
            color: #007bff;
        }}
        
        .radio-label input[type="radio"] {{
            margin: 0;
            cursor: pointer;
            accent-color: #007bff;
        }}
        
        .radio-text {{
            font-weight: 500;
        }}
        
        .checkbox-group {{
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}
        
        .checkbox-label {{
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            font-size: 0.9em;
            color: #495057;
            transition: color 0.2s;
        }}
        
        .checkbox-label:hover {{
            color: #007bff;
        }}
        
        .checkbox-label input[type="checkbox"] {{
            margin: 0;
            cursor: pointer;
            accent-color: #007bff;
        }}
        
        .checkbox-text {{
            font-weight: 500;
        }}
        
        .filter-show-label {{
            font-weight: 600;
            color: #495057;
            font-size: 0.9em;
            white-space: nowrap;
        }}
        
        .filter-group-gender {{
            flex: 1;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        .view-tabs-container {{
            max-width: 1200px;
            margin: 20px auto 0;
            padding: 0 20px;
        }}
        
        .view-tabs {{
            display: flex;
            gap: 0;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px 8px 0 0;
            overflow: hidden;
        }}
        
        .view-tab {{
            flex: 1;
            padding: 12px 16px;
            border: none;
            background: transparent;
            font-size: 0.95em;
            font-weight: 600;
            color: #495057;
            cursor: pointer;
            transition: background-color 0.2s, color 0.2s;
        }}
        
        .view-tab:hover {{
            background: #e9ecef;
        }}
        
        .view-tab.active {{
            background: white;
            color: #007bff;
            box-shadow: inset 0 -2px 0 #007bff;
        }}
        
        .table-pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 16px;
            padding: 12px 16px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
        }}
        
        .pagination-btn {{
            padding: 6px 14px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            background: white;
            color: #495057;
            font-size: 0.85em;
            cursor: pointer;
        }}
        
        .pagination-btn:hover:not(:disabled) {{
            background: #e9ecef;
        }}
        
        .pagination-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .pagination-info {{
            font-size: 0.85em;
            color: #6c757d;
        }}
        
        th.sortable {{
            cursor: pointer;
            user-select: none;
        }}
        
        th.sortable:hover {{
            background-color: #e9ecef;
        }}
        
        .sort-indicator {{
            margin-left: 4px;
            color: #007bff;
        }}
        
        .event-link {{
            background: none;
            border: none;
            padding: 0;
            color: #007bff;
            font: inherit;
            cursor: pointer;
            text-align: left;
        }}
        
        .event-link:hover {{
            text-decoration: underline;
        }}
        
        .results-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .results-table {{
            background: white;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        
        .table-header {{
            background: #495057;
            color: white;
            padding: 12px 16px;
            font-size: 1em;
            font-weight: 700;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .table-header-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            font-weight: 700;
        }}
        
        .table-header-title > span:first-child {{
            color: white;
            font-weight: 700;
        }}
        
        .table-header > span {{
            color: white;
            font-weight: 700;
        }}
        
        .info-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            border: 1.5px solid rgba(255, 255, 255, 0.75);
            font-size: 11px;
            font-weight: 700;
            font-style: italic;
            line-height: 1;
            cursor: help;
            position: relative;
            flex-shrink: 0;
            color: white;
        }}
        
        .info-icon::before {{
            content: 'i';
        }}
        
        .info-icon::after {{
            content: attr(data-tooltip);
            position: absolute;
            top: calc(100% + 8px);
            left: 50%;
            transform: translateX(-50%);
            width: max-content;
            max-width: 280px;
            white-space: normal;
            padding: 10px 12px;
            background: #212529;
            color: white;
            font-size: 0.75rem;
            font-weight: 400;
            font-style: normal;
            line-height: 1.4;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.15s ease, visibility 0.15s ease;
            z-index: 10;
            pointer-events: none;
        }}
        
        .info-icon:hover::after,
        .info-icon:focus::after {{
            opacity: 1;
            visibility: visible;
        }}
        
        .table-content {{
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #495057;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .rank {{
            width: 60px;
            text-align: center;
            font-weight: 600;
            color: #007bff;
        }}
        

        
        .last-updated {{
            font-size: 0.85em;
            color: #6c757d;
            font-style: italic;
            text-align: center;
            padding: 15px;
            border-top: 1px solid #e9ecef;
            background: #f8f9fa;
        }}
        
        .no-data {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
            font-style: italic;
            background: #f8f9fa;
            border-radius: 8px;
            margin: 20px 0;
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 15px 10px;
            }}
            
            .header-content {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .header-main {{
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
            }}
            
            .header h1 {{
                font-size: 1.1em;
                text-align: center;
                margin: 0;
                flex: 1;
            }}
            
            .logo {{
                width: 60px;
                height: 60px;
            }}
            
            .language-switcher {{
                position: static;
                margin-top: 5px;
            }}
            
            .flag-btn {{
                font-size: 14px;
                padding: 3px 5px;
            }}
            
            .header-subtext {{
                font-size: 0.9em;
                line-height: 1.4;
                padding: 0 10px;
            }}
            
            .filters {{
                flex-direction: column;
                align-items: stretch;
                gap: 15px;
                padding: 15px 10px;
                margin: 15px auto;
            }}
            
            .filter-group {{
                width: 100%;
            }}
            
            .filter-group select {{
                width: 100%;
                padding: 12px;
                font-size: 1em;
            }}
            
            .radio-group {{
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }}
            
            .view-tabs-container {{
                padding: 0 10px;
                margin-top: 15px;
            }}
            
            .view-tab {{
                padding: 10px 12px;
                font-size: 0.9em;
            }}
            
            .checkbox-group {{
                flex-direction: column;
                gap: 10px;
                align-items: flex-start;
            }}
            
            .radio-label {{
                font-size: 1em;
                padding: 8px 0;
            }}
            
            .results-container {{
                padding: 0 10px;
            }}
            
            .results-table {{
                margin-bottom: 15px;
                border-radius: 6px;
            }}
            
            .table-header {{
                padding: 10px 12px;
                font-size: 0.8em;
                flex-direction: column;
                gap: 5px;
                text-align: center;
            }}
            
            .table-header span:last-child {{
                font-size: inherit;
            }}
            
            .table-content {{
                overflow-x: auto;
            }}
            
            table {{
                font-size: 0.8em;
                min-width: 600px;
            }}
            
            th, td {{
                padding: 8px 6px;
                font-size: 0.8em;
            }}
            
            .rank {{
                width: 40px;
            }}
            
            .points {{
                width: 60px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .header-main {{
                flex-direction: row;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
            }}
            
            .header h1 {{
                font-size: 0.85em;
                text-align: center;
                margin: 0;
                flex: 1;
            }}
            
            .logo {{
                width: 50px;
                height: 50px;
            }}
            
            .filters {{
                padding: 10px;
                margin: 10px auto;
            }}
            
            .filter-group select {{
                padding: 10px;
                font-size: 0.9em;
            }}
            
            .table-header {{
                padding: 8px 10px;
                font-size: 0.75em;
            }}
            
            table {{
                font-size: 0.75em;
                min-width: 500px;
            }}
            
            th, td {{
                padding: 6px 4px;
                font-size: 0.75em;
            }}
            
            .rank {{
                width: 35px;
            }}
            
            .points {{
                width: 50px;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-main">
                <img src="logo.png" alt="TSLK Logo" class="logo">
                <h1 id="mainTitle">
                    <span id="mainTitleText">Klubbrekorder TS&LK</span>
                    <span class="main-title-updated" id="mainTitleUpdated">Sist oppdatert {latest_date}</span>
                </h1>
                <div class="nav-buttons">
                    <!-- Logo click will return to best swimmers view -->
                </div>
                <div class="language-switcher">
                    <button class="flag-btn active" onclick="changeLanguage('no')" title="Norsk">🇳🇴</button>
                    <button class="flag-btn" onclick="changeLanguage('en')" title="English">🇬🇧</button>
                </div>
            </div>
            <div class="header-subtext" id="headerSubtext">
                <span class="subtext-short">Denne oversikten viser TS&LK's klubbrekorder i svømming gjennom tidene. <a href="#" class="read-more-link" onclick="toggleSubtext(event)">Les mer</a></span>
                <span class="subtext-full" style="display: none;">Denne oversikten viser TS&LK's klubbrekorder i svømming gjennom tidene. Dataene er hentet fra medley.no og i tillegg er det lagt til noen eldre manuelle oppføringer som medley.no ikke har registrert. Tidene som vises på utøverene må være fra når de har representert TS&LK. Jeg vil forsøke å oppdatere listen 1-2 ganger årlig basert på ferske resultater i Medley - jeg kommer ikke til å legge inn ferske resultater, da må du vente på neste oppdatering. Dersom noen mener at noe er feil, gamle oppføringer som mangler etc. så send meg en mail på ingesqz@gmail.com. Poengene er basert på FINA 2024. <a href="#" class="read-less-link" onclick="toggleSubtext(event)">Les mindre</a></span>
            </div>
        </div>
    </div>
    
    <div class="view-tabs-container" id="viewTabsContainer">
        <div class="view-tabs">
            <button type="button" class="view-tab active" id="tabRecords">Klubbrekorder</button>
            <button type="button" class="view-tab" id="tabLatest">Nyeste registreringer</button>
        </div>
    </div>
    
    <div class="filters" id="recordsFilters">
        <div class="filter-group">
            <select id="eventSelect">
                <option value="" id="allEvents">Velg øvelse</option>
                {''.join(f'<option value="{event}">{event}</option>' for event in events)}
            </select>
        </div>
        
        <div class="filter-group">
            <div class="radio-group">
                <label class="radio-label">
                    <input type="radio" name="gender" value="Male" id="maleOption" checked>
                    <span class="radio-text">Menn</span>
                </label>
                <label class="radio-label">
                    <input type="radio" name="gender" value="Female" id="femaleOption">
                    <span class="radio-text">Kvinner</span>
                </label>
            </div>
        </div>
    </div>
    
    <div class="filters" id="latestFilters" style="display: none;">
        <span class="filter-show-label" id="latestShowLabel">Vis</span>
        <div class="filter-group">
            <div class="checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="latestMale" checked>
                    <span class="checkbox-text" id="latestMaleLabel">Menn</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="latestFemale" checked>
                    <span class="checkbox-text" id="latestFemaleLabel">Kvinner</span>
                </label>
            </div>
        </div>
        
        <div class="filter-group">
            <div class="checkbox-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="latestPool25" checked>
                    <span class="checkbox-text">25m</span>
                </label>
                <label class="checkbox-label">
                    <input type="checkbox" id="latestPool50" checked>
                    <span class="checkbox-text">50m</span>
                </label>
            </div>
        </div>
    </div>
    
    <div class="results-container" id="resultsContainer">
        <!-- Results will be populated by JavaScript -->
    </div>

    <script>
        // Data from Python
        const allData = {json.dumps(all_data)};
        const events = {json.dumps(events)};
        
        // Event name translations
        const eventTranslations = {{
            no: {{
                "50m Butterfly": "50m Butterfly",
                "50m Rygg": "50m Rygg",
                "50m Bryst": "50m Bryst",
                "50m Fri": "50m Fri",
                "100m Butterfly": "100m Butterfly",
                "100m Rygg": "100m Rygg",
                "100m Bryst": "100m Bryst",
                "100m Fri": "100m Fri",
                "100m Medley": "100m Medley",
                "200m Butterfly": "200m Butterfly",
                "200m Rygg": "200m Rygg",
                "200m Bryst": "200m Bryst",
                "200m Fri": "200m Fri",
                "200m Medley": "200m Medley",
                "400m Fri": "400m Fri",
                "400m Medley": "400m Medley",
                "800m Fri": "800m Fri",
                "1500m Fri": "1500m Fri"
            }},
            en: {{
                "50m Butterfly": "50m Butterfly",
                "50m Rygg": "50m Backstroke",
                "50m Bryst": "50m Breaststroke",
                "50m Fri": "50m Freestyle",
                "100m Butterfly": "100m Butterfly",
                "100m Rygg": "100m Backstroke",
                "100m Bryst": "100m Breaststroke",
                "100m Fri": "100m Freestyle",
                "100m Medley": "100m Medley",
                "200m Butterfly": "200m Butterfly",
                "200m Rygg": "200m Backstroke",
                "200m Bryst": "200m Breaststroke",
                "200m Fri": "200m Freestyle",
                "200m Medley": "200m Medley",
                "400m Fri": "400m Freestyle",
                "400m Medley": "400m Medley",
                "800m Fri": "800m Freestyle",
                "1500m Fri": "1500m Freestyle"
            }}
        }};
        
        const latestUpdateDate = '{latest_date}';
        
        // Translations
        const translations = {{
            no: {{
                mainTitle: "Klubbrekorder",
                mainTitleUpdated: "Sist oppdatert",
                headerSubtextShort: "Denne oversikten viser TS&LK's beste resultater i svømming gjennom tidene.",
                headerSubtextFull: "Denne oversikten viser TS&LK's beste resultater i svømming gjennom tidene. Dataene er hentet fra medley.no og i tillegg er det lagt til noen eldre manuelle oppføringer som medley.no ikke har registrert. Tidene som vises på utøverene må være fra når de har representert TS&LK. Jeg vil forsøke å oppdatere listen 1-2 ganger årlig basert på ferske resultater i Medley - jeg kommer ikke til å legge inn ferske resultater, da må du vente på neste oppdatering. Dersom noen mener at noe er feil, gamle oppføringer som mangler etc. så send meg en mail på ingesqz@gmail.com. Poengene er basert på FINA 2024.",
                readMore: "Les mer",
                readLess: "Les mindre",
                eventLabel: "Øvelse:",
                genderLabel: "Kjønn:",
                allEvents: "Velg øvelse",
                allGenders: "Velg kjønn",
                maleOption: "Menn",
                femaleOption: "Kvinner",
                rankHeader: "#",
                nameHeader: "Navn",
                eventHeader: "Øvelse",
                poolHeader: "Basseng",
                posHeader: "Pos",
                timeHeader: "Tid",
                pointsHeader: "Poeng",
                dateHeader: "Dato",
                locationHeader: "Sted",
                men: "Menn",
                women: "Kvinner",
                top10Men: "Beste resultater - Menn",
                top10Women: "Beste resultater - Kvinner",
                top10InfoTooltip: "Denne tabellen viser de 10 resultatene med høyest FINA poeng, uavhengig av øvelse og bane. FINA poengene regnes ut i fra verdensrekorden og er derfor sammenlignbare på tvers av øvelser.",
                tabRecords: "Klubbrekorder",
                tabLatest: "Nyeste registreringer",
                showLabel: "Vis",
                latestRegistrations: "Nyeste registreringer",
                latestRegistrationsInfoTooltip: "Denne tabellene viser alle registreringer i alle øvelser. Tabellene er sortert på dato utøveren satt rekorden slik at de nyeste innlagte registreringene vises øverst.",
                prevPage: "Forrige",
                nextPage: "Neste",
                pageLabel: "Side",
                pageOf: "av",
                lastUpdated: "Sist oppdatert",
                filterMessage: "Vennligst velg både øvelse og kjønn for å se resultater.",
                noResultsMessage: "Ingen resultater funnet for de valgte filtrene."
            }},
            en: {{
                mainTitle: "Club Records",
                mainTitleUpdated: "Last updated",
                headerSubtextShort: "This overview shows TS&LK's swimming club records through time.",
                headerSubtextFull: "This overview shows TS&LK's swimming club records through time. The data is retrieved from medley.no and in addition some older manual entries that medley.no has not registered have been added. The times shown for the athletes must be from when they represented TS&LK. I will try to update the list 1-2 times annually based on fresh results in Medley - I will not add fresh results, then you must wait for the next update. If anyone thinks something is wrong, old entries are missing etc. then send me an email at ingesqz@gmail.com. The points are based on FINA 2024.",
                readMore: "Read more",
                readLess: "Read less",
                eventLabel: "Event:",
                genderLabel: "Gender:",
                allEvents: "Select event",
                allGenders: "Select gender",
                maleOption: "Men",
                femaleOption: "Women",
                rankHeader: "#",
                nameHeader: "Name",
                eventHeader: "Event",
                poolHeader: "Pool",
                posHeader: "Pos",
                timeHeader: "Time",
                pointsHeader: "Points",
                dateHeader: "Date",
                locationHeader: "Location",
                men: "Men",
                women: "Women",
                top10Men: "Best results - Men",
                top10Women: "Best results - Women",
                top10InfoTooltip: "This table shows the 10 results with the highest FINA points, regardless of event and pool. FINA points are calculated from the world record and are therefore comparable across events.",
                tabRecords: "Club Records",
                tabLatest: "Latest registrations",
                showLabel: "Show",
                latestRegistrations: "Latest registrations",
                latestRegistrationsInfoTooltip: "This table shows all registrations across all events. The table is sorted by the date the swimmer set the record, so the most recently added registrations appear at the top.",
                prevPage: "Previous",
                nextPage: "Next",
                pageLabel: "Page",
                pageOf: "of",
                lastUpdated: "Last updated",
                filterMessage: "Please select both event and gender to see results.",
                noResultsMessage: "No results found for the selected filters."
            }}
        }};
        
        let currentLanguage = 'no';
        let viewMode = 'records';
        let latestRegistrationsPage = 1;
        let latestSortColumn = 'Dato';
        let latestSortDirection = 'desc';
        
        function updateMainTitle(lang) {{
            document.getElementById('mainTitleText').textContent =
                `${{translations[lang].mainTitle}} TS&LK`;
            document.getElementById('mainTitleUpdated').textContent =
                `${{translations[lang].mainTitleUpdated}} ${{latestUpdateDate}}`;
        }}
        
        function parseDate(dateStr) {{
            if (!dateStr) return new Date(0);
            const parts = String(dateStr).split('.');
            if (parts.length !== 3) return new Date(0);
            const [day, month, year] = parts.map(Number);
            return new Date(year, month - 1, day);
        }}
        
        function parseTime(timeStr) {{
            if (!timeStr) return Infinity;
            const str = String(timeStr).trim();
            if (str.includes('.')) {{
                const [mins, secs] = str.split('.');
                return parseInt(mins, 10) * 60 + parseFloat(secs.replace(',', '.'));
            }}
            return parseFloat(str.replace(',', '.'));
        }}
        
        function getSortIndicator(column) {{
            if (latestSortColumn !== column) return '';
            return `<span class="sort-indicator">${{latestSortDirection === 'asc' ? '↑' : '↓'}}</span>`;
        }}
        
        function sortLatestRegistrations(results) {{
            const multiplier = latestSortDirection === 'asc' ? 1 : -1;
            
            return [...results].sort((a, b) => {{
                let cmp = 0;
                
                switch (latestSortColumn) {{
                    case 'Name':
                        cmp = (a.Name || '').localeCompare(b.Name || '', 'no');
                        break;
                    case 'Event':
                        cmp = (a.Event || '').localeCompare(b.Event || '', 'no');
                        break;
                    case 'Pool':
                        cmp = (a.Pool || '').localeCompare(b.Pool || '', 'no');
                        break;
                    case 'Pos':
                        cmp = (a.Pos || 0) - (b.Pos || 0);
                        break;
                    case 'Tid':
                        cmp = parseTime(a.Tid) - parseTime(b.Tid);
                        break;
                    case 'Poeng':
                        cmp = (a.Poeng || 0) - (b.Poeng || 0);
                        break;
                    case 'Dato':
                        cmp = parseDate(a.Dato) - parseDate(b.Dato);
                        break;
                    case 'Sted':
                        cmp = (a.Sted || '').localeCompare(b.Sted || '', 'no');
                        break;
                    default:
                        cmp = parseDate(a.Dato) - parseDate(b.Dato);
                }}
                
                return cmp * multiplier;
            }});
        }}
        
        function handleLatestSort(column) {{
            if (latestSortColumn === column) {{
                latestSortDirection = latestSortDirection === 'asc' ? 'desc' : 'asc';
            }} else {{
                latestSortColumn = column;
                latestSortDirection = (column === 'Dato' || column === 'Poeng') ? 'desc' : 'asc';
            }}
            latestRegistrationsPage = 1;
            showLatestRegistrations(1);
        }}
        
        function setViewMode(mode) {{
            viewMode = mode;
            document.getElementById('tabRecords').classList.toggle('active', mode === 'records');
            document.getElementById('tabLatest').classList.toggle('active', mode === 'latest');
            document.getElementById('recordsFilters').style.display = mode === 'records' ? 'flex' : 'none';
            document.getElementById('latestFilters').style.display = mode === 'latest' ? 'flex' : 'none';
        }}
        
        function navigateToEventRecord(eventName, gender) {{
            document.getElementById('eventSelect').value = eventName;
            if (gender === 'Male') {{
                document.getElementById('maleOption').checked = true;
            }} else {{
                document.getElementById('femaleOption').checked = true;
            }}
            setViewMode('records');
            filterResults();
        }}
        
        function filterLatestRegistrations(results) {{
            const showMale = document.getElementById('latestMale').checked;
            const showFemale = document.getElementById('latestFemale').checked;
            const show25m = document.getElementById('latestPool25').checked;
            const show50m = document.getElementById('latestPool50').checked;
            
            return results.filter(row => {{
                const genderMatch = (row.Gender === 'Male' && showMale) || (row.Gender === 'Female' && showFemale);
                const pool = row.Pool || '';
                const poolMatch = (pool === '25m' && show25m) || (pool === '50m' && show50m);
                return genderMatch && poolMatch;
            }});
        }}
        
        function getAllRegistrations() {{
            const categories = ['Male_25m', 'Male_50m', 'Female_25m', 'Female_50m'];
            const allResults = [];
            
            for (const [eventName, eventData] of Object.entries(allData)) {{
                for (const category of categories) {{
                    if (eventData[category]) {{
                        eventData[category].forEach((result, index) => {{
                            allResults.push({{
                                ...result,
                                Event: eventName,
                                Pool: result.Pool || (category.endsWith('25m') ? '25m' : '50m'),
                                Gender: result.Gender || (category.startsWith('Male') ? 'Male' : 'Female'),
                                Pos: index + 1
                            }});
                        }});
                    }}
                }}
            }}
            
            return allResults;
        }}
        
        function toggleSubtext(event) {{
            event.preventDefault();
            const shortText = document.querySelector('.subtext-short');
            const fullText = document.querySelector('.subtext-full');
            
            if (shortText.style.display !== 'none') {{
                shortText.style.display = 'none';
                fullText.style.display = 'inline';
            }} else {{
                shortText.style.display = 'inline';
                fullText.style.display = 'none';
            }}
        }}
        
        function changeLanguage(lang) {{
            currentLanguage = lang;
            
            // Update flag buttons
            document.querySelectorAll('.flag-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Update HTML lang attribute
            document.documentElement.lang = lang;
            
            // Update all text elements
            updateMainTitle(lang);
            
            // Update subtext elements
            const shortText = document.querySelector('.subtext-short');
            const fullText = document.querySelector('.subtext-full');
            const readMoreLink = document.querySelector('.read-more-link');
            const readLessLink = document.querySelector('.read-less-link');
            
            shortText.innerHTML = `${{translations[lang].headerSubtextShort}} <a href="#" class="read-more-link" onclick="toggleSubtext(event)">${{translations[lang].readMore}}</a>`;
            fullText.innerHTML = `${{translations[lang].headerSubtextFull}} <a href="#" class="read-less-link" onclick="toggleSubtext(event)">${{translations[lang].readLess}}</a>`;
            
            document.getElementById('allEvents').textContent = translations[lang].allEvents;
            document.querySelector('#maleOption + .radio-text').textContent = translations[lang].maleOption;
            document.querySelector('#femaleOption + .radio-text').textContent = translations[lang].femaleOption;
            document.getElementById('latestMaleLabel').textContent = translations[lang].maleOption;
            document.getElementById('latestFemaleLabel').textContent = translations[lang].femaleOption;
            document.getElementById('latestShowLabel').textContent = translations[lang].showLabel;
            document.getElementById('tabRecords').textContent = translations[lang].tabRecords;
            document.getElementById('tabLatest').textContent = translations[lang].tabLatest;
            
            // Update event dropdown options
            const eventSelect = document.getElementById('eventSelect');
            const currentSelectedValue = eventSelect.value;
            
            // Clear existing options except the first one
            while (eventSelect.children.length > 1) {{
                eventSelect.removeChild(eventSelect.lastChild);
            }}
            
            // Add translated event options
            events.forEach(event => {{
                const option = document.createElement('option');
                option.value = event;
                option.textContent = eventTranslations[lang][event] || event;
                eventSelect.appendChild(option);
            }});
            
            // Restore selected value if it exists
            if (currentSelectedValue) {{
                eventSelect.value = currentSelectedValue;
            }}
            
            // Refresh results to update table headers and messages
            filterResults();
        }}
        
        function filterResults() {{
            const container = document.getElementById('resultsContainer');
            container.innerHTML = '';
            
            if (viewMode === 'latest') {{
                showLatestRegistrations(latestRegistrationsPage);
                return;
            }}
            
            const selectedEvent = document.getElementById('eventSelect').value;
            const selectedGender = document.querySelector('input[name="gender"]:checked').value;
            
            if (selectedEvent) {{
                showEventResults(selectedEvent, selectedGender);
            }} else {{
                showBestSwimmers();
            }}
        }}
        
        function showLatestRegistrations(page = 1) {{
            const container = document.getElementById('resultsContainer');
            container.innerHTML = '';
            const allResults = sortLatestRegistrations(filterLatestRegistrations(getAllRegistrations()));
            
            if (allResults.length === 0) {{
                container.innerHTML = `<div class="no-data">${{translations[currentLanguage].noResultsMessage}}</div>`;
                return;
            }}
            
            const pageSize = 10;
            const totalPages = Math.max(1, Math.ceil(allResults.length / pageSize));
            const currentPage = Math.min(Math.max(1, page), totalPages);
            latestRegistrationsPage = currentPage;
            
            const pageResults = allResults.slice((currentPage - 1) * pageSize, currentPage * pageSize);
            const startRank = (currentPage - 1) * pageSize;
            
            const tableDiv = document.createElement('div');
            tableDiv.className = 'results-table';
            tableDiv.innerHTML = `
                <div class="table-header">
                    <span class="table-header-title">
                        <span>${{translations[currentLanguage].latestRegistrations}}</span>
                        <span class="info-icon" data-tooltip="${{translations[currentLanguage].latestRegistrationsInfoTooltip}}" tabindex="0" aria-label="${{translations[currentLanguage].latestRegistrationsInfoTooltip}}"></span>
                    </span>
                </div>
                <div class="table-content">
                    <table>
                        <thead>
                            <tr>
                                <th class="rank">${{translations[currentLanguage].rankHeader}}</th>
                                <th class="sortable" data-sort="Name">${{translations[currentLanguage].nameHeader}}${{getSortIndicator('Name')}}</th>
                                <th class="sortable" data-sort="Event">${{translations[currentLanguage].eventHeader}}${{getSortIndicator('Event')}}</th>
                                <th class="sortable" data-sort="Pool">${{translations[currentLanguage].poolHeader}}${{getSortIndicator('Pool')}}</th>
                                <th class="sortable" data-sort="Pos">${{translations[currentLanguage].posHeader}}${{getSortIndicator('Pos')}}</th>
                                <th class="sortable" data-sort="Tid">${{translations[currentLanguage].timeHeader}}${{getSortIndicator('Tid')}}</th>
                                <th class="sortable points" data-sort="Poeng">${{translations[currentLanguage].pointsHeader}}${{getSortIndicator('Poeng')}}</th>
                                <th class="sortable" data-sort="Dato">${{translations[currentLanguage].dateHeader}}${{getSortIndicator('Dato')}}</th>
                                <th class="sortable" data-sort="Sted">${{translations[currentLanguage].locationHeader}}${{getSortIndicator('Sted')}}</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${{pageResults.map((row, index) => `
                                <tr>
                                    <td class="rank">${{startRank + index + 1}}</td>
                                    <td>${{row.Name || ''}}</td>
                                    <td>
                                        <button type="button" class="event-link" data-event="${{row.Event || ''}}" data-gender="${{row.Gender || ''}}">
                                            ${{eventTranslations[currentLanguage][row.Event] || row.Event || ''}}
                                        </button>
                                    </td>
                                    <td>${{row.Pool || ''}}</td>
                                    <td>${{row.Pos || ''}}</td>
                                    <td>${{row.Tid || ''}}</td>
                                    <td class="points">${{row.Poeng || ''}}</td>
                                    <td>${{row.Dato || ''}}</td>
                                    <td>${{row.Sted || 'Ukjent'}}</td>
                                </tr>
                            `).join('')}}
                        </tbody>
                    </table>
                </div>
                <div class="table-pagination">
                    <button type="button" class="pagination-btn pagination-prev" ${{currentPage <= 1 ? 'disabled' : ''}}>${{translations[currentLanguage].prevPage}}</button>
                    <span class="pagination-info">${{translations[currentLanguage].pageLabel}} ${{currentPage}} ${{translations[currentLanguage].pageOf}} ${{totalPages}}</span>
                    <button type="button" class="pagination-btn pagination-next" ${{currentPage >= totalPages ? 'disabled' : ''}}>${{translations[currentLanguage].nextPage}}</button>
                </div>
            `;
            
            container.appendChild(tableDiv);
            
            tableDiv.querySelectorAll('th.sortable').forEach(th => {{
                th.addEventListener('click', () => handleLatestSort(th.dataset.sort));
            }});
            
            tableDiv.querySelectorAll('.event-link').forEach(btn => {{
                btn.addEventListener('click', () => navigateToEventRecord(btn.dataset.event, btn.dataset.gender));
            }});
            
            const prevBtn = tableDiv.querySelector('.pagination-prev');
            const nextBtn = tableDiv.querySelector('.pagination-next');
            
            if (prevBtn && currentPage > 1) {{
                prevBtn.addEventListener('click', () => showLatestRegistrations(currentPage - 1));
            }}
            if (nextBtn && currentPage < totalPages) {{
                nextBtn.addEventListener('click', () => showLatestRegistrations(currentPage + 1));
            }}
        }}
        
        function showBestSwimmers() {{
            const container = document.getElementById('resultsContainer');
            const selectedGender = document.querySelector('input[name="gender"]:checked').value;
            
            // Collect all results from all events
            const allMaleResults = [];
            const allFemaleResults = [];
            
            for (const [eventName, eventData] of Object.entries(allData)) {{
                // Add male results
                for (const category of ['Male_25m', 'Male_50m']) {{
                    if (eventData[category]) {{
                        for (const result of eventData[category]) {{
                            const resultCopy = {{...result}};
                            resultCopy.Event = eventName;
                            resultCopy.Pool = category.endsWith('25m') ? '25m' : '50m';
                            allMaleResults.push(resultCopy);
                        }}
                    }}
                }}
                
                // Add female results
                for (const category of ['Female_25m', 'Female_50m']) {{
                    if (eventData[category]) {{
                        for (const result of eventData[category]) {{
                            const resultCopy = {{...result}};
                            resultCopy.Event = eventName;
                            resultCopy.Pool = category.endsWith('25m') ? '25m' : '50m';
                            allFemaleResults.push(resultCopy);
                        }}
                    }}
                }}
            }}
            
            // Sort by points (highest first) and take top 10
            allMaleResults.sort((a, b) => (b.Poeng || 0) - (a.Poeng || 0));
            allFemaleResults.sort((a, b) => (b.Poeng || 0) - (a.Poeng || 0));
            
            const top10Male = allMaleResults.slice(0, 10);
            const top10Female = allFemaleResults.slice(0, 10);
            
            // Show tables based on selected gender
            if (selectedGender === 'Male' && top10Male.length > 0) {{
                const maleTableDiv = document.createElement('div');
                maleTableDiv.className = 'results-table';
                maleTableDiv.innerHTML = `
                    <div class="table-header">
                        <span class="table-header-title">
                            <span>${{translations[currentLanguage].top10Men}}</span>
                            <span class="info-icon" data-tooltip="${{translations[currentLanguage].top10InfoTooltip}}" tabindex="0" aria-label="${{translations[currentLanguage].top10InfoTooltip}}"></span>
                        </span>
                    </div>
                    <div class="table-content">
                        <table>
                            <thead>
                                <tr>
                                    <th class="rank">${{translations[currentLanguage].rankHeader}}</th>
                                    <th>${{translations[currentLanguage].nameHeader}}</th>
                                    <th>${{translations[currentLanguage].eventHeader}}</th>
                                    <th>${{translations[currentLanguage].poolHeader}}</th>
                                    <th>${{translations[currentLanguage].timeHeader}}</th>
                                    <th class="points">${{translations[currentLanguage].pointsHeader}}</th>
                                    <th>${{translations[currentLanguage].dateHeader}}</th>
                                    <th>${{translations[currentLanguage].locationHeader}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{top10Male.map((row, index) => `
                                    <tr>
                                        <td class="rank">${{index + 1}}</td>
                                        <td>${{row.Name || ''}}</td>
                                        <td>${{eventTranslations[currentLanguage][row.Event] || row.Event || ''}}</td>
                                        <td>${{row.Pool || ''}}</td>
                                        <td>${{row.Tid || ''}}</td>
                                        <td class="points">${{row.Poeng || ''}}</td>
                                        <td>${{row.Dato || ''}}</td>
                                        <td>${{row.Sted || 'Ukjent'}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
                container.appendChild(maleTableDiv);
            }}
            
            if (selectedGender === 'Female' && top10Female.length > 0) {{
                const femaleTableDiv = document.createElement('div');
                femaleTableDiv.className = 'results-table';
                femaleTableDiv.innerHTML = `
                    <div class="table-header">
                        <span class="table-header-title">
                            <span>${{translations[currentLanguage].top10Women}}</span>
                            <span class="info-icon" data-tooltip="${{translations[currentLanguage].top10InfoTooltip}}" tabindex="0" aria-label="${{translations[currentLanguage].top10InfoTooltip}}"></span>
                        </span>
                    </div>
                    <div class="table-content">
                        <table>
                            <thead>
                                <tr>
                                    <th class="rank">${{translations[currentLanguage].rankHeader}}</th>
                                    <th>${{translations[currentLanguage].nameHeader}}</th>
                                    <th>${{translations[currentLanguage].eventHeader}}</th>
                                    <th>${{translations[currentLanguage].poolHeader}}</th>
                                    <th>${{translations[currentLanguage].timeHeader}}</th>
                                    <th class="points">${{translations[currentLanguage].pointsHeader}}</th>
                                    <th>${{translations[currentLanguage].dateHeader}}</th>
                                    <th>${{translations[currentLanguage].locationHeader}}</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${{top10Female.map((row, index) => `
                                    <tr>
                                        <td class="rank">${{index + 1}}</td>
                                        <td>${{row.Name || ''}}</td>
                                        <td>${{eventTranslations[currentLanguage][row.Event] || row.Event || ''}}</td>
                                        <td>${{row.Pool || ''}}</td>
                                        <td>${{row.Tid || ''}}</td>
                                        <td class="points">${{row.Poeng || ''}}</td>
                                        <td>${{row.Dato || ''}}</td>
                                        <td>${{row.Sted || 'Ukjent'}}</td>
                                    </tr>
                                `).join('')}}
                            </tbody>
                        </table>
                    </div>
                `;
                container.appendChild(femaleTableDiv);
            }}
            

        }}
        
        function showEventResults(selectedEvent, selectedGender) {{
            const container = document.getElementById('resultsContainer');
            
            const eventData = allData[selectedEvent];
            if (!eventData) {{
                container.innerHTML = `<div class="no-data">${{translations[currentLanguage].noResultsMessage}}</div>`;
                return;
            }}
            
            // Determine which categories to show based on selected gender
            const categories = [];
            if (selectedGender === 'Male') {{
                categories.push('Male_25m');
                categories.push('Male_50m');
            }}
            if (selectedGender === 'Female') {{
                categories.push('Female_25m');
                categories.push('Female_50m');
            }}
            
            // Show 25m first, then 50m
            categories.forEach(category => {{
                const data = eventData[category];
                if (data && data.length > 0) {{
                    const gender = category.startsWith('Male') ? translations[currentLanguage].men : translations[currentLanguage].women;
                    const pool = category.endsWith('25m') ? '25m' : '50m';
                    
                    const tableDiv = document.createElement('div');
                    tableDiv.className = 'results-table';
                    
                    tableDiv.innerHTML = `
                        <div class="table-header">
                            <span>${{eventTranslations[currentLanguage][selectedEvent] || selectedEvent}} - ${{gender}} ${{pool}}</span>
                        </div>
                        <div class="table-content">
                            <table>
                                <thead>
                                    <tr>
                                        <th class="rank">${{translations[currentLanguage].rankHeader}}</th>
                                        <th>${{translations[currentLanguage].nameHeader}}</th>
                                        <th>${{translations[currentLanguage].timeHeader}}</th>
                                        <th class="points">${{translations[currentLanguage].pointsHeader}}</th>
                                        <th>${{translations[currentLanguage].dateHeader}}</th>
                                        <th>${{translations[currentLanguage].locationHeader}}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${{data.map((row, index) => `
                                        <tr>
                                            <td class="rank">${{index + 1}}</td>
                                            <td>${{row.Name || ''}}</td>
                                            <td>${{row.Tid || ''}}</td>
                                            <td class="points">${{row.Poeng || ''}}</td>
                                            <td>${{row.Dato || ''}}</td>
                                            <td>${{row.Sted || 'Ukjent'}}</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>

                        </div>
                    `;
                    
                    container.appendChild(tableDiv);
                }}
            }});
            
            // Show message if no results found for the selected filters
            if (container.children.length === 0) {{
                container.innerHTML = `<div class="no-data">${{translations[currentLanguage].noResultsMessage}}</div>`;
            }}
        }}
        
        // Add event listeners
        document.getElementById('eventSelect').addEventListener('change', filterResults);
        document.querySelectorAll('input[name="gender"]').forEach(radio => {{
            radio.addEventListener('change', filterResults);
        }});
        
        ['latestMale', 'latestFemale', 'latestPool25', 'latestPool50'].forEach(id => {{
            document.getElementById(id).addEventListener('change', () => {{
                latestRegistrationsPage = 1;
                filterResults();
            }});
        }});
        
        document.getElementById('tabRecords').addEventListener('click', () => {{
            setViewMode('records');
            filterResults();
        }});
        
        document.getElementById('tabLatest').addEventListener('click', () => {{
            document.getElementById('eventSelect').value = '';
            latestRegistrationsPage = 1;
            latestSortColumn = 'Dato';
            latestSortDirection = 'desc';
            setViewMode('latest');
            filterResults();
        }});
        
        // Add logo click event to return to best swimmers view
        document.querySelector('.logo').addEventListener('click', function() {{
            document.getElementById('eventSelect').value = '';
            document.getElementById('maleOption').checked = true;
            latestRegistrationsPage = 1;
            setViewMode('records');
            filterResults();
        }});
        
        // Initialize page with current language
        updateMainTitle(currentLanguage);
        
        // Update dropdown options and radio button labels
        document.getElementById('allEvents').textContent = translations[currentLanguage].allEvents;
        document.querySelector('#maleOption + .radio-text').textContent = translations[currentLanguage].maleOption;
        document.querySelector('#femaleOption + .radio-text').textContent = translations[currentLanguage].femaleOption;
        document.getElementById('latestMaleLabel').textContent = translations[currentLanguage].maleOption;
        document.getElementById('latestFemaleLabel').textContent = translations[currentLanguage].femaleOption;
        document.getElementById('latestShowLabel').textContent = translations[currentLanguage].showLabel;
        document.getElementById('tabRecords').textContent = translations[currentLanguage].tabRecords;
        document.getElementById('tabLatest').textContent = translations[currentLanguage].tabLatest;
        
        // Update subtext elements
        const shortText = document.querySelector('.subtext-short');
        const fullText = document.querySelector('.subtext-full');
        
        shortText.innerHTML = `${{translations[currentLanguage].headerSubtextShort}} <a href="#" class="read-more-link" onclick="toggleSubtext(event)">${{translations[currentLanguage].readMore}}</a>`;
        fullText.innerHTML = `${{translations[currentLanguage].headerSubtextFull}} <a href="#" class="read-less-link" onclick="toggleSubtext(event)">${{translations[currentLanguage].readLess}}</a>`;
        
        // Initial load
        filterResults();
    </script>
</body>
</html>"""
    
    # Write main HTML file
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Website generated successfully!")
    print(f"HTML files: index.html")
    print(f"Data loaded from {len(all_data)} events")
    print(f"Latest update: {latest_date}")

if __name__ == "__main__":
    generate_html() 
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
    
    # Get the latest modification time
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
            font-size: 2.2em;
            font-weight: 600;
            color: #2c3e50;
            margin: 0;
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
            gap: 8px;
        }}
        
        .language-btn {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            color: #6c757d;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 0.9em;
            font-weight: 500;
        }}
        
        .language-btn:hover {{
            background: #e9ecef;
            border-color: #adb5bd;
        }}
        
        .language-btn.active {{
            background: #007bff;
            color: white;
            border-color: #007bff;
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
            margin: 20px auto;
            max-width: 1200px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
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
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .table-header span:last-child {{
            font-size: 0.75em;
            color: #adb5bd;
            font-weight: 400;
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
            .header-content {{
                flex-direction: column;
                gap: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .language-switcher {{
                position: static;
                margin-top: 10px;
            }}
            
            .nav-buttons {{
                position: static;
                margin-top: 10px;
            }}
            
            .filters {{
                flex-direction: column;
                align-items: stretch;
            }}
            
            .filter-group {{
                width: 100%;
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
            <div class="header-main">
                <img src="logo.png" alt="TSLK Logo" class="logo">
                <h1 id="mainTitle">TS&LK Klubbrekorder</h1>
                <div class="nav-buttons">
                    <!-- Logo click will return to best swimmers view -->
                </div>
                <div class="language-switcher">
                    <button class="language-btn active" onclick="changeLanguage('no')">Norsk</button>
                    <button class="language-btn" onclick="changeLanguage('en')">English</button>
                </div>
            </div>
            <div class="header-subtext" id="headerSubtext">
                <span class="subtext-short">Denne oversikten viser TS&LK's klubbrekorder i svømming gjennom tidene. <a href="#" class="read-more-link" onclick="toggleSubtext(event)">Les mer</a></span>
                <span class="subtext-full" style="display: none;">Denne oversikten viser TS&LK's klubbrekorder i svømming gjennom tidene. Dataene er hentet fra medley.no og i tillegg er det lagt til noen eldre manuelle oppføringer som medley.no ikke har registrert. Tidene som vises på utøverene må være fra når de har representert TS&LK. Jeg vil forsøke å oppdatere listen 1-2 ganger årlig basert på ferske resultater i Medley - jeg kommer ikke til å legge inn ferske resultater, da må du vente på neste oppdatering. Dersom noen mener at noe er feil, gamle oppføringer som mangler etc. så send meg en mail på ingesqz@gmail.com. Poengene er basert på FINA 2024. <a href="#" class="read-less-link" onclick="toggleSubtext(event)">Les mindre</a></span>
            </div>
        </div>
    </div>
    
    <div class="filters">
        <div class="filter-group">
            <label for="eventSelect" id="eventLabel">Øvelse:</label>
            <select id="eventSelect">
                <option value="" id="allEvents">Velg øvelse</option>
                {''.join(f'<option value="{event}">{event}</option>' for event in events)}
            </select>
        </div>
        
        <div class="filter-group">
            <label for="genderSelect" id="genderLabel">Kjønn:</label>
            <select id="genderSelect">
                <option value="" id="allGenders">Velg kjønn</option>
                <option value="Male" id="maleOption">Menn</option>
                <option value="Female" id="femaleOption">Kvinner</option>
            </select>
        </div>
    </div>
    
    <div class="results-container" id="resultsContainer">
        <!-- Results will be populated by JavaScript -->
    </div>

    <script>
        // Data from Python
        const allData = {json.dumps(all_data)};
        const events = {json.dumps(events)};
        
        // Translations
        const translations = {{
            no: {{
                mainTitle: "TS&LK Klubbrekorder",
                headerSubtextShort: "Denne oversikten viser TS&LK's klubbrekorder i svømming gjennom tidene.",
                headerSubtextFull: "Denne oversikten viser TS&LK's klubbrekorder i svømming gjennom tidene. Dataene er hentet fra medley.no og i tillegg er det lagt til noen eldre manuelle oppføringer som medley.no ikke har registrert. Tidene som vises på utøverene må være fra når de har representert TS&LK. Jeg vil forsøke å oppdatere listen 1-2 ganger årlig basert på ferske resultater i Medley - jeg kommer ikke til å legge inn ferske resultater, da må du vente på neste oppdatering. Dersom noen mener at noe er feil, gamle oppføringer som mangler etc. så send meg en mail på ingesqz@gmail.com. Poengene er basert på FINA 2024.",
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
                timeHeader: "Tid",
                pointsHeader: "Poeng",
                dateHeader: "Dato",
                locationHeader: "Sted",
                men: "Menn",
                women: "Kvinner",
                top10Men: "Topp 10 resultat - uansett øvelse og basseng - Menn",
                top10Women: "Topp 10 resultat - uansett øvelse og basseng - Kvinner",
                lastUpdated: "Sist oppdatert",
                filterMessage: "Vennligst velg både øvelse og kjønn for å se resultater.",
                noResultsMessage: "Ingen resultater funnet for de valgte filtrene."
            }},
            en: {{
                mainTitle: "TS&LK Club Records",
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
                timeHeader: "Time",
                pointsHeader: "Points",
                dateHeader: "Date",
                locationHeader: "Location",
                men: "Men",
                women: "Women",
                top10Men: "Top 10 results - regardless of event and pool - Men",
                top10Women: "Top 10 results - regardless of event and pool - Women",
                lastUpdated: "Last updated",
                filterMessage: "Please select both event and gender to see results.",
                noResultsMessage: "No results found for the selected filters."
            }}
        }};
        
        let currentLanguage = 'no';
        
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
            
            // Update language buttons
            document.querySelectorAll('.language-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');
            
            // Update HTML lang attribute
            document.documentElement.lang = lang;
            
            // Update all text elements
            document.getElementById('mainTitle').textContent = translations[lang].mainTitle;
            
            // Update subtext elements
            const shortText = document.querySelector('.subtext-short');
            const fullText = document.querySelector('.subtext-full');
            const readMoreLink = document.querySelector('.read-more-link');
            const readLessLink = document.querySelector('.read-less-link');
            
            shortText.innerHTML = `${{translations[lang].headerSubtextShort}} <a href="#" class="read-more-link" onclick="toggleSubtext(event)">${{translations[lang].readMore}}</a>`;
            fullText.innerHTML = `${{translations[lang].headerSubtextFull}} <a href="#" class="read-less-link" onclick="toggleSubtext(event)">${{translations[lang].readLess}}</a>`;
            
            document.getElementById('eventLabel').textContent = translations[lang].eventLabel;
            document.getElementById('genderLabel').textContent = translations[lang].genderLabel;
            document.getElementById('allEvents').textContent = translations[lang].allEvents;
            document.getElementById('allGenders').textContent = translations[lang].allGenders;
            document.getElementById('maleOption').textContent = translations[lang].maleOption;
            document.getElementById('femaleOption').textContent = translations[lang].femaleOption;
            
            // Refresh results to update table headers and messages
            filterResults();
        }}
        
        function filterResults() {{
            const selectedEvent = document.getElementById('eventSelect').value;
            const selectedGender = document.getElementById('genderSelect').value;
            
            const container = document.getElementById('resultsContainer');
            container.innerHTML = '';
            
            // If both event and gender are selected, show specific event results
            if (selectedEvent && selectedGender) {{
                showEventResults(selectedEvent, selectedGender);
            }} else {{
                // Otherwise show best swimmers
                showBestSwimmers();
            }}
        }}
        
        function showBestSwimmers() {{
            const container = document.getElementById('resultsContainer');
            
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
            
            // Create male table
            if (top10Male.length > 0) {{
                const maleTableDiv = document.createElement('div');
                maleTableDiv.className = 'results-table';
                maleTableDiv.innerHTML = `
                    <div class="table-header">
                        <span>${{translations[currentLanguage].top10Men}}</span>
                        <span>${{translations[currentLanguage].lastUpdated}}: {latest_date}</span>
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
                                        <td>${{row.Event || ''}}</td>
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
            
            // Create female table
            if (top10Female.length > 0) {{
                const femaleTableDiv = document.createElement('div');
                femaleTableDiv.className = 'results-table';
                femaleTableDiv.innerHTML = `
                    <div class="table-header">
                        <span>${{translations[currentLanguage].top10Women}}</span>
                        <span>${{translations[currentLanguage].lastUpdated}}: {latest_date}</span>
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
                                        <td>${{row.Event || ''}}</td>
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
                            <span>${{selectedEvent}} - ${{gender}} ${{pool}}</span>
                            <span>${{translations[currentLanguage].lastUpdated}}: {latest_date}</span>
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
        document.getElementById('genderSelect').addEventListener('change', filterResults);
        
        // Add logo click event to return to best swimmers view
        document.querySelector('.logo').addEventListener('click', function() {{
            document.getElementById('eventSelect').value = '';
            document.getElementById('genderSelect').value = '';
            filterResults();
        }});
        
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
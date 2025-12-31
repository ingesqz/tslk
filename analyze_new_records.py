import pandas as pd
import os
import glob
from datetime import datetime

def get_pool_length(pool_val):
    """Extract pool length from the pool value."""
    if pd.isna(pool_val):
        return "Unknown"
    
    pool_str = str(pool_val).lower()
    if '25' in pool_str or '25m' in pool_str:
        return "25m"
    elif '50' in pool_str or '50m' in pool_str:
        return "50m"
    else:
        return "Unknown"

def identify_gender(name):
    """Identify gender based on the swimmer's name."""
    # Remove "Navn: " prefix if present
    clean_name = name.replace("Navn: ", "").strip()
    
    # Split the name to get the first name
    name_parts = clean_name.split(',')
    if len(name_parts) > 1:
        first_name = name_parts[1].strip().split()[0]
    else:
        first_name = clean_name.split()[0]
    
    first_name = first_name.lower()
    
    # Common Norwegian male names
    male_names = {
        'odin', 'adam', 'jon', 'albert', 'ole', 'aamund', 'johannes', 'tomas', 'paal',
        'sondre', 'andreas', 'ivan', 'tamer', 'bjarne', 'brage', 'ådne', 'sindre', 'vetle', 'terje'
    }
    
    # Common Norwegian female names
    female_names = {
        'sara', 'maria', 'silje', 'carina', 'eirill', 'henriette', 'elise', 'vilde', 
        'tove', 'amanda', 'kirsti', 'guro', 'linn-mari', 'paulien', 'frøydis', 'mari', 
        'sissel', 'gudrun', 'torborg', 'solveig', 'elisabeth', 'malin', 'siv', 'sigrid', 
        'annelin', 'heidi', 'linn', 'maud', 'miriam', 'ingrid'
    }
    
    if first_name in male_names:
        return 'Male'
    elif first_name in female_names:
        return 'Female'
    else:
        if first_name.endswith(('a', 'e', 'i', 'n', 'r')):
            if first_name.endswith(('a', 'e')):
                return 'Female'
            else:
                return 'Male'
        else:
            return 'Male'

def clean_swimmer_name(name):
    """Clean swimmer name for comparison."""
    clean_name = name.replace("Navn: ", "").strip()
    return clean_name

def standardize_name_variations(name):
    """Standardize known name variations."""
    if name == "Solum Ole Peder Uthus":
        return "Ole Peder Uthus Solum"
    return name

def format_name_for_display(name):
    """Format name as 'Firstname Lastname' from various input formats."""
    clean_name = name.replace("Navn: ", "").strip()
    clean_name = standardize_name_variations(clean_name)
    
    if ',' in clean_name:
        parts = clean_name.split(',')
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            return f"{first_name} {last_name}"
    
    return clean_name

def process_single_file(input_file):
    """Process a single swim results Excel file and return the processed data."""
    print(f"\nProcessing file: {input_file}")
    
    try:
        df = pd.read_excel(input_file, header=None)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return None, None
    
    # Find the event name
    event_name = None
    for idx, row in df.iterrows():
        if pd.notna(row[1]) and isinstance(row[1], str):
            if any(keyword in row[1].lower() for keyword in ['m', 'butterfly', 'freestyle', 'backstroke', 'breaststroke', 'medley']):
                event_name = row[1]
                break
    
    if not event_name:
        print(f"Could not find event name in {input_file}")
        return None, None
    
    # Rename "Individuell Medley" to "Medley"
    if "individuell medley" in event_name.lower():
        event_name = event_name.replace("Individuell Medley", "Medley")
        event_name = event_name.replace("Individuell medley", "Medley")
        event_name = event_name.replace("individuell medley", "Medley")
    
    print(f"Event name found: {event_name}")
    
    # Process rows
    swimmers_data = []
    current_swimmer = None
    current_swimmer_data = []
    
    for idx, row in df.iterrows():
        if pd.notna(row[0]) and isinstance(row[0], str):
            if current_swimmer and current_swimmer_data:
                swimmers_data.append((current_swimmer, current_swimmer_data))
            current_swimmer = row[0]
            current_swimmer_data = []
        else:
            if current_swimmer:
                try:
                    time_val = row[2] if pd.notna(row[2]) else None
                    points_val = row[3] if pd.notna(row[3]) else None
                    date_val = row[4] if pd.notna(row[4]) else None
                    location_val = row[5] if pd.notna(row[5]) else None
                    pool_val = row[6] if pd.notna(row[6]) else None
                    
                    if points_val is not None and isinstance(points_val, (int, float)):
                        current_swimmer_data.append({
                            'Name': current_swimmer,
                            'Tid': time_val,
                            'Poeng': points_val,
                            'Dato': date_val,
                            'Sted': location_val,
                            'Pool': pool_val
                        })
                except:
                    continue
    
    if current_swimmer and current_swimmer_data:
        swimmers_data.append((current_swimmer, current_swimmer_data))
    
    # Keep all results
    all_results = []
    for swimmer, results in swimmers_data:
        if results:
            all_results.extend(results)
    
    if not all_results:
        print("No valid results found")
        return None, None
    
    result_df = pd.DataFrame(all_results)
    result_df['Gender'] = result_df['Name'].apply(identify_gender)
    result_df['PoolLength'] = result_df['Pool'].apply(get_pool_length)
    result_df['CleanName'] = result_df['Name'].apply(clean_swimmer_name)
    result_df['CleanName'] = result_df['CleanName'].apply(standardize_name_variations)
    
    # Group by cleaned name and pool type, keep the best result for each unique swimmer per pool
    merged_results = []
    for _, group in result_df.groupby(['CleanName', 'PoolLength']):
        if len(group) > 1:
            best_entry = group.loc[group['Poeng'].idxmax()]
            merged_results.append(best_entry)
        else:
            merged_results.append(group.iloc[0])
    
    result_df = pd.DataFrame(merged_results)
    result_df = result_df.drop('CleanName', axis=1)
    result_df['Name'] = result_df['Name'].apply(format_name_for_display)
    result_df = result_df.sort_values('Poeng', ascending=False)
    
    # Map PoolLength to Pool format used in EndResult
    result_df['Pool'] = result_df['PoolLength']
    result_df = result_df.drop('PoolLength', axis=1)
    
    return event_name, result_df

def load_current_records():
    """Load current records from EndResult folder."""
    current_records = {}
    endresult_folder = "EndResult"
    
    if not os.path.exists(endresult_folder):
        return current_records
    
    excel_files = glob.glob(os.path.join(endresult_folder, "*.xlsx"))
    
    for file_path in excel_files:
        try:
            event_name = os.path.splitext(os.path.basename(file_path))[0]
            excel_file = pd.ExcelFile(file_path)
            
            event_data = {}
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                if not df.empty:
                    event_data[sheet_name] = df
            
            if event_data:
                current_records[event_name] = event_data
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            continue
    
    return current_records

def compare_records(new_records, current_records):
    """Compare new records with current records and identify improvements."""
    improvements = {}
    
    for event_name, new_df in new_records.items():
        if event_name not in current_records:
            print(f"\n⚠️  NEW EVENT FOUND: {event_name}")
            improvements[event_name] = {'new_event': True, 'records': new_df}
            continue
        
        current_event = current_records[event_name]
        event_improvements = []
        
        # Compare by category (Male_25m, Male_50m, Female_25m, Female_50m)
        for category in ['Male_25m', 'Male_50m', 'Female_25m', 'Female_50m']:
            # Filter new records for this category
            gender = 'Male' if category.startswith('Male') else 'Female'
            pool = '25m' if category.endswith('25m') else '50m'
            
            new_category_df = new_df[(new_df['Gender'] == gender) & (new_df['Pool'] == pool)].copy()
            
            if new_category_df.empty:
                continue
            
            # Get current records for this category
            current_category_df = current_event.get(category, pd.DataFrame())
            
            if current_category_df.empty:
                print(f"\n✅ NEW CATEGORY: {event_name} - {category}")
                event_improvements.append({
                    'category': category,
                    'type': 'new_category',
                    'records': new_category_df.head(10)
                })
                continue
            
            # Compare top records
            new_top = new_category_df.head(10).copy()
            current_top = current_category_df.head(10).copy()
            
            # Check for new records that beat current ones
            for _, new_record in new_top.iterrows():
                swimmer_name = new_record['Name']
                new_points = new_record['Poeng']
                
                # Check if this swimmer exists in current records
                swimmer_current = current_category_df[current_category_df['Name'] == swimmer_name]
                
                if swimmer_current.empty:
                    # New swimmer
                    event_improvements.append({
                        'category': category,
                        'type': 'new_swimmer',
                        'swimmer': swimmer_name,
                        'points': new_points,
                        'time': new_record['Tid'],
                        'date': new_record['Dato']
                    })
                else:
                    # Check if points improved
                    current_points = swimmer_current.iloc[0]['Poeng']
                    if new_points > current_points:
                        event_improvements.append({
                            'category': category,
                            'type': 'improved_record',
                            'swimmer': swimmer_name,
                            'old_points': current_points,
                            'new_points': new_points,
                            'old_time': swimmer_current.iloc[0]['Tid'],
                            'new_time': new_record['Tid'],
                            'date': new_record['Dato']
                        })
            
            # Check if any new record beats the current top 10
            if not current_top.empty:
                current_min_points = current_top['Poeng'].min()
                new_better = new_category_df[new_category_df['Poeng'] > current_min_points]
                
                if not new_better.empty:
                    for _, better_record in new_better.iterrows():
                        if better_record['Name'] not in current_top['Name'].values:
                            event_improvements.append({
                                'category': category,
                                'type': 'top10_improvement',
                                'swimmer': better_record['Name'],
                                'points': better_record['Poeng'],
                                'time': better_record['Tid'],
                                'date': better_record['Dato'],
                                'beats_min': current_min_points
                            })
        
        if event_improvements:
            improvements[event_name] = {
                'new_event': False,
                'improvements': event_improvements
            }
    
    return improvements

def main():
    """Main function to analyze new records."""
    print("=" * 80)
    print("ANALYZING NEW 2025 RECORDS")
    print("=" * 80)
    
    # Get new files (numbered 1-17 and grdRanking.xlsx)
    new_files = []
    for i in range(1, 18):
        file_path = f"Rawdata/grdRanking ({i}).xlsx"
        if os.path.exists(file_path):
            new_files.append(file_path)
    
    if os.path.exists("Rawdata/grdRanking.xlsx"):
        new_files.append("Rawdata/grdRanking.xlsx")
    
    if not new_files:
        print("No new files found in Rawdata folder")
        return
    
    print(f"\nFound {len(new_files)} new files to process")
    
    # Process new files
    new_records = {}
    for file_path in new_files:
        event_name, result_df = process_single_file(file_path)
        if event_name and result_df is not None:
            if event_name in new_records:
                # Combine with existing data
                new_records[event_name] = pd.concat([new_records[event_name], result_df], ignore_index=True)
                new_records[event_name] = new_records[event_name].drop_duplicates(subset=['Name', 'Pool'], keep='first')
                new_records[event_name] = new_records[event_name].sort_values('Poeng', ascending=False)
            else:
                new_records[event_name] = result_df
    
    print(f"\n✅ Processed {len(new_records)} events from new files")
    
    # Load current records
    print("\n" + "=" * 80)
    print("LOADING CURRENT RECORDS")
    print("=" * 80)
    current_records = load_current_records()
    print(f"✅ Loaded {len(current_records)} current events")
    
    # Compare records
    print("\n" + "=" * 80)
    print("COMPARING NEW RECORDS WITH CURRENT RECORDS")
    print("=" * 80)
    improvements = compare_records(new_records, current_records)
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY OF POTENTIAL IMPROVEMENTS")
    print("=" * 80)
    
    if not improvements:
        print("\n✅ No new records found that beat current records")
        return
    
    for event_name, data in improvements.items():
        print(f"\n📊 EVENT: {event_name}")
        print("-" * 80)
        
        if data['new_event']:
            print("  ⚠️  NEW EVENT - Not in current records")
            print(f"  Records found: {len(data['records'])}")
        else:
            for imp in data['improvements']:
                category = imp['category']
                imp_type = imp['type']
                
                if imp_type == 'new_category':
                    print(f"  ✅ NEW CATEGORY: {category}")
                    print(f"     Records: {len(imp['records'])}")
                elif imp_type == 'new_swimmer':
                    print(f"  🆕 NEW SWIMMER in {category}:")
                    print(f"     {imp['swimmer']} - {imp['points']} points ({imp['time']}) - {imp['date']}")
                elif imp_type == 'improved_record':
                    print(f"  📈 IMPROVED RECORD in {category}:")
                    print(f"     {imp['swimmer']}")
                    print(f"     Old: {imp['old_points']} points ({imp['old_time']})")
                    print(f"     New: {imp['new_points']} points ({imp['new_time']}) - {imp['date']}")
                elif imp_type == 'top10_improvement':
                    print(f"  ⬆️  TOP 10 IMPROVEMENT in {category}:")
                    print(f"     {imp['swimmer']} - {imp['points']} points ({imp['time']}) - {imp['date']}")
                    print(f"     (Beats current minimum: {imp['beats_min']} points)")

if __name__ == "__main__":
    main()


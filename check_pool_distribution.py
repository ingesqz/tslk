import pandas as pd
import os

print("🏊‍♂️ CHECKING ATHLETES WITH BOTH POOL TYPES")
print("=" * 50)

# Check a few raw data files
raw_files = ['grdRanking (27).xlsx', 'grdRanking (31).xlsx', 'grdRanking (24).xlsx']

for file in raw_files:
    print(f"\n📊 {file}:")
    
    try:
        df = pd.read_excel(f'Rawdata/{file}')
        
        # Get pool distribution
        pool_counts = df['Basseng'].value_counts()
        print(f"  Pool distribution: {dict(pool_counts)}")
        
        # Find athletes with both pool types
        athletes = {}
        for idx, row in df.iterrows():
            if pd.notna(row['Basseng']) and pd.notna(row['Nr']):
                name = row['Nr']
                pool = row['Basseng']
                if name not in athletes:
                    athletes[name] = set()
                athletes[name].add(pool)
        
        # Count athletes with both pools
        both_pools = [name for name, pools in athletes.items() if len(pools) > 1]
        print(f"  Athletes with both pool types: {len(both_pools)}")
        
        if len(both_pools) > 0:
            print(f"  Examples: {both_pools[:5]}")
    
    except Exception as e:
        print(f"  Error: {e}")

print(f"\n✅ VERIFICATION:")
print(f"   • System should allow athletes in both 25m and 50m pools")
print(f"   • Each athlete gets their best points result per pool type")
print(f"   • This provides more complete performance tracking") 
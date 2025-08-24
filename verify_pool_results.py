import pandas as pd

# Read all four sheets from the Excel file
males_25m = pd.read_excel("100m Butterfly.xlsx", sheet_name='Male_25m')
males_50m = pd.read_excel("100m Butterfly.xlsx", sheet_name='Male_50m')
females_25m = pd.read_excel("100m Butterfly.xlsx", sheet_name='Female_25m')
females_50m = pd.read_excel("100m Butterfly.xlsx", sheet_name='Female_50m')

print("=== MALE 25m SWIMMERS (Top 10) ===")
print(f"Total male 25m swimmers: {len(males_25m)}")
if len(males_25m) > 0:
    print("\nTop 10 Male 25m results:")
    print(males_25m[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
    print(f"\nMale 25m statistics:")
    print(f"Highest points: {males_25m['Poeng'].max()}")
    print(f"Lowest points: {males_25m['Poeng'].min()}")
    print(f"Average points: {males_25m['Poeng'].mean():.2f}")
else:
    print("No male 25m swimmers found")

print("\n" + "="*50)

print("\n=== MALE 50m SWIMMERS (Top 10) ===")
print(f"Total male 50m swimmers: {len(males_50m)}")
if len(males_50m) > 0:
    print("\nTop 10 Male 50m results:")
    print(males_50m[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
    print(f"\nMale 50m statistics:")
    print(f"Highest points: {males_50m['Poeng'].max()}")
    print(f"Lowest points: {males_50m['Poeng'].min()}")
    print(f"Average points: {males_50m['Poeng'].mean():.2f}")
else:
    print("No male 50m swimmers found")

print("\n" + "="*50)

print("\n=== FEMALE 25m SWIMMERS (Top 10) ===")
print(f"Total female 25m swimmers: {len(females_25m)}")
if len(females_25m) > 0:
    print("\nTop 10 Female 25m results:")
    print(females_25m[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
    print(f"\nFemale 25m statistics:")
    print(f"Highest points: {females_25m['Poeng'].max()}")
    print(f"Lowest points: {females_25m['Poeng'].min()}")
    print(f"Average points: {females_25m['Poeng'].mean():.2f}")
else:
    print("No female 25m swimmers found")

print("\n" + "="*50)

print("\n=== FEMALE 50m SWIMMERS (Top 10) ===")
print(f"Total female 50m swimmers: {len(females_50m)}")
if len(females_50m) > 0:
    print("\nTop 10 Female 50m results:")
    print(females_50m[['Name', 'Tid', 'Poeng', 'Dato', 'Sted', 'PoolLength']])
    print(f"\nFemale 50m statistics:")
    print(f"Highest points: {females_50m['Poeng'].max()}")
    print(f"Lowest points: {females_50m['Poeng'].min()}")
    print(f"Average points: {females_50m['Poeng'].mean():.2f}")
else:
    print("No female 50m swimmers found")

print("\n" + "="*50)

print(f"\n=== SUMMARY ===")
print(f"Male 25m swimmers: {len(males_25m)}")
print(f"Male 50m swimmers: {len(males_50m)}")
print(f"Female 25m swimmers: {len(females_25m)}")
print(f"Female 50m swimmers: {len(females_50m)}")
print(f"Total swimmers across all categories: {len(males_25m) + len(males_50m) + len(females_25m) + len(females_50m)}") 
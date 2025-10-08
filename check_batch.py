import pandas as pd
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Check the last batch file
df = pd.read_csv(os.path.join(script_dir, 'swarms', 'input', 'npi_batch_12.csv'))

print('SWARM_OUTPUT column check:')
print(f'Non-null SWARM_OUTPUT entries: {df["SWARM_OUTPUT"].notna().sum()}')
print(f'Total records: {len(df)}')

print('\nSample SWARM_OUTPUT data:')
for i, output in enumerate(df['SWARM_OUTPUT'].dropna()):
    print(f"Record {i+1}: {output[:200]}...")
    if i >= 2:  # Show only first 3 samples
        break

print(f'\nBatch file contains records with NPIs: {list(df["NPI"])}')

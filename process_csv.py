import pandas as pd
import json
import asyncio
import os
from main import run_swarm

script_dir = os.path.dirname(os.path.abspath(__file__))

async def process_row(index, row, df):
    print(f"Processing row {index + 1} of {len(df)}")

    input_data = {
        "first_name": row['PROVIDER_FIRST_NAME'] if pd.notna(row['PROVIDER_FIRST_NAME']) else "",
        "middle_name": row['PROVIDER_MIDDLE_NAME'] if pd.notna(row['PROVIDER_MIDDLE_NAME']) else "",
        "last_name": row['PROVIDER_LAST_NAME_LEGAL_NAME'] if pd.notna(row['PROVIDER_LAST_NAME_LEGAL_NAME']) else "",
        "classification": row['CLASSIFICATION'] if pd.notna(row['CLASSIFICATION']) else "",
        "npi_number": str(row['NPI']) if pd.notna(row['NPI']) else "",
        "primary_affiliation_name": row['PRIMARY_AFFILIATION_NAME'] if pd.notna(row['PRIMARY_AFFILIATION_NAME']) else ""
    }

    try:
        result = await run_swarm(input_data)
        df.at[index, 'SWARM_OUTPUT'] = json.dumps(result)
        print(f"✓ Successfully processed row {index + 1}")
    except Exception as e:
        print(f"✗ Error processing row {index + 1}: {str(e)}")
        df.at[index, 'SWARM_OUTPUT'] = json.dumps({"error": str(e)})

async def process_csv_concurrent():
    df = pd.read_csv(os.path.join(script_dir, 'swarms', 'input', 'NPI_100_gpt5.csv'))

    # Skip first 20 records, process next 60 records (20-79 inclusive)
    start_index = 20
    end_index = 80  # Exclusive end, so 20-79 = 60 records
    df_subset = df.iloc[start_index:end_index]

    chunk_size = 5  # Process 5 records concurrently
    total_records = len(df_subset)

    print(f"Starting processing of {total_records} records (skipping first 20)")
    print(f"Processing in chunks of {chunk_size} records concurrently")

    for i in range(0, total_records, chunk_size):
        chunk_df = df_subset.iloc[i:i+chunk_size]
        chunk_start = start_index + i
        chunk_end = min(start_index + i + chunk_size, end_index)

        print(f"\n--- Processing chunk: records {chunk_start + 1}-{chunk_end} ---")

        tasks = []
        for subset_idx, (original_index, row) in enumerate(chunk_df.iterrows()):
            # Use the original dataframe index for updating
            actual_index = start_index + i + subset_idx
            print(f"  Queueing row {actual_index + 1} (subset index: {subset_idx})")
            tasks.append(process_row(actual_index, row, df))

        # Process the chunk concurrently
        try:
            await asyncio.gather(*tasks)
            print(f"✓ Chunk {chunk_start + 1}-{chunk_end} processed successfully")
        except Exception as e:
            print(f"✗ Error in chunk {chunk_start + 1}-{chunk_end}: {str(e)}")
            continue  # Continue with next chunk even if one fails

        # Save the updated chunk to a separate CSV
        updated_chunk = df.iloc[chunk_start:chunk_end]
        batch_num = (i // chunk_size) + 1
        output_filename = os.path.join(script_dir, 'swarms', 'input', f'npi_batch_{batch_num}.csv')
        updated_chunk.to_csv(output_filename, index=False)
        print(f"✓ Saved batch {batch_num} to {output_filename}")

        # Verify the file was created successfully
        if os.path.exists(output_filename):
            saved_records = len(pd.read_csv(output_filename))
            print(f"✓ Verified: {saved_records} records saved in batch {batch_num}")
        else:
            print(f"✗ Warning: Batch file {output_filename} was not created properly")

    print("\n=== Processing Summary ===")
    print(f"Total records processed: {total_records}")
    print(f"Records skipped: {start_index}")
    print(f"Batch files created: {batch_num}")
    print("Processing complete.")

if __name__ == "__main__":
    asyncio.run(process_csv_concurrent())

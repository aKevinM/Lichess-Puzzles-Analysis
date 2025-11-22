import csv
import os

def clean_puzzles():
    input_file = 'lichess_db_puzzle.csv'
    output_file = 'lichess_db_puzzle_uncleaned.csv'
    
    print(f"Starting to process {input_file}...")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    total_count = 0
    kept_count = 0
    removed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        
        # Write header
        writer.writeheader()
        print("Header written to output file")
        
        # Process each row
        for row in reader:
            total_count += 1
            
            # Garder uniquement les puzzles SANS OpeningTags
            if not row['OpeningTags'] or not row['OpeningTags'].strip():
                writer.writerow(row)
                kept_count += 1
            else:
                removed_count += 1
            
            # Log progress every 10000 rows
            if total_count % 10000 == 0:
                print(f"Processed {total_count:,} puzzles - Kept: {kept_count:,}, Removed: {removed_count:,}")
    
    print("\n" + "="*60)
    print(f"Processing complete!")
    print(f"Total puzzles processed: {total_count:,}")
    print(f"Puzzles kept (without OpeningTags): {kept_count:,}")
    print(f"Puzzles removed (with OpeningTags): {removed_count:,}")
    print(f"Output saved to: {output_file}")
    print("="*60)

if __name__ == "__main__":
    clean_puzzles()

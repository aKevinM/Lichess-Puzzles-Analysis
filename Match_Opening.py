import csv
import os
from difflib import get_close_matches

def normalize_string(s):
    """Normalize a string for comparison by removing special chars and converting to lowercase."""
    return s.lower().replace("'", "").replace("-", "").replace(":", "").replace(" ", "").replace("_", "")

def load_opening_names(analysis_file):
    """Load all unique opening names from the analysis file."""
    print(f"Loading opening names from {analysis_file}...")
    opening_names = set()
    
    with open(analysis_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Opening'] and row['Opening'].strip():
                opening_names.add(row['Opening'].strip())
    
    print(f"Loaded {len(opening_names):,} unique opening names")
    return opening_names

def create_opening_mapping(opening_names):
    """Create a mapping from normalized strings to actual opening names."""
    print("Creating opening name mapping...")
    mapping = {}
    
    for opening in opening_names:
        normalized = normalize_string(opening)
        mapping[normalized] = opening
    
    print(f"Created mapping for {len(mapping):,} openings")
    return mapping

def find_best_match(opening_tag, mapping):
    """Find the best matching opening name for a given opening tag."""
    # Split opening tag if it contains multiple tags (space-separated)
    tags = opening_tag.split()
    
    # Try each tag
    for tag in tags:
        normalized_tag = normalize_string(tag)
        
        # Direct match
        if normalized_tag in mapping:
            return mapping[normalized_tag]
        
        # Partial match - check if tag is contained in any opening
        for norm_opening, actual_opening in mapping.items():
            if normalized_tag in norm_opening or norm_opening in normalized_tag:
                return actual_opening
    
    return None

def normalize_puzzle_openings():
    analysis_file = 'lichess_games_analysis.csv'
    puzzle_file = 'lichess_db_puzzle_cleaned.csv'
    output_file = 'lichess_db_puzzle_normalized.csv'
    
    # Check if files exist
    if not os.path.exists(analysis_file):
        print(f"Error: {analysis_file} not found!")
        return
    
    if not os.path.exists(puzzle_file):
        print(f"Error: {puzzle_file} not found!")
        return
    
    # Load opening names and create mapping
    opening_names = load_opening_names(analysis_file)
    opening_mapping = create_opening_mapping(opening_names)
    
    print(f"\nStarting to normalize {puzzle_file}...")
    print("="*60)
    
    total_count = 0
    matched_count = 0
    unmatched_count = 0
    unmatched_samples = set()
    
    with open(puzzle_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        
        # Write header
        writer.writeheader()
        print("Header written to output file")
        
        # Process each row
        for row in reader:
            total_count += 1
            
            original_tag = row['OpeningTags']
            
            # Try to find matching opening
            matched_opening = find_best_match(original_tag, opening_mapping)
            
            if matched_opening:
                row['OpeningTags'] = matched_opening
                matched_count += 1
            else:
                unmatched_count += 1
                # Keep first 10 unmatched samples for reporting
                if len(unmatched_samples) < 10:
                    unmatched_samples.add(original_tag)
            
            writer.writerow(row)
            
            # Log progress every 50000 rows
            if total_count % 50000 == 0:
                match_rate = (matched_count / total_count * 100) if total_count > 0 else 0
                print(f"Processed {total_count:,} puzzles - Matched: {matched_count:,} ({match_rate:.1f}%), Unmatched: {unmatched_count:,}")
    
    # Final report
    print("\n" + "="*60)
    print(f"Processing complete!")
    print(f"Total puzzles processed: {total_count:,}")
    print(f"Puzzles matched: {matched_count:,} ({matched_count/total_count*100:.2f}%)")
    print(f"Puzzles unmatched: {unmatched_count:,} ({unmatched_count/total_count*100:.2f}%)")
    print(f"Output saved to: {output_file}")
    
    if unmatched_samples:
        print("\nSample unmatched OpeningTags:")
        for i, sample in enumerate(list(unmatched_samples)[:10], 1):
            print(f"  {i}. {sample}")
    
    print("="*60)

if __name__ == "__main__":
    normalize_puzzle_openings()

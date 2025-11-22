import re
import csv
from pathlib import Path

def process_large_pgn_file(pgn_file_path, csv_file_path):
    """
    Process a large PGN file efficiently by reading line by line
    """
    print(f"Processing large PGN file: {pgn_file_path}")
    
    games_processed = 0
    current_game_data = {}
    games_data = []
    
    with open(pgn_file_path, 'r', encoding='utf-8') as pgn_file:
        for line in pgn_file:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check if this is a metadata line
            metadata_match = re.match(r'\[(\w+)\s+"([^"]*)"\]', line)
            if metadata_match:
                key, value = metadata_match.groups()
                current_game_data[key] = value
            else:
                # This is a move line, which means we've reached the end of metadata
                # Process the completed game
                if all(field in current_game_data for field in ['Opening', 'WhiteElo', 'BlackElo']):
                    try:
                        white_elo = int(current_game_data['WhiteElo'])
                        black_elo = int(current_game_data['BlackElo'])
                        avg_rating = (white_elo + black_elo) / 2
                        
                        games_data.append({
                            'Opening': current_game_data['Opening'],
                            'WhiteElo': white_elo,
                            'BlackElo': black_elo,
                            'AvgPlayerRating': avg_rating
                        })
                        
                        games_processed += 1
                        
                        # Write to CSV in batches to save memory
                        if len(games_data) >= 1000:
                            write_batch_to_csv(games_data, csv_file_path, games_processed == 1000)
                            games_data = []
                            
                    except (ValueError, TypeError):
                        # Skip games with invalid data
                        pass
                
                # Reset for next game
                current_game_data = {}
    
    # Write any remaining games
    if games_data:
        write_batch_to_csv(games_data, csv_file_path, games_processed == len(games_data))
    
    print(f"Successfully processed {games_processed} games")
    print(f"CSV file created: {csv_file_path}")

def write_batch_to_csv(games_data, csv_file_path, write_header=False):
    """
    Write a batch of games to CSV
    """
    with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Opening', 'WhiteElo', 'BlackElo', 'AvgPlayerRating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if write_header:
            writer.writeheader()
        
        for game in games_data:
            writer.writerow(game)

def main():
    pgn_file = "lichess_db_standard_rated.pgn"
    csv_file = "lichess_games_analysis.csv"
    
    # Check if PGN file exists
    if not Path(pgn_file).exists():
        print(f"Error: File '{pgn_file}' not found in the current directory.")
        print("Please make sure the PGN file is in the same folder as this script.")
        return
    
    # Delete existing CSV file if it exists
    if Path(csv_file).exists():
        Path(csv_file).unlink()
    
    try:
        process_large_pgn_file(pgn_file, csv_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("This might be due to the file being very large or corrupted.")

if __name__ == "__main__":
    main()
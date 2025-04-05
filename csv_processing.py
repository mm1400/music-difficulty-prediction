import pandas as pd
import numpy as np
import argparse
import os
from multiprocessing import Pool
from pathlib import Path

def get_features(filepath):
    """
    Extract features from a CSV file containing music data.
    """
    # Load CSV file
    df = pd.read_csv(filepath, low_memory=False)
    
    if 'tempo' not in df.columns:
        print('file does not contain tempo column', filepath)
        return None
        
    
    df = df.sort_values(by="tick")
    df["tempo"] = df["tempo"].ffill() # fill blank tempo values

    tempo_deviation = df["tempo"].std()

    average_tempo = df["tempo"].mean()
    average_bpm = (60_000_000 / average_tempo)

    total_duration = df['time'].sum()
    
    unique_note_count = df['note'].nunique()

    note_on_count = df[df['type'] == 'note_on'].shape[0]
    
    average_note_density = note_on_count

    # for each note_on, compare to the tick on the next row on how big the difference is between the two 
    df[df['type'] == 'note_on']

    tick_count = df['tick'].max()

    note_density = note_on_count / tick_count

    # determine if the time signature has an odd numerator, if so song is harder?
    time_signature = df[df['type'] == 'time_signature']
    
    
    overlapping_notes = get_overlapping_notes(df)
    
    return {
      'file': filepath.split('\\')[1],
      'average_tempo': average_tempo,
      'average_bpm': average_bpm,
      'note_count': note_on_count,
      'tick_count': tick_count,
      'note_density': note_density,
      'tempo_deviation': tempo_deviation,
      'unique_note_count': unique_note_count,
      'total_duration': total_duration,
      'overlapping_notes': overlapping_notes,
    }

def get_overlapping_notes(df):
    overlapping_notes = 0
    for i in range(1, len(df)):
        current_row = df.iloc[i-1]
        next_row = df.iloc[i]
        if current_row['type'] == 'note_on' and next_row['type'] == 'note_on':
            if current_row['tick'] == next_row['tick'] and current_row['note'] != next_row['note']:
                overlapping_notes += 1
    return overlapping_notes

def process_directory(directory, recursive=False):
    """
    Process all CSV files in the given directory and extract features.
    """
    print('getting files...')
    files = list(get_files_in_directory(directory, recursive))
    total_files = len(files)
    results = []
    print(f'found {total_files} files, processing...')
    with Pool() as pool:
        for i in range(0, total_files, 100):
            chunk = files[i:i+100]
            chunk_results = pool.map(get_features, chunk)
            print(f"Processed {i} files of {total_files} files")
            results.extend(chunk_results)
    
    #remove None values from results
    return [result for result in results if result is not None]

def get_files_in_directory(directory, recursive=False):
    """
    Get all CSV files in the given directory
    """
    if recursive:
        return Path(directory).rglob("*.csv")
    else:
        return Path(directory).glob("*.csv")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract features from CSV files present in a directory")
    parser.add_argument("directory", type=str, help="Directory containing CSV files")
    parser.add_argument(
        "--output", 
        "-o", 
        type=str, 
        default="features.csv", 
        help="Output CSV file for features"
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action='store_true',
        help="Whether to search recursively in subdirectories"
    )
    args = parser.parse_args()
    features = []
    try:
        features = process_directory(args.directory, args.recursive)
    except Exception as e:
        print(f"Error processing files: {e}")
    finally:
        if features:
            df = pd.DataFrame(features)
            df.to_csv(f"{args.output}", index=False)
        else:
            print("No features found")
            

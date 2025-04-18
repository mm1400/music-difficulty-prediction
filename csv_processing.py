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

    tick_count = df['tick'].max()

    note_density = note_on_count / tick_count

    # determine if the time signature has an odd numerator
    if 'numerator' in df.columns:
        odd_time_signature_count = df[(df['type'] == 'time_signature') & (df['numerator'] % 2 != 0)].shape[0]
    else:
        odd_time_signature_count = 0
    
    overlapping_notes = get_overlapping_notes(df)

    chord_density = overlapping_notes / note_on_count
    
    duration_per_note = unique_note_count / total_duration
    
    tempo_complexity = tempo_deviation / average_tempo
    
    notes_per_second = note_on_count / (total_duration / 1000)
    
    pitch_range = df['note'].max() - df['note'].min()
    
    tempo_change_count = df[df['type'] == 'set_tempo'].shape[0]
    
    max_polyphony = df[df['type'] == 'note_on'].groupby('tick').size().max()
    
    note_transitions =  note_transition(df)
    return {
      'file': str(filepath).split('\\')[1],
      'average_tempo': average_tempo,
      'average_bpm': average_bpm,
      'note_count': note_on_count,
      'tick_count': tick_count,
      'note_density': note_density,
      'tempo_deviation': tempo_deviation,
      'unique_note_count': unique_note_count,
      'total_duration': total_duration,
      'overlapping_notes': overlapping_notes,
      'chord_density': chord_density,
      'duration_per_note': duration_per_note,
      'tempo_complexity': tempo_complexity,
      'notes_per_second': notes_per_second,
      'hand_independence': get_hand_independence_score(df),
      'odd_time_signature_count': odd_time_signature_count,
      'consecutive_note_std': get_consecutive_note_std(df),
      'pitch_range': pitch_range,
      'average_polyphony': get_average_polyphony(df),
      'tempo_change_count': tempo_change_count,
      'max_polyphony': max_polyphony,
      'note_to_note_transition': note_transitions[0],
      'note_to_chord_transition': note_transitions[1],
      'chord_to_note_transition': note_transitions[2],
      'chord_to_chord_transition': note_transitions[3]
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

def get_hand_independence_score(df):
    df = df[df['type'] == 'note_on']
    
    grouped = df.groupby('tick')

    independent_ticks = 0
    for _, group in grouped:
        if group['track'].nunique() > 1:
            independent_ticks += 1
    
    total_ticks_with_notes = grouped.ngroups
    
    return independent_ticks / total_ticks_with_notes
    
def get_consecutive_note_std(df):
    note_ons = df[df['type'] == 'note_on'].copy()
    note_ons['tick_diff'] =  note_ons['tick'].diff()
    
    tick_diffs = note_ons['tick_diff'].dropna()
    
    return tick_diffs.std()

def get_average_polyphony(df):
    note_ons = df[df['type'] == 'note_on']
    grouped = note_ons.groupby('tick').size()
    return grouped.mean()
    
def process_directory(file_list):
    """
    Process all CSV files in the given directory and extract features.
    """
    print('getting files...')
    files = list(file_list)
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
    
def note_transition(df):


    # Filter for "note_on" events with velocity > 0 (to exclude note_offs)
    note_df = df[(df["type"] == "note_on") & (df["velocity"] > 0)]

    # Group by tick to find notes played simultaneously (i.e., chords)
    grouped = note_df.groupby("tick")["note"].apply(list).reset_index()


    # Helper functions
    def get_type(notes):
        return "chord" if len(notes) > 1 else "note"

    def get_centroid(notes):
        return sum(notes) / len(notes)

    # Calculate weighted intervals between events
    note_to_note = 0
    note_to_chord = 0
    chord_to_note = 0
    chord_to_chord = 0

    for i in range(len(grouped) - 1):
        current_notes = grouped.iloc[i]["note"]
        next_notes = grouped.iloc[i + 1]["note"]

        current_type = get_type(current_notes)
        next_type = get_type(next_notes)

        current_centroid = get_centroid(current_notes)
        next_centroid = get_centroid(next_notes)

        interval = abs(next_centroid - current_centroid)

        if current_type == "note":
            if next_type == "note":
                note_to_note += interval
            else:
                note_to_chord += interval
        else:
            if next_type == "note":
                chord_to_note += interval
            else:
                chord_to_chord += interval


    return note_to_note, note_to_chord, chord_to_note, chord_to_chord


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract features from CSV files present in a directory")
    parser.add_argument("directory", type=str, help="Directory containing CSV files")
    parser.add_argument(
        "--output", 
        "-o", 
        type=str, 
        default="features(2).csv", 
        help="Output CSV file for features"
    )
    parser.add_argument(
        "--recursive",
        "-r",
        action='store_true',
        help="Whether to search recursively in subdirectories"
    )
    parser.add_argument(
        "--filepath",
        type=str,
        help="Path to a file that lists CSV files to process",
    )
    args = parser.parse_args()
    features = []
    if args.filepath:
        with open(args.filepath, 'r', encoding="utf-8") as f:
            file_list = [os.path.join(args.directory, line.strip()) for line in f.readlines()]
    else:
        file_list = list(get_files_in_directory(args.directory, args.recursive))
    
    try:
        features = process_directory(file_list)
    except Exception as e:
        print(f"Error processing files: {e}")
    finally:
        if features:
            df = pd.DataFrame(features)
            df.to_csv(f"{args.output}", index=False)
        else:
            print("No features found")
            

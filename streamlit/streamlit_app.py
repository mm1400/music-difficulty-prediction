import streamlit as st

import pandas as pd

from mido import MidiFile

import pickle

from AveragingModels import AveragingModels

import csv_processing
import convert_midi_to_csv as convert

st.title("Piano Music Difficult Prediction")
st.write(
    "A tool to let you know what you should play next"
)

midi = st.file_uploader("Choose a file in midi format", type = ["mid","midi"])

if midi != None:
    
    st.write("Filename:", midi.name)

    # Rewind to start in case it was read already
    midi.seek(0)

    # Load MIDI directly from file-like object
    mid = MidiFile(file=midi)

    # Convert to CSV (as DataFrame)
    csv = pd.DataFrame(convert.mid_to_csv(mid))
    csv = csv.reset_index()

    st.write(csv)
    

    df = pd.DataFrame(csv_processing.get_features(csv), index=[0])

    st.write("Features extracted:")
    st.write(df)

    features_kept = ['note_count', 'note_density', 'unique_note_count', 'notes_per_second',
       'pitch_range', 'tempo_change_count', 'note_to_note_transition',
       'note_to_chord_transition', 'chord_to_note_transition',
       'chord_to_chord_transition']

    df = df.loc[:, features_kept]
    



    with open('models/averaged_models.pkl', 'rb') as file:
        averaged_models = pickle.load(file)

    st.write("Predicted difficult level")
    st.write(averaged_models.predict(df))


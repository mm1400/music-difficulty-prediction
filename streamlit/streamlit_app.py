import streamlit as st

import convert_midi_to_csv as convert

from mido import MidiFile




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
    csv = convert.mid_to_csv(mid)

    st.write(csv)



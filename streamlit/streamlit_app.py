import streamlit as st

import convert_midi_to_csv as convert

st.title("Piano Music Difficult Prediction")
st.write(
    "A tool to let you know what you should play next"
)

midi = st.file_uploader("Choose a file in midi format", type = ["mid","midi"])

if midi != None:
    
    st.write("Filename:", midi.name)

    # Save the uploaded file temporarily to disk
    filename = f"saved_{midi.name}"
    with open(filename, "wb") as f:
        f.write(midi.read())


    # Convert the midi file to a CSV DataFrame
    csv = convert.mid_to_csv(filename)

    # Display the CSV DataFrame
    st.write(csv)


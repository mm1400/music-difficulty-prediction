import pickle

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score

import random

from AveragingModels import AveragingModels
import csv_processing
import convert_midi_to_csv as convert
import streamlit as st
import pandas as pd


class streamlit:
    def __init__(self):
        self.predcsv = pd.read_csv("predictions.csv")

        self.midi = None
        self.submit = False
        self.selected = "Select an option"



    def display_title(self):
        """
        Display the header
        """
        st.title("Scale Up")
        st.subheader("A tool to let you know what you should play next")
        st.write(
            "A tool to let you know what you should play next"
        )



    def display_uploader(self):
        """
        Display the place to upload the midi file
        """
        self.midi = st.file_uploader("Choose a file in midi format", type = ["mid","midi"])




    def display_selector(self):
        """
        Display the selector 
        """
        #selector
        csv = self.predcsv["file"].tolist()

        k = [x[:-4] for x in csv]
        options = ["Select an Option"] + k
        
        

        st.write("Or alternatively, choose what you last played!")
        self.selected = st.selectbox("Pieces:", options)





    def display_button(self):
        """
        Show the submit button
        """
        self.submit = st.button("Submit")



    def process_midi_uploaded(self):
        """
        Process and output the difficulty level of the piece of the midi uploaded
        """

        st.write("Filename:", self.midi.name)

        # Rewind to start in case it was read already
        self.midi.seek(0)

        # Load MIDI directly from file-like object
        mid = MidiFile(file=self.midi)

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
        


        with open('./models/averaged_models.pkl', 'rb') as file:
            averaged_models = pickle.load(file)

        df = averaged_models.scaler.transform(df)

        self.difficulty_predicted = averaged_models.predict(df)
        st.markdown(f"**Predicted difficult level: {self.difficulty_predicted[0]}**")




    def process_selected(self):
        """
        Process and output the difficulty level of the piece selected
        """
        st.write("Name of Piece:", self.selected)
        self.difficulty_predicted = self.predcsv.loc[self.predcsv['file'] == self.selected + ".csv", 'predicted_difficulty'].iloc[0]
        st.markdown(f"**Predicted difficult level: {self.difficulty_predicted}**")



    def make_recommendations(self):
        """
        Make the recommendations of pieces based on the difficulty of the submitted piece
        The recommendations comes from predictions.csv
        """
        recommendations = pd.read_csv("predictions.csv")

        self.recommendation_list = []
        while len(self.recommendation_list) != 3:
            piece = recommendations.iloc[random.randint(0,len(recommendations))]
            if self.difficulty_predicted - 0.3 < piece["predicted_difficulty"] < self.difficulty_predicted + 0.5:
                self.recommendation_list.append(piece)

    def display_difficulty_ranges(self):
        """
        Display a list of songs grouped by difficulty ranges.
        """
        st.markdown("### Browse Songs by Difficulty Range")

        # Load predictions if not already loaded
        df = self.predcsv.copy()

        # Define ranges
        difficulty_ranges = [
            (1.0, 1.5),
            (2.0, 2.5),
            (3.0, 3.0),
            (3.5, 3.5),
            (4.0, 4.5),
            (5.0, 5.0)
        ]

        for low, high in difficulty_ranges:
            if low == high:
                label = f"Difficulty {low}"
            else:
                label = f"Difficulty {low}-{high}"

            filtered = df[(df["predicted_difficulty"] >= low) & (df["predicted_difficulty"] <= high)]
            
            if not filtered.empty:
                with st.expander(label):
                    for _, row in filtered.iterrows():
                        st.write(f"{row['file'][:-4]} — Difficulty: {row['predicted_difficulty']:.2f}")
            else:
                with st.expander(label):
                    st.write("No songs in this range.")

    def display_recommendations(self):
        """
        Display the recommendations
        """
        st.write("")
        st.markdown("### Here are some pieces recommended for you")
        for p in self.recommendation_list:
            st.write(f"{p["file"][:-4]}, Difficulty: {p["predicted_difficulty"]:.2f}")


    def display_everything(self):
        """
        Display everything that needs to be displayed
        """
        self.display_title()
        self.display_uploader()
        self.display_selector()
        self.display_button()
        self.display_difficulty_ranges()

        if self.submit:
            if self.midi != None:
                self.process_midi_uploaded()
                self.make_recommendations()
                self.display_recommendations()

            elif self.selected !="Select an Option":
                self.process_selected()
                self.make_recommendations()
                self.display_recommendations()
                
            else:
                self.submit = False
                st.write("Please select an option or upload a midi file before submitting.")


            

#run the stuff

if 'app' not in st.session_state:
    st.session_state.app = streamlit()

st.session_state.app.display_everything()





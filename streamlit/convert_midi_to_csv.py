#Code retrieved from https://www.kaggle.com/datasets/vincentloos/classical-music-midi-as-csv

import os
import pandas as pd
from mido import MidiFile, MetaMessage, Message, MidiTrack

# Function to convert a MIDI file to a CSV file.
def mid_to_csv(mid) -> None:
    """Convert a midi file to a csv file"""
    df = pd.DataFrame()

    for n_track, track in enumerate(mid.tracks):
        track_df = pd.DataFrame()
        time = 0

        # place all midi messages into a dataframe
        for msg in track:
            msg_dict = msg.__dict__
            msg_dict["meta"] = int(isinstance(msg, MetaMessage))
            msg_dict["track"] = n_track

            if "time" not in msg_dict:
                continue

            time += int(msg_dict["time"])
            msg_dict["tick"] = time

            # delete redundant keys
            for k in ["name", "text"]:
                if k in msg_dict:
                    del msg_dict[k]

            track_df = pd.concat(
                [track_df, pd.DataFrame([msg_dict])], ignore_index=True
            )

        # merge song dataframe with track dataframe
        if df.shape[0] > 0:
            df = pd.merge(df, track_df, how="outer")
        else:
            df = track_df

    for col in df.columns:
        if df[col].dtype == "float64":
            df[col] = df[col].astype("Int64")

    df.set_index("tick", inplace=True)
    df.sort_index(inplace=True)

    return df
# Music Difficulty Prediction

This is a music difficulty prediction regression based model. We ensemble XGboost and Randomforest in averaged model.

Try it yourself: https://scaleup.streamlit.app/

We sourced our data from:
- Midi to csv data: https://www.kaggle.com/datasets/vincentloos/classical-music-midi-as-csv
- Difficulty data used: https://www.pianolibrary.org/

## Setup instructions


### Setup venv 
`python -m venv .venv`
### Install dependencies
- `pip install -r requirements.txt`
- `cd streamlit && pip install -r requirements.txt`

## File structure
- `/models` includes the trained models and our final model `averaged_models.pkl` used in streamlit.
- `/data/` includes the parsed csv files used throuhgout our app
- `/model_params.json` holds the hyperparemeters used in each model for the `model` notebook
  
## How to run

### Processing the data

After completing setup from below...

- Download the dataset from kaggle: https://www.kaggle.com/datasets/vincentloos/classical-music-midi-as-csv
- Put the ALL folder in the root of repo.
- `py csv_processing.py --filepath data/song_to_process.txt all` outputs to data/features.csv
- `py data/map_features_to_difficulty.py` This associates difficulty to each of the songs in `features.csv`. Outputs to `data/features_difficulty_merged.csv`
- Then run the `data_visualization` notebook. This will get you graphs and output to `data/processed.csv`
  
### Training the model

- Run the `model` notebook which uses `data/processed.csv` included by default in repo.
- This will tune the hyperparameters of each model used and train each model.
- Our final used model for streamlit is `models/averaged_models.pkl`

### Running Streamlit

`streamlit run streamlit/streamlit_app.py`


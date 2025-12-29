import os
from kaggle.api.kaggle_api_extended import KaggleApi

os.environ["KAGGLE_USERNAME"] = "nw3cheng"
os.environ["KAGGLE_KEY"] = "KGAT_4229292ebf44621036b8e8372590b1cd"

api = KaggleApi()
api.authenticate()

api.dataset_download_files('andrewmvd/sp-500-stocks', path='data', unzip=True)


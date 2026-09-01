from multiprocessing import Process
import os
from datacollector import DataCollectAndUpdate
from timedecayupdater import update_time_decay
from sentimentupdater import update_sentiment
from impactupdater import update_impact
from riskclassifier import update_risk_category
import subprocess

def data_processing():
    DataCollectAndUpdate()
    update_time_decay()
    update_sentiment()
    update_impact()
    update_risk_category()

def main():
    data_processing_process = Process(target=data_processing)
    data_processing_process.start()
    data_processing_process.join()
    subprocess.run(["streamlit", "run", "app/streamlitapp.py"],check=True)


if __name__ == "__main__":
    main()
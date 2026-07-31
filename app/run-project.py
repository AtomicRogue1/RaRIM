from multiprocessing import Process
import os
from datacollector import DataCollectAndUpdate
from timedecayupdater import update_time_decay
from sentimentupdater import update_sentiment
from impactupdater import update_impact
import subprocess

def data_processing():
    DataCollectAndUpdate()
    update_time_decay()
    update_sentiment()
    update_impact()

def main():
    data_processing_process = Process(target=data_processing)
    data_processing_process.start()

    try:
        subprocess.run(
            ["streamlit", "run", "app/streamlitapp.py"],
            check=True
        )
    finally:
        data_processing_process.join()


if __name__ == "__main__":
    main()
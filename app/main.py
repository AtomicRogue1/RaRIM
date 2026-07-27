import streamlit as st
from datacollector import DataCollectAndUpdate
from timedecayupdater import update_time_decay
from sentimentupdater import update_sentiment
from impactupdater import update_impact
import threading

def data_stuff():
    DataCollectAndUpdate()
    update_time_decay()
    update_sentiment()
    update_impact()

threading.Thread(target=data_stuff,args=(),kwargs={}).start()

st.title("My First Streamlit App")

st.write("Hello! This is a basic Streamlit application.")

name = st.text_input("Enter your name")

age = st.number_input(
    "Enter your age",
    min_value=0,
    max_value=120
)

if st.button("Submit"):
    st.success(f"Hello {name}! You are {age} years old.")

import streamlit as st

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

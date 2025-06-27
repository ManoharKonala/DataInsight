import streamlit as st

st.title("Test Application")
st.write("This is a test to verify Streamlit is working properly.")
st.write("If you can see this, the server is running correctly.")

# Simple test features
st.header("Basic Features Test")
name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}!")

number = st.slider("Pick a number", 0, 100, 50)
st.write(f"You picked: {number}")

if st.button("Test Button"):
    st.success("Button works!")
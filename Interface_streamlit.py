
# FRONT-END (STREAMLIT) 

import streamlit as st
import requests
import base64
import pandas as pd
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Conexao com Back-end via .env
API_URL = os.getenv("API_URL")

def get_base64_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

image_path = os.path.join(os.path.dirname(__file__), "image", "aviao.jpg")
img_base64 = get_base64_image(image_path)
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
""", unsafe_allow_html=True)

#LOGIN
USUARIO = os.getenv ("LOGIN_USER")
SENHA = os.getenv ("LOGIN_PASSWORD")

params = st.query_params
if "auth" not in params or params["auth"][0] != "1":
    st.title("Login")
    user = st.text_input("User")
    password = st.text_input("Password", type="password")
    if st.button("Enter"):
        if user == USUARIO and password == SENHA:
            st.query_params["auth"] = "1"
            st.rerun()
        else:
            st.error("Incorrect username or password.")
    st.stop()

st.title("Part Registration")


with st.form("part_form"):
    part_name = st.text_input("Part Name")
    manufacturer = st.text_input("Manufacturer")
    sector = st.text_input("Application Sector")
    aircraft = st.text_input("Aircraft")
    quantity = st.number_input("Quantity", step=1, min_value=0)
    value = st.number_input("Value", format="%.2f", min_value=0.0)
    submit = st.form_submit_button("Register")

    if submit:
        if all([part_name, manufacturer, sector, aircraft, quantity, value]):
            response = requests.post(API_URL, json={
                "part_name": part_name,
                "manufacturer": manufacturer,
                "application_sector": sector,
                "aircraft": aircraft,
                "quantity": quantity,
                "value": value
            })
            if response.status_code == 200:
                st.success("Part registered successfully!")
            else:
                st.error(response.json().get("detail", "Error registering part."))
        else:
            st.warning("Please fill in all fields.")

st.header("Registered Parts")

response = requests.get(API_URL)
if response.status_code == 200:
    parts = response.json()
    if parts:
        df = pd.DataFrame(parts)
        df = df.rename(columns={
            "part_name": "Part Name",
            "manufacturer": "Manufacturer",
            "application_sector": "Sector",
            "aircraft": "Aircraft",
            "quantity": "Quantity",
            "value": "Value"
        })
        st.dataframe(df)
    else:
        st.info("No parts registered yet.")
else:
    st.error("Error loading parts.")
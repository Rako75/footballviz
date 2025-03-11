import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('df_BIG2025.csv', delimiter=';', encoding='latin1')

st.title("Football Statistics Dashboard")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("df_BIG2025.csv")  # Remplacez par votre fichier

st.title("Football Statistics Dashboard")


# Count the number of players based on playing positions
position_count = df['Position'].value_counts().reset_index()
position_count.columns = ['Position', 'Count']

# Create a donut chart for playing positions
fig = go.Figure(go.Pie(labels=position_count['Position'], values=position_count['Count'], hole=0.3, name='Playing Positions'))
fig.update_layout(title_text=f'Donut Chart for Playing Positions', showlegend=True)


# Display the donut chart
st.plotly_chart(fig)















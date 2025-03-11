import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv("df_BIG2025.csv")  # Remplacez par votre fichier

st.title("Football Statistics Dashboard")


# Calculate the total number of yellow and red cards for each club
discipline_by_club = df.groupby('Équipe')[['Cartons jaunes', 'Cartons rouges']].sum().reset_index()

# Calculate a total discipline score for each club (sum of yellow and red cards)
discipline_by_club['DisciplineScore'] = discipline_by_club['Cartons jaunes'] + discipline_by_club['Cartons rouges']

# Create a treemap
fig = px.treemap(discipline_by_club, 
                 path=['Équipe'],
                 values='DisciplineScore',
                 title='Club Discipline - Treemap',
                 labels={'Équipe': 'Club', 'DisciplineScore': 'Discipline Score'})

# Customize the layout for better readability
fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))

# Display the treemap
st.plotly_chart(fig)
















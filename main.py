import streamlit as st
import pandas as pd
import numpy as np
import requests, os
from scipy.io import loadmat

def requestCoordinates(query):
    url = 'https://nominatim.openstreetmap.org/search'

    params = dict(
        q = query,
        format = 'geocodejson',
        countrycodes = 'de',
        limit = 1
    )

    resp = requests.get(url=url, params=params)
    lon, lat = resp.json()['features'][0]['geometry']['coordinates']
    return lon, lat

st.title('Starkniederschlagshöhen und Starkniederschlagsspenden nach KOSTRA2020')

@st.cache_data
def load_data():
    return loadmat('data/KOSTRA_2020_data.mat')['data'], loadmat('data/KOSTRA_2020_chords.mat')['data']

kostraData, chordSheme = load_data()
query = ''

query = st.text_input('Ort eingeben')

if query != '':
    filename = 'KOSTRA_2020_' + str(query)
    lon, lat = requestCoordinates(query)

    index = np.argmin(np.sum((chordSheme - np.array([[lon,lat]]))**2,axis=1))
    st.write('Rasterkoordinaten: ' + str(chordSheme[index,:]))
    
    # Show the map
    st.write('Kartenansicht:')
    st.map(pd.DataFrame(data=[[lat,lon]], columns=['lat','lon']))
    
    duration = ['5 min','10 min','15 min','20 min','30 min','45 min','60 min','90 min','2 h','3 h','4 h','6 h','9 h','12 h','18 h','24 h','48 h','72 h','96 h','120 h','144 h','168 h']
    returnPeriod = ['1 a','2 a','3 a','5 a','10 a','20 a','30 a','50 a','100 a']

    option = st.selectbox(
        'Auswahl der Datengrundlage:',
        ('Bemessungsniederschlag in mm', 'Bemessungsspende in L/s/ha', 'Unsicherheit in %')
    )

    if option == 'Bemessungsniederschlag in mm': k = 0
    elif option == 'Bemessungsspende in L/s/ha': k = 9
    elif option == 'Unsicherheit in %': k = 18

    # Create the Pandas DataFrame of the selected location
    df = pd.DataFrame(data=kostraData[:,index,k:k+9], index=duration, columns=returnPeriod)
    
    # Preview the data
    st.write('Vorschau der generierten Daten:')
    st.dataframe(df, use_container_width=True)
    
    # Create the CSV-Download button
    csv = df.to_csv(sep=';', decimal=',').encode('utf-8')
    st.download_button(
        label = "Download data as CSV",
        data = csv,
        file_name = filename + '.csv',
        mime ='text/csv',
    )

st.write('Quelle: https://www.dwd.de/DE/service/copyright/copyright_node.html')
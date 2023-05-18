import streamlit as st
import pandas as pd
import numpy as np
import requests, os
from scipy.io import loadmat
import plotly.express as px

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

st.set_page_config(
    page_title='KOSTRA - WebApp',
    page_icon='🌧️',
    layout='centered'
)

st.title(' DWD KOSTRA 2020')
st.header('Starkniederschlagshöhen und Starkniederschlagsspenden')

@st.cache_data
def load_data():
    return loadmat('data/KOSTRA_2020_data.mat')['data'], loadmat('data/KOSTRA_2020_chords.mat')['data']

kostraData, chordSheme = load_data()
query = ''

query = st.text_input('Orts-/Adressangabe:')

if query != '':
    filename = 'KOSTRA_2020_' + str(query)
    lon, lat = requestCoordinates(query)

    index = np.argmin(np.sum((chordSheme[:,12:14] - np.array([[lon,lat]]))**2,axis=1))
    latCenter, lonCenter = chordSheme[index,12:14]
    raster = chordSheme[index,4:12].reshape(4,2)
    index_rc = chordSheme[index,0]
    
    st.markdown('**Koordinaten:**')
    st.write('%.4f , %.4f'%(lat,lon))
    st.write('INDEX_RC: %i' % (int(index_rc)))

    # Show the map
    st.subheader('Kartenansicht:')
    st.map(pd.DataFrame(data=np.append(raster,np.array([[lon,lat]]),axis=0), columns=['lon','lat']))
    
    duration = ['5 min','10 min','15 min','20 min','30 min','45 min','60 min','90 min','2 h','3 h','4 h','6 h','9 h','12 h','18 h','24 h','48 h','72 h','96 h','120 h','144 h','168 h']
    duration2 = [5,10,15,20,30,45,60,90,120,180,240,360,540,720,1080,1440,2880,4320,5760,7200,8640,10080]
    returnPeriod = ['1 a','2 a','3 a','5 a','10 a','20 a','30 a','50 a','100 a']

    st.subheader('Auswahl der Datengrundlage:')
    option = st.selectbox(
        label='Auswahl der Datengrundlage:', 
        options=('Bemessungsniederschläge [mm]', 'Bemessungsspende [L/s/ha]', 'Unsicherheit [%]'), 
        label_visibility='collapsed'
        )
    
    k=0
    if option == 'Bemessungsniederschläge [mm]': k = 0
    elif option == 'Bemessungsspende [L/s/ha]': k = 9
    elif option == 'Unsicherheit [%]': k = 18

    # Create the Pandas DataFrame of the selected location
    df = pd.DataFrame(data=kostraData[:,index,k:k+9], index=duration, columns=returnPeriod)
    df2 = pd.DataFrame(data=kostraData[:,index,k:k+9], index=duration2, columns=returnPeriod)
    
    # Preview the data
    st.subheader('Darstellung der %s über Andauer- und Wiederkehrzeit:'%(option))
    st.dataframe(df, use_container_width=True)
    
    # Create the CSV-Download button
    csv = df.to_csv(sep=';', decimal=',').encode('utf-8')
    st.download_button(
        label = "Download als CSV",
        data = csv,
        file_name = filename + '.csv',
        mime ='text/csv',
    )
    
    # Additional graphs
    st.subheader("Grafische Darstellung")
    
    checkboxLog = st.checkbox('Logarithmische Darstellung')
    
    fig = px.line(df2,
                  labels={
                     "value": option,
                     "index": "Niederschlagsdauer in min",
                     "variable": "Wiederkehrzeit (Jahre)"
                     }, 
                  log_x=checkboxLog,
                  title=option, markers=True)
    st.plotly_chart(fig, use_container_width=True)

st.write('Quelle: Deutscher Wetterdienst')
import requests
import pandas as pd
import numpy as np
import streamlit as st
st.title('Population of Mecklenburg Country Census Blocks')

def get_lat_lng(address):
    api_key = st.secrets['GOOGLE_KEY']
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

    # Send request to Google Maps Geocoding API
    response = requests.get(base_url, params={'address': address, 'key': api_key})

    # Parse JSON response
    data = response.json()

    # Extract latitude and longitude
    if data['status'] == 'OK':
        lat_lng = data['results'][0]['geometry']['location']
        latitude = lat_lng['lat']
        longitude = lat_lng['lng']
        return latitude, longitude
    else:
        print("Error:", data['status'])
        return None, None

def getVelocity(y1,y2,dataset):
    # Filter out rows with population greater than 0
    merged_byyear_i = dataset[dataset['population'] > 0]

    # Filter data for each year
    block_pop_y1 = merged_byyear_i[merged_byyear_i['year'] == y1]
    block_pop_y2 = merged_byyear_i[merged_byyear_i['year'] == y2]

    # Calculate population percentage for each year
    block_pop_y1['population_y1'] = block_pop_y1['population']
    block_pop_y2['population_y2'] = block_pop_y2['population']

    # Merge DataFrames on 'block' column
    merged_blocks = block_pop_y2.merge(block_pop_y1[['block', 'population_y1']], on="block")

    # Calculate velocity
    merged_blocks['vel'] = merged_blocks['population_y2'] - merged_blocks['population_y1']
    #calculate z score of velocity
    merged_blocks['vel_z'] = (merged_blocks['vel'] - np.average(merged_blocks['vel'])) / np.std(merged_blocks['vel'])

    return(merged_blocks)

merged_blocks = pd.read_csv("cencus_block_population_by_year.csv")
block_velos = getVelocity(2016,2021,merged_blocks)

# Example usage
address = st.text_input("Address",value="2705 Haverford Pl")
latitude, longitude = get_lat_lng(address)
if latitude is not None and longitude is not None:
    input_address = np.array([latitude, longitude])
block_velos['lookup_distance'] = block_velos.apply(lambda row: np.linalg.norm(row[['lat', 'long']].values - input_address), axis=1)
st.subheader(block_velos.loc[block_velos['lookup_distance'].idxmin()][['block','vel_z']].values)


    
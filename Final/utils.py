import folium
import requests
import pandas as pd
import numpy as np
import config
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

def change_neighborhood_name(name, change_name_dict):
    for key in change_name_dict.keys():
        if name in change_name_dict[key]:
            return key   
    return name


def draw_neigborhoods_map(location, df, cluster_colors=None):
    n_map = folium.Map(location=location, zoom_start=10, tiles='Stamen Terrain')
    if cluster_colors:
        for neighbor, lat, lng, cluster in zip(df['Neighborhood'], df['Latitude'], df['Longitude'], df['Cluster']):
            folium.CircleMarker(
                location = (lat, lng),
                radius=15,
                popup=f"{neighbor}",
                fill = True,
                fill_color=cluster_colors[cluster],
                fill_opacity=0.8

            ).add_to(n_map)     
    else:
        for neighbor, lat, lng in zip(df['Neighborhood'], df['Latitude'], df['Longitude']):
            folium.Marker(
                location = (lat, lng),
                popup=f"{neighbor}"
            ).add_to(n_map)
    return n_map



# Define Foursquare Credentials and Version
CLIENT_ID = config.CLIENT_ID # your Foursquare ID
CLIENT_SECRET = config.CLIENT_SECRET # your Foursquare Secret
VERSION = '20180605' # Foursquare API version
LIMIT = 100 # A default Foursquare API limit value


def getNearbyVenues(names, latitudes, longitudes, radius=750):
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            config.CLIENT_ID, 
            config.CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results if v['venue']['categories'][0]['name'] != 'Neighborhood'])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


def return_n_most_common_venues(df_grouped, num_top_venues):
    #function to sort the venues in descending order
    def return_most_common_venues(row, num_top_venues):
        row_categories = row.iloc[1:]
        row_categories_sorted = row_categories.sort_values(ascending=False)

        return row_categories_sorted.index.values[0:num_top_venues]
    indicators = ['st', 'nd', 'rd']

    # create columns according to number of top venues
    columns = ['Neighborhood']
    for ind in np.arange(num_top_venues):
        try:
            columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
        except:
            columns.append('{}th Most Common Venue'.format(ind+1))

    # create a new dataframe
    neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
    neighborhoods_venues_sorted['Neighborhood'] = df_grouped['Neighborhood']

    for ind in np.arange(df_grouped.shape[0]):
        neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(df_grouped.iloc[ind, :], num_top_venues)

    return neighborhoods_venues_sorted


def plot_barchart(df, x, y, xlabel=None, ylabel=None, title=''):
    fig, ax = plt.subplots(figsize=(15,10))
    plot = sns.barplot(x = x, y = y, data = df.sort_values(y, ascending=False),ax=ax)

    for item in plot.get_xticklabels():
        item.set_rotation(90)
    if xlabel: 
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    plt.title(title)
    plt.show()
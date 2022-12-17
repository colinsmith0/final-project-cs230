'''
Name: Colin Smith
Class: CS230-5
Project Description: An online and interactive web page that allows the user to learn more about the world's volcanoes.
'''


# import modules

import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import random

# read csv file with pandas as a dataframe

VOLCANOES = "volcanoes.csv"
volcano_file = open(VOLCANOES, "r", encoding="utf-8-sig")
volcano_df = pd.read_csv(VOLCANOES)
volcano_file.close()

# rename columns for mapping purposes

volcano_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}, inplace=True)

# volcano icon for the map

ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/e/e8/Volcano_icon.png"
icon_data = {
    "url": ICON_URL,
    "width": 100,
    "height": 100,
    "anchorY": 100
}

# checks if a cell is empty

def isEmpty(value):
    emptiness = pd.isna(value)
    return emptiness

# takes date from csv file and turns it into a float value so that it can be used in a slider

def volcanodater(volc):
    date = 0
    if volc != "Unknown":
        volc = volc.split(" ")
        if volc[1] == "BCE":
            date = float("-" + volc[0])
        elif volc[1] == "CE":
            date = float(volc[0])
    else:
        return "Unknown"
    return date

# add icon data column and replace empty cells with N/A
# if a cell has an unknown eruption date exclude it from the slider list

date_list = []

volcano_df["icon_data"] = None
for i in volcano_df.index:
    volcano_df["icon_data"][i] = icon_data
    if isEmpty(volcano_df["Dominant Rock Type"][i]):
        volcano_df["Dominant Rock Type"][i] = "N/A"
    if isEmpty(volcano_df["Tectonic Setting"][i]):
        volcano_df["Tectonic Setting"][i] = "N/A"
    if volcanodater(volcano_df["Last Known Eruption"][i]) != "Unknown":
        date_list.append(volcano_df.iloc[i])

# create lists for dropdown menus

type_list = [" "]
dominant_list = [" "]
tectonic_list = [" "]
for x in volcano_df.index:
    if volcano_df["Primary Volcano Type"][x] not in type_list:
        type_list.append(volcano_df["Primary Volcano Type"][x])
    if volcano_df["Dominant Rock Type"][x] not in dominant_list:
        dominant_list.append(volcano_df["Dominant Rock Type"][x])
    if volcano_df["Tectonic Setting"][x] not in tectonic_list:
        tectonic_list.append(volcano_df["Tectonic Setting"][x])

# list comprehension for dropdown menus

sorted_type_list = sorted((i for i in type_list))
sorted_dominant_list = sorted((i for i in dominant_list if i != "N/A"))
sorted_tectonic_list = sorted((i for i in tectonic_list if i != "N/A"))

# map title

st.title("Map of the World's Volcanoes")

# dropdown menus on sidebar

type_select = st.sidebar.selectbox("Select a Primary Volcano Type", sorted_type_list)
dominant_select = st.sidebar.selectbox("Select a Dominant Rock Type", sorted_dominant_list)
tectonic_select = st.sidebar.selectbox("Select a Tectonic Setting", sorted_tectonic_list)

# create new dataframe that has dated volcanoes in correct format
# create the slider for dates and format the output

date_df = pd.DataFrame(date_list)
for v in date_df.index:
    date_df["Last Known Eruption"][v] = volcanodater(date_df["Last Known Eruption"][v])
mindate = min(date_df["Last Known Eruption"])
maxdate = max(date_df["Last Known Eruption"])
datevalues = st.sidebar.slider('Select a range of dates (negative denotes BCE)', mindate, maxdate, (mindate, maxdate))
st.write('Volcanoes that last erupted in this date range:', datevalues)
datevalues = str(datevalues).replace("(", "")
datevalues = datevalues.replace(")", "")
datevalues = datevalues.replace(",", "")
datevalues = (str(datevalues)).split(" ")

# remove volcanoes from the dataframe if they are outside the slider range

for v in date_df.index:
    if date_df["Last Known Eruption"][v] < float(datevalues[0]) or date_df["Last Known Eruption"][v] > float(
            datevalues[1]):
        date_df.drop(v, inplace=True)

# restrict dataframe based on user dropdown input

if type_select != " ":
    date_df = date_df[date_df["Primary Volcano Type"] == type_select]
if dominant_select != " ":
    date_df = date_df[date_df["Dominant Rock Type"] == dominant_select]
if tectonic_select != " ":
    date_df = date_df[date_df["Tectonic Setting"] == tectonic_select]

# add map layer with icon data and filtered dataframe

icon_layer = pdk.Layer(type="IconLayer", data=date_df, get_icon="icon_data", get_position="[lon,lat]",
                       get_size=4, size_scale=10, pickable=True)

# create map in pydeck using view state, tool tip, and icon map

st.write(f"There are {len(date_df)} volcanoes that meet this criteria.")
view_state = pdk.ViewState(
    latitude=volcano_df["lat"].mean(),
    longitude=volcano_df["lon"].mean(),
    zoom=1,
    pitch=0)
tool_tip = {"html": "Volcano Name:<br/> <b>{Volcano Name}</b>",
            "style": {"backgroundColor": "orange",
                      "color": "white"}}
icon_map = pdk.Deck(
    map_style="mapbox://styles/mapbox/navigation-day-v1",
    layers=[icon_layer],
    initial_view_state=view_state,
    tooltip=tool_tip)
st.pydeck_chart(icon_map)

# create histogram that displays volcanoes by their elevation

fig, ax = plt.subplots()
ax.hist(volcano_df["Elevation (m)"].values, bins=20, ec="black")
ax.set_xlabel("Elevation in meters")
ax.set_ylabel("Volcanoes")
ax.set_title("Histogram of Volcano Elevation")
st.pyplot(fig)

# create bar chart that totals the number of volcanoes in each region

volcano_regions = volcano_df.groupby(by=["Region"]).count()
fig, ax = plt.subplots()
number_of_colors = len(volcano_regions)
color = ["#" + ''.join([random.choice('0123456789ABCDEF') for c in range(6)]) for i in range(number_of_colors)]
ax.bar(volcano_regions.index, volcano_regions.iloc[:, 1], label=volcano_regions.index, color=color)
ax.legend(title="Region", loc="upper left", bbox_to_anchor=(1.05, 1.0))
plt.xticks([])
ax.set_ylabel("Volcanoes")
ax.set_title("Volcanoes by Region")
st.pyplot(fig)

# function that takes a dropdown selection and a dataframe and returns the selected region's total number of volcanoes per country

def region_selector(region, df):
    region_df = df[df["Region"] == region]
    region_countries = region_df.groupby(by=["Country"]).count()
    return region_countries

# creates a dropdown for regions and pie chart for countries with volcanoes in that region if one is selected

volcano_regions_list = [" "]
for r in volcano_regions.index:
    volcano_regions_list.append(r)
selected_region = st.sidebar.selectbox("Select a region for the pie chart", volcano_regions_list)
if selected_region != " ":
    countries = region_selector(selected_region, volcano_df)
    fig, ax = plt.subplots()
    ax.pie(countries.iloc[:, 1], labels=countries.index, autopct="%.1f%%")
    st.pyplot(fig)

# unedited dataframe for user to get specific volcano information

st.write("Detailed data on all volcanoes:")
st.write(volcano_df.iloc[:, :13])

# if the user has had enough of volcanoes, they can press the button for balloons instead

if st.sidebar.button("Press for balloons"):
    st.balloons()

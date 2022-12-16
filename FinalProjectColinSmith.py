import csv
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import random

VOLCANOES = "volcanoes.csv"
volcano_file = open(VOLCANOES, "r", encoding="utf-8-sig")
volcano_dict = list(csv.DictReader(volcano_file))
volcano_df = pd.read_csv(VOLCANOES)
volcano_file.close()
# st.write(volcano_df)
# st.write(volcano_dict)
st.write("ballin")
volcano_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}, inplace=True)

ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/e/e8/Volcano_icon.png"
icon_data = {
    "url": ICON_URL,
    "width": 100,
    "height": 100,
    "anchorY": 100
}


def isEmpty(value):
    emptiness = pd.isna(value)
    return emptiness


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

sorted_type_list = sorted((i for i in type_list))
sorted_dominant_list = sorted((i for i in dominant_list if i != "N/A"))
sorted_tectonic_list = sorted((i for i in tectonic_list if i != "N/A"))

# Mapping Time

st.title("Map of the World's Volcanoes")

type_select = st.selectbox("Select a Primary Volcano Type", sorted_type_list)
dominant_select = st.selectbox("Select a Dominant Rock Type", sorted_dominant_list)
tectonic_select = st.selectbox("Select a Tectonic Setting", sorted_tectonic_list)

date_df = pd.DataFrame(date_list)
for v in date_df.index:
    date_df["Last Known Eruption"][v] = volcanodater(date_df["Last Known Eruption"][v])

mindate = min(date_df["Last Known Eruption"])
maxdate = max(date_df["Last Known Eruption"])

datevalues = st.slider('Select a range of dates (negative denotes BCE)', mindate, maxdate, (mindate, maxdate))
st.write('Volcanoes that last erupted in this date range:', datevalues)
datevalues = str(datevalues).replace("(", "")
datevalues = datevalues.replace(")", "")
datevalues = datevalues.replace(",", "")
datevalues = (str(datevalues)).split(" ")

for v in date_df.index:
    if date_df["Last Known Eruption"][v] < float(datevalues[0]) or date_df["Last Known Eruption"][v] > float(
            datevalues[1]):
        date_df.drop(v, inplace=True)

if type_select != " ":
    date_df = date_df[date_df["Primary Volcano Type"] == type_select]
if dominant_select != " ":
    date_df = date_df[date_df["Dominant Rock Type"] == dominant_select]
if tectonic_select != " ":
    date_df = date_df[date_df["Tectonic Setting"] == tectonic_select]

icon_layer = pdk.Layer(type="IconLayer", data=date_df, get_icon="icon_data", get_position="[lon,lat]",
                       get_size=4, size_scale=10, pickable=True)

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

volcano_regions = volcano_df.groupby(by=["Region"]).count()

fig, ax = plt.subplots()
number_of_colors = len(volcano_regions)
color = ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for i in range(number_of_colors)]
ax.bar(volcano_regions.index, volcano_regions.iloc[:, 1], label=volcano_regions.index, color=color)
ax.legend(title="Region", loc="upper left", bbox_to_anchor=(1.05, 1.0))
plt.xticks([])
ax.set_ylabel("Volcanoes")
ax.set_title("Volcanoes by Region")
st.pyplot(fig)


def region_selector(region, df):
    region_df = df[df["Region"] == region]
    region_countries = region_df.groupby(by=["Country"]).count()
    return region_countries


selected_region = st.sidebar.selectbox("Select a region for the pie chart", volcano_regions.index)

countries = region_selector(selected_region, volcano_df)
fig, ax = plt.subplots()
ax.pie(countries.iloc[:, 1], labels=countries.index, autopct="%.1f%%")

st.sidebar.pyplot(fig)

import folium
import streamlit as st
import pandas as pd
from folium.plugins import FastMarkerCluster
from pathlib import Path
from streamlit_folium import st_folium
from streamlit_dynamic_filters import DynamicFilters

"""
# :material/workspace_premium: Apprenticeship vacancies in England

Explore apprenticeship vacancies across England.  
Data: Tuesday, 24 March 2026 @ 07:18
"""

def get_map(df_locations):
    # Map
    m = folium.Map(
        location=[52.561928, -1.464854],
        tiles="cartodb positron",
        max_bounds=True,
        min_lat=49.5,
        max_lat=56.0,
        min_lon=-6.5,
        max_lon=2.0,
        zoom_start=7,
    )

    # Markers
    icon_create_function = """\
    function(cluster) {
        return L.divIcon({
        html: '<b>' + cluster.getChildCount() + '</b>',
        className: 'marker-cluster marker-cluster-large',
        iconSize: new L.Point(20, 20)
        });
    }"""

    vacancies = (
        df_locations
        .loc[(~df_locations['longitude'].isnull()) & (~df_locations['longitude'].isnull())]
        .to_dict(orient='records')
    )

    # Data for callback popup
    data = [
        [vacancy['latitude'],
         vacancy['longitude'],
         vacancy['title'],
         vacancy['employerName'],
         vacancy['addressLine1'],
         vacancy['course.title'],
         vacancy['vacancyUrl']] for vacancy in vacancies]

    # Marker Cluster

    callback = """
    function (row) {
        var marker = L.marker(new L.LatLng(row[0], row[1]), {color: "red"});
        var icon = L.AwesomeMarkers.icon({
            icon: 'briefcase',
            iconColor: 'white',
            markerColor: 'green',
            prefix: 'glyphicon',
            extraClasses: 'fa-rotate-0'
        });
        marker.setIcon(icon);
        var popup = L.popup({maxWidth: '300'});

        var card = L.DomUtil.create("div", "job-card");
        card.style.cssText = "background: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); font-family: Arial, sans-serif;";

        var title = L.DomUtil.create("h3", "job-title", card);
        title.textContent = row[2];
        title.style.cssText = "margin: 0 0 10px 0; color: #2c3e50; font-size: 16px; font-weight: bold;";

        var employerRow = L.DomUtil.create("div", "job-detail", card);
        employerRow.style.cssText = "margin-bottom: 8px; display: flex; align-items: center;";
        var employerIcon = L.DomUtil.create("span", "glyphicon glyphicon-briefcase", employerRow);
        employerIcon.style.cssText = "margin-right: 8px; color: #7f8c8d;";
        var employerText = L.DomUtil.create("span", null, employerRow);
        employerText.textContent = row[3];
        employerText.style.cssText = "color: #555; font-size: 13px;";

        var locationRow = L.DomUtil.create("div", "job-detail", card);
        locationRow.style.cssText = "margin-bottom: 8px; display: flex; align-items: center;";
        var locationIcon = L.DomUtil.create("span", "glyphicon glyphicon-map-marker", locationRow);
        locationIcon.style.cssText = "margin-right: 8px; color: #e74c3c;";
        var locationText = L.DomUtil.create("span", null, locationRow);
        locationText.textContent = row[4];
        locationText.style.cssText = "color: #555; font-size: 13px;";

        // Qualification
        var qualRow = L.DomUtil.create("div", "job-detail", card);
        qualRow.style.cssText = "margin-bottom: 12px; display: flex; align-items: center;";
        var qualIcon = L.DomUtil.create("span", "glyphicon glyphicon-education", qualRow);
        qualIcon.style.cssText = "margin-right: 8px; color: #9b59b6;";
        var qualText = L.DomUtil.create("span", null, qualRow);
        qualText.textContent = "Qualification: " + row[5];
        qualText.style.cssText = "color: #555; font-size: 13px; font-weight: 500;";

        var link = L.DomUtil.create("a", "job-link", card);
        link.href = row[6];
        link.textContent = "Vacancy Details";
        link.target = "_blank";
        link.style.cssText = "display: inline-block; background: #3498db; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-size: 13px; font-weight: 500; transition: background 0.2s;";
        link.onmouseover = function() { this.style.background = "#2980b9"; };
        link.onmouseout = function() { this.style.background = "#3498db"; };

        popup.setContent(card);
        marker.bindPopup(popup);
        return marker;
    }
    """


    marker_cluster = FastMarkerCluster(
        data=data,
        name="Vacancies",
        overlay=True,
        control=True,
        icon_create_function=icon_create_function,
        callback=callback,
        options={
            "showCoverageOnHover": False,
            "removeOutsideVisibleBounds": True,
            "maxClusterRadius": 60
        }
    )

    m.add_child(marker_cluster)
    return m

# Data


# 1. Get the directory where the current script is located
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()

# 2. Construct the absolute path to the target file
# Use the '/' operator to join paths
file_path = current_dir / "output" / "vacancies_england_latest.json"
print(file_path)



df = (
    pd.read_json(file_path)
    .loc[
        lambda _df: (~ _df['course.route'].isnull()) &
                    (~ _df['course.title'].isnull()) &
                    (~ _df['employerName'].isnull())
    ]
    .assign(**{
        'postedDate': lambda _df: pd.to_datetime(_df['postedDate'], format='mixed'),
    })
)
# Minimum posted date
date_posted_min = (df['postedDate'].dt.date).min()
print(date_posted_min)

# Page configuration
st.set_page_config(
    page_title="Apprenticeship vacancies in England",
    layout="wide",
    initial_sidebar_state="expanded")

# Filters
dynamic_filters = DynamicFilters(df, filters=['course.route', 'course.title', 'course.level', 'employerName', 'providerName'])
with st.sidebar:

    st.write("Search")
    dynamic_filters.display_filters(location='sidebar')
    # posted_from = st.date_input("Date vacancy posted from", value=None, min_value=date_posted_min, max_value="today")



# st.button("Reset Filters", on_click=dynamic_filters.reset_filters)

# Map
f_map = get_map(dynamic_filters.filter_df())
st_data = st_folium(f_map, width=725)

# Display Dataframe
st.dataframe(dynamic_filters.filter_df())
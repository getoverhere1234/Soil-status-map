import streamlit as st
import folium
import pandas as pd
from streamlit_folium import folium_static
from PIL import Image
import io
import base64

def add_click_events(map_object):
    """Add click events to the Folium map to display coordinates."""
    map_object.add_child(folium.ClickForMarker(popup="Click to add a marker"))

def display_legend():
    """Display legend for the codes."""
    st.sidebar.markdown(
        """
        <div style='border: 2px solid darkblue; padding: 10px;'>
            <h3 style='text-align: center; color: Black;'>Code Interpreter</h3>
            <ul>
                <li><b>Code 1</b>: Low pH, N, Zn and Mn</li>
                <li><b>Code 2</b>: Low pH, Zn and Mn</li>
                <li><b>Code 3</b>: Low pH, N and Mn</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


def main():
    #st.title("Soil Status Map")
    st.markdown("<h1 style='text-align: center; color: darkblue; font-family: Arial; font-weight: bold;'><b>SOIL STATUS MAP</b></h1>", unsafe_allow_html=True)
    #st.markdown("<h3 style='text-align: center; color: darkblue; font-family: Arial; font-style: italic; font-weight: bold;'>Designed and engineered by Dr. Watitemjen</h3>", unsafe_allow_html=True)
    # Set background color
    st.markdown(
        """
        <style>
        body {
            background-color: black;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # File uploader widget for the main CSV file
    uploaded_file_main = st.file_uploader("Choose the main CSV file", type=["csv"])

    if uploaded_file_main is not None:
        # Read data from the main uploaded CSV file
        main_data = pd.read_csv(uploaded_file_main)

        # Check if the required columns are present
        if 'Latitude' in main_data.columns and 'Longitude' in main_data.columns and 'Code' in main_data.columns:
            # Display legend
            display_legend()

            # Create a base map
            m = folium.Map(location=[main_data['Latitude'].mean(), main_data['Longitude'].mean()], zoom_start=10)

            # Add click events to display coordinates
            add_click_events(m)

            # Add markers to the map based on the main data
            for index, row in main_data.iterrows():
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=f"Coordinates: ({row['Latitude']}, {row['Longitude']})<br>Code: {row['Code']}",
                    icon=folium.Icon(color='red' if row['Code'] == 1 else 'blue' if row['Code'] == 2 else 'green')
                ).add_to(m)

            # Display the map using folium_static
            folium_static(m)

            # File uploader widget for the additional CSV file
            uploaded_file_additional = st.file_uploader("Choose the additional CSV file", type=["csv"])

            if uploaded_file_additional is not None:
                # Read data from the additional uploaded CSV file
                additional_data = pd.read_csv(uploaded_file_additional)

                # Add markers to the map based on the additional data
                for index, row in additional_data.iterrows():
                    marker = folium.CircleMarker(
                        location=[row['Latitude'], row['Longitude']],
                        radius=10,
                        popup=f"sl.no: {row['sl.no']}<br>Coordinates: ({row['Latitude']}, {row['Longitude']})",
                        color='black',
                        fill=True,
                        fill_color='black'
                    )
                    marker.add_to(m)

                # Display the updated map using folium_static
                folium_static(m)

            # Input boxes for manual latitude and longitude
            st.sidebar.header("Add Soil GPS coordinates")
            input_lat = st.sidebar.number_input("Enter Latitude:", value=main_data['Latitude'].mean())
            input_lon = st.sidebar.number_input("Enter Longitude:", value=main_data['Longitude'].mean())

            if st.sidebar.button("Add Marker"):
                folium.Marker(
                    location=[input_lat, input_lon],
                    popup=f"Custom Coordinates: ({input_lat}, {input_lon})",
                    icon=folium.Icon(color='purple', icon='star')
                ).add_to(m)
                folium_static(m)

            # Export options
            export_format = st.selectbox("Select export format:", ["JPG", "PNG"])

            if st.button("Export Map"):
                img_data = m._to_png()
                img = Image.open(io.BytesIO(img_data))

                if export_format == "JPG":
                    img_format = "jpeg"
                    img = img.convert("RGB")
                else:
                    img_format = "png"

                buffered = io.BytesIO()
                img.save(buffered, format=img_format)
                img_str = base64.b64encode(buffered.getvalue()).decode()
                href = f'<a href="data:image/{img_format};base64,{img_str}" download="soil_status_map.{img_format}">Download map</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Map exported successfully!")

        else:
            st.warning("The main uploaded CSV file does not contain the required columns: 'Latitude', 'Longitude', 'Code'.")

if __name__ == "__main__":
    main()

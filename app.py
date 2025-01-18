import streamlit as st
from PIL import Image
import pytesseract
from pyproj import Proj, transform
import os
import folium
import re
from streamlit.components.v1 import html

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_coordinates(image_path):
    """Extract Northing and Easting coordinates from the image using OCR."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        st.write("Extracted Text:\n", text)  # Display extracted text in Streamlit
        
        pattern = r"(\d{7}\.\d+)\s+(\d{6}\.\d+)"
        matches = re.findall(pattern, text)
        
        coordinates = [(float(northing), float(easting)) for northing, easting in matches]
        return coordinates
    except Exception as e:
        st.error(f"Error in extract_coordinates: {e}")
        return []

def convert_to_lat_lon(northing, easting):
    """Convert UTM coordinates to latitude and longitude."""
    try:
        utm_projection = Proj(proj='utm', zone=40, ellps='WGS84', south=False)
        wgs84_projection = Proj(proj='latlong', datum='WGS84')
        lon, lat = transform(utm_projection, wgs84_projection, easting, northing)
        return lat, lon
    except Exception as e:
        st.error(f"Error in convert_to_lat_lon: {e}")
        return None, None

def create_map(coordinates, satellite=False):
    """Create a Folium map with the given coordinates."""
    try:
        if not coordinates or None in coordinates[0]:
            raise ValueError("Invalid coordinates")
            
        map_center = coordinates[0]
        st.write("Map Center:", map_center)  # Debug: Print map center
        
        # Create a Folium map
        m = folium.Map(location=map_center, zoom_start=15)

        # Add markers for each coordinate
        for coord in coordinates:
            if None not in coord:
                st.write("Adding Marker:", coord)  # Debug: Print each marker
                folium.Marker(location=coord).add_to(m)

        # Add satellite tile layer if requested
        if satellite:
            folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Esri',
                name='Satellite',
                overlay=False,
                control=True
            ).add_to(m)

        # Add a layer control to toggle between map views
        folium.LayerControl().add_to(m)

        # Save the map to an HTML file
        map_file = "map.html"
        m.save(map_file)

        # Read the HTML file and display it in Streamlit
        with open(map_file, "r", encoding="utf-8") as f:
            map_html = f.read()
        
        return map_html
    except Exception as e:
        st.error(f"Error in create_map: {e}")
        return None

def main():
    """Main function for the Streamlit app."""
    st.title("Land Coordinates Extractor")
    st.write("Upload an image of land details to extract coordinates and view them on a map.")

    # Add a toggle for satellite view
    satellite_view = st.checkbox("Enable Satellite View")

    # File uploader
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Save the uploaded file
        image_path = os.path.join("uploaded_image.jpg")
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Extract coordinates
        coordinates = extract_coordinates(image_path)
        if coordinates:
            st.success("Coordinates extracted successfully!")
            #st.write("Extracted Coordinates:", coordinates)

            # Convert coordinates to latitude/longitude
            lat_lon_coordinates = [convert_to_lat_lon(n, e) for n, e in coordinates]
            lat_lon_coordinates = [coord for coord in lat_lon_coordinates if None not in coord]

            if lat_lon_coordinates:
                st.write("Converted Latitude/Longitude:", lat_lon_coordinates)

                # Create and display the map
                st.write("Displaying the map...")
                map_html = create_map(lat_lon_coordinates, satellite=satellite_view)
                if map_html:
                    html(map_html, width=800, height=600)
                else:
                    st.error("Failed to create the map.")
            else:
                st.error("Failed to convert coordinates.")
        else:
            st.error("No coordinates found in the image.")

if __name__ == '__main__':
    main()
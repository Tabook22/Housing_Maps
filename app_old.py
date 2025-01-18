from flask import Flask, request, jsonify, render_template
from PIL import Image
import pytesseract
from pyproj import Proj, transform
import os
import folium
import re

# Get the absolute path to the application directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask with explicit template and static folders
app = Flask(__name__,
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'images'), exist_ok=True)

def extract_coordinates(image_path):
    """Extract Northing and Easting coordinates from the image using OCR."""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        print("Extracted Text:\n", text)
        
        pattern = r"(\d{7}\.\d+)\s+(\d{6}\.\d+)"
        matches = re.findall(pattern, text)
        
        coordinates = [(float(northing), float(easting)) for northing, easting in matches]
        return coordinates
    except Exception as e:
        print("Error in extract_coordinates:", e)
        return []

def convert_to_lat_lon(northing, easting):
    """Convert UTM coordinates to latitude and longitude."""
    try:
        utm_projection = Proj(proj='utm', zone=40, ellps='WGS84', south=False)
        wgs84_projection = Proj(proj='latlong', datum='WGS84')
        lon, lat = transform(utm_projection, wgs84_projection, easting, northing)
        return lat, lon
    except Exception as e:
        print("Error in convert_to_lat_lon:", e)
        return None, None

def create_map(coordinates):
    """Create a Folium map with the given coordinates."""
    try:
        if not coordinates or None in coordinates[0]:
            raise ValueError("Invalid coordinates")
            
        map_center = coordinates[0]
        m = folium.Map(location=map_center, zoom_start=15)

        for coord in coordinates:
            if None not in coord:
                folium.Marker(location=coord).add_to(m)

        map_file = os.path.join(BASE_DIR, 'static', 'map.html')
        m.save(map_file)
        return map_file
    except Exception as e:
        print("Error in create_map:", e)
        return None

@app.route('/', methods=['GET'])
def index():
    """Render the main page."""
    try:
        return render_template('index.html')
    except Exception as e:
        print("Error rendering index:", e)
        return "Error loading page", 500

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        # Save the uploaded file
        image_path = os.path.join(BASE_DIR, 'images', 'uploaded_image.jpg')
        file.save(image_path)

        if not os.path.exists(image_path):
            return jsonify({'error': 'Failed to save image'})

        coordinates = extract_coordinates(image_path)
        if not coordinates:
            return jsonify({'error': 'No coordinates found in image'})

        lat_lon_coordinates = [convert_to_lat_lon(n, e) for n, e in coordinates]
        lat_lon_coordinates = [coord for coord in lat_lon_coordinates if None not in coord]

        if not lat_lon_coordinates:
            return jsonify({'error': 'Failed to convert coordinates'})

        map_file = create_map(lat_lon_coordinates)
        if not map_file:
            return jsonify({'error': 'Failed to create map'})

        return jsonify({
            'success': True,
            'coordinates': lat_lon_coordinates,
            'map_url': '/map'
        })
    except Exception as e:
        print("Error in upload_image:", e)
        return jsonify({'error': str(e)})

@app.route('/map', methods=['GET'])
def show_map():
    """Render the map page."""
    try:
        return render_template('map.html')
    except Exception as e:
        print("Error rendering map:", e)
        return "Error loading map", 500

if __name__ == '__main__':
    # Initialize application directories
    ensure_directories()
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
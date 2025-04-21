from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import folium
from folium import plugins
import ee
import json
from datetime import datetime, timedelta
import logging

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Google Earth Engine
try:
    ee.Initialize(project='ee-deforest-monitor-tool')
    logger.info("Earth Engine initialized successfully")
except Exception as e:
    logger.error("Earth Engine initialization failed: %s", str(e))
    raise

# Constants
VEGETATION_THRESHOLD = 0.2  # Lower threshold to include all vegetation, not just forests
CLOUD_FILTER = 60  # Maximum cloud percentage allowed in images
NDVI_DECREASE_THRESHOLD = 0.1  # Lower threshold to detect more subtle vegetation loss

def mask_clouds(image):
    """Improved cloud masking for Sentinel-2."""
    qa = image.select('QA60')
    # Bits 10 and 11 are clouds and cirrus
    cloud_bit_mask = (1 << 10) | (1 << 11)
    # Both flags should be set to zero, indicating clear conditions
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0)
    return image.updateMask(mask)

def calculate_ndvi(image):
    """Calculate NDVI only."""
    try:
        # NDVI (Normalized Difference Vegetation Index)
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return image.addBands(ndvi)
    except Exception as e:
        logger.warning(f"NDVI calculation failed: {str(e)}")
        return image

def get_year_composite(year, geometry):
    """Create annual composite with proper image handling."""
    try:
        start_date = ee.Date.fromYMD(year, 1, 1)
        end_date = ee.Date.fromYMD(year, 12, 31)
        
        # Use the newer Sentinel-2 SR collection
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterBounds(geometry)
                     .filterDate(start_date, end_date)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CLOUD_FILTER))
                     .select(['B2', 'B3', 'B4', 'B8', 'B12', 'QA60'])
                     .map(mask_clouds)
                     .map(calculate_ndvi))
        
        # Check if the collection is empty
        collection_size = collection.size().getInfo()
        if collection_size == 0:
            logger.warning(f"No images found for year {year} in the specified region")
            return None
        
        # Get the median values for a more stable composite
        return collection.median().clip(geometry)
    except Exception as e:
        logger.error(f"Error creating composite for {year}: {str(e)}")
        return None

def generate_vegetation_loss_map(latitude, longitude, distance, base_year):
    """Generate vegetation loss map with robust data handling."""
    try:
        # Create region of interest
        distance_meters = distance * 1000
        roi = ee.Geometry.Point([longitude, latitude]).buffer(distance_meters)
        
        current_year = datetime.now().year
        
        # Get composites for base year and current year
        base_year_composite = get_year_composite(base_year, roi)
        current_year_composite = get_year_composite(current_year, roi)
        
        # Check if we have valid composites
        if base_year_composite is None:
            raise ValueError(f"No suitable imagery found for base year {base_year}")
        
        if current_year_composite is None:
            raise ValueError(f"No suitable imagery found for current year {current_year}")
        
        # Calculate NDVI difference
        ndvi_diff = current_year_composite.select('NDVI').subtract(
            base_year_composite.select('NDVI')).rename('NDVI_diff')
        
        # Create vegetation mask from base year - include ALL vegetation
        vegetation_mask = base_year_composite.select('NDVI').gt(VEGETATION_THRESHOLD)
        
        # Identify vegetation loss
        vegetation_loss = ndvi_diff.lt(-NDVI_DECREASE_THRESHOLD).rename('vegetation_loss')
        
        # Apply vegetation mask to only show loss in areas that had vegetation
        masked_loss = vegetation_loss.updateMask(vegetation_mask)
        
        # Classify severity based on NDVI decrease magnitude
        severity = ee.Image(1)
        severity = severity.where(ndvi_diff.lt(-0.2), 2)
        severity = severity.where(ndvi_diff.lt(-0.3), 3) 
        severity = severity.where(ndvi_diff.lt(-0.4), 4)
        severity = severity.where(ndvi_diff.lt(-0.5), 5)
        severity = severity.updateMask(masked_loss)
        severity = severity.rename('severity')
        
        return severity, roi
    except Exception as e:
        logger.error(f"Error in vegetation loss map generation: {str(e)}")
        raise

@app.route('/getData', methods=['GET'])
def get_data():
    try:
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        distance = float(request.args.get('distance', 10))
        year = int(request.args.get('year', datetime.now().year - 1))  # Default to previous year
        
        # Input validation
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            return jsonify({'error': 'Invalid coordinates'}), 400
        if distance <= 0 or distance > 1000:
            return jsonify({'error': 'Invalid distance (0-1000 km)'}), 400
        current_year = datetime.now().year
        if year < 2015 or year > current_year:
            return jsonify({'error': f'Invalid year (2015-{current_year})'}), 400
        
        logger.info(f"Processing request: lat={latitude}, lon={longitude}, distance={distance}km, base_year={year}")
        
        # Generate map
        try:
            severity, roi = generate_vegetation_loss_map(latitude, longitude, distance, year)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        
        # Define visualization parameters for vegetation loss severity
        vis_params = {
            'min': 1, 
            'max': 5,
            'palette': ['yellow', 'orange', 'red', 'darkred', 'purple']
        }
        
        try:
            map_id_dict = severity.getMapId(vis_params)
            tile_url = map_id_dict['tile_fetcher'].url_format
        except Exception as e:
            logger.error(f"Error generating map tiles: {str(e)}")
            return jsonify({'error': 'Failed to generate map tiles. Please try again.'}), 500
        
        # Create Folium map
        m = folium.Map(location=[latitude, longitude], zoom_start=10, tiles='OpenStreetMap')
        
        # Add the vegetation loss layer
        folium.raster_layers.TileLayer(
            tiles=tile_url,
            attr='Google Earth Engine',
            name=f'Vegetation Loss since {year}',
            overlay=True,
            control=True,
            opacity=0.8,
        ).add_to(m)
        
        # Add the center marker
        folium.Marker(
            location=[latitude, longitude],
            popup=f"Center Point<br>Lat: {latitude}<br>Lon: {longitude}<br>Year: {year}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
        
        # Add a circle to show the study area
        folium.Circle(
            location=[latitude, longitude],
            radius=distance * 1000,  # Convert km to meters
            color='blue',
            fill=True,
            fill_opacity=0.1,
            popup=f"Study area: {distance} km radius"
        ).add_to(m)
        
        # Add map controls
        folium.LayerControl().add_to(m)
        plugins.MiniMap().add_to(m)
        plugins.Fullscreen().add_to(m)
        plugins.MousePosition().add_to(m)
        
        # Add a title
        title_html = '''
            <h3 align="center" style="font-size:16px"><b>Vegetation Loss Analysis</b><br>
            {0} to {1}</h3>
        '''.format(year, current_year)
        
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Create a legend
        legend_html = '''
        <div style="position: fixed; 
            bottom: 50px; right: 50px; width: 180px; height: 180px; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white;
            padding: 10px;
            border-radius: 6px;">
            <p style="margin-bottom: 5px;"><b>Vegetation Loss Severity</b></p>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: yellow; width: 20px; height: 20px; margin-right: 10px;"></div>
                <div>Very Low (0.1-0.2)</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: orange; width: 20px; height: 20px; margin-right: 10px;"></div>
                <div>Low (0.2-0.3)</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: red; width: 20px; height: 20px; margin-right: 10px;"></div>
                <div>Moderate (0.3-0.4)</div>
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: darkred; width: 20px; height: 20px; margin-right: 10px;"></div>
                <div>High (0.4-0.5)</div>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="background-color: purple; width: 20px; height: 20px; margin-right: 10px;"></div>
                <div>Severe (>0.5)</div>
            </div>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return render_template_string(m.get_root().render())
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
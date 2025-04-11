from flask import Flask,render_template,request,jsonify
from flask_cors import CORS
import time
import json
import os
import glob
import logging
import argparse
from house_gan.house_gan import generate_floorplan_files

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure required directories exist
def ensure_directories():
    dirs = ['static/imgs/generated', 'static/selected', 'temp']
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            logger.info(f"Created directory: {dir_path}")

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    logger.debug("Accessing index route")
    return render_template('index.html')

@app.route('/api/floorplans', methods=['DELETE'])
def resetSelectedFloorplan():
    logger.debug("Resetting selected floorplan")
    try:
        with open('static/selected/selected.json', 'w') as outfile:
            json.dump({}, outfile)
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Error resetting floorplan: {e}")
        return {"status": "ERROR", "message": str(e)}, 500

@app.route('/api/floorplans', methods=['POST'])
def getFloorplans():
    logger.debug("Generating floorplans")
    try:
        # Clean up existing files
        files = glob.glob('static/imgs/generated/*.png')
        logger.debug(f"Found existing files: {files}")
        for f in files:
            os.remove(f)

        request_data = request.get_json()
        if not request_data:
            raise ValueError("No JSON data received")
            
        logger.debug(f"Received request data: {request_data}")

        nodes = request_data.get('nodes')
        edges = request_data.get('edges')
        
        if not nodes or not edges:
            raise ValueError("Missing nodes or edges in request data")

        response = generate_floorplan_files(nodes, edges)
        logger.debug("Successfully generated floorplans")
        
        # write results to temp folder
        with open('temp/data.json', 'w') as outfile:
            json.dump(response, outfile)

        imgURLS = []
        t = int(round(time.time() * 1000))
        for i,d in enumerate(response):
            index = d['iteration']
            url = f'/static/imgs/generated/floorplan_{index}.png?t={t}'
            imgURLS.append(url)

        return {
            "status": "OK",
            "data": imgURLS
        }
    except Exception as e:
        logger.error(f"Error generating floorplans: {e}")
        return {"status": "ERROR", "message": str(e)}, 500

@app.route('/api/floorplans/select', methods=['POST'])
def getFloorplan():
    try:
        request_data = request.get_json()
        logger.debug(f"Selecting floorplan: {request_data}")

        if not request_data or 'iteration' not in request_data:
            raise ValueError("No iteration specified")

        iteration = request_data['iteration']

        with open('temp/data.json', 'r') as f:
            data = json.loads(f.read())

        for d in data:
            if d['iteration'] == iteration:
                logger.debug(f"Found selected floorplan: {d}")
                with open('static/selected/selected.json', 'w') as outfile:
                    json.dump(d, outfile)
                return {
                    "status": "OK",
                    "iteration": iteration
                }
        
        raise ValueError(f"No floorplan found with iteration {iteration}")
    except Exception as e:
        logger.error(f"Error selecting floorplan: {e}")
        return {"status": "ERROR", "message": str(e)}, 500

@app.route('/api/floorplans/selected', methods=['GET'])
def getSelectedFloorplan():
    try:
        logger.debug("Getting selected floorplan")
        with open('static/selected/selected.json', 'r') as f:
            data = json.loads(f.read())
        return {
            "status": "OK",
            "data": data
        }
    except Exception as e:
        logger.error(f"Error getting selected floorplan: {e}")
        return {"status": "ERROR", "message": str(e)}, 500

def main():
    parser = argparse.ArgumentParser(description='Run the Flask application for floor plan generation')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Ensure all required directories exist
    ensure_directories()
    
    logger.info(f"Starting Flask application on {args.host}:{args.port}")
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == '__main__':
    main()
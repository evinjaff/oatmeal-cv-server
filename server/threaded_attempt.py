from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64

app = Flask(__name__)

# Initialize a global variable for the image
global image
image = None

@app.route('/publish', methods=['POST'])
def publish():
    global image
    try:
        data = request.json
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode the base64 image
        img_data = base64.b64decode(data['image'])
        np_arr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        return jsonify({'status': 'Image received'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def display_image():
    global image
    while True:
        if image is not None:
            cv2.imshow('Image Window', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    import threading

    # Start the display_image function in a separate thread
    display_thread = threading.Thread(target=display_image)
    display_thread.daemon = True
    display_thread.start()

    # Run the Flask server
    app.run(debug=True, host='0.0.0.0', port=5000)

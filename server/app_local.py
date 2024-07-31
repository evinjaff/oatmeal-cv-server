from flask import Flask, render_template, request
from flask import g
import datetime
import cv2
import numpy as np
from ultralytics import YOLO
import time
import base64
from flask import send_file


app = Flask(__name__, static_folder='static') # you might change this

frame_hit_counter = 0

latest_oatmeal_image = {
    'image_name': "oatmeal.png",
    # 'base64': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9h",
    'base64': 'not an image',
    'base64_unprocessed': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9h",
    'date': "2018-01-01 00:00:00"
}


def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    # old (python 2 version):
    # nparr = np.fromstring(encoded_data.decode('base64'), np.uint8)

    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def process_image(image, type="base64"):
    global allRequiredItems_state
    global someDistractions_state
    # frame = cv2.imread("/Users/evinjaff/github/oatmeal-cv-server/server/add_005.jpg")
    # if image is base64, also wrap in a decode
    # frame = base64.b64decode(image)
    if type == "base64":
        frame = data_uri_to_cv2_img(image)
    elif type == "debug":
        cv2.imread("/Users/evinjaff/github/oatmeal-cv-server/server/add_005.jpg")

    w = int(frame.shape[1])
    h = int(frame.shape[0])

    model = YOLO("best.pt")

    finalImg = frame

    # get prediction
    predictionObject = model(frame)

    cv2.imwrite('image.png', finalImg)

    # return finalImg as base64
    with open("image.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    
    return 'data:image/png;base64,' + encoded_string.decode('utf-8')


@app.route("/publish", methods=['POST'])
def publish():
    global latest_oatmeal_image
    global frame_hit_counter
    
    # The request sends it in as a JSON object
    # so we have to parse it out, the base64 image is in the 'image' field
    # of the JSON object
    image = request.json['image']

    # print("Got image from client")
    # print(image)

    cv_img = process_image(image)

    # push the cv_img to the opencv window for preview
    cv2.imshow("preview", cv_img)

    # print("Processed image")
    # print(cv_img)

    frame_hit_counter += 1
    
    latest_oatmeal_image = {
        'image_name': "oatmeal.png",
        'base64': cv_img,
        'base64_unprocessed': image,
        'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return "success"

@app.route("/publish", methods=['GET'])
def bad_publish():
    # Return a bad method http code
    return "bad method - use POST"


# @app.route("/audio/allpresent.mp3")
# def audio(filename):
#   return send_file(filename, as_attachment=True)


    

if __name__ == '__main__':
    index_add_counter = 0
    app.app_context().push()
    g.site_counter = 0

    # open an opencv window
    cv2.namedWindow("preview")

    app.run(debug=True, port=8000, host='0.0.0.0')

from flask import Flask, render_template, request
from flask import g
import datetime
import cv2
import numpy as np
from ultralytics import YOLO
import time
import base64

app = Flask(__name__) # you might change this

site_counter = 0

latest_oatmeal_image = {
    'image_name': "oatmeal.png",
    'base64': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9h",
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

    for allPreds in predictionObject:
        for pred in allPreds:
            if np.array(pred.boxes.conf)[0] >= 0.5:
                

                # get label
                labelNum = np.array(pred.boxes.cls)[0]
                labelName = allPreds.names[labelNum]

                # Draw bounding box for object
                box = np.array(pred.boxes.xyxy).flatten().astype(int)
                # randomColor = tuple(np.random.random(size=3) * 256)
                randomColor = (0,255,0)
                cv2.rectangle(
                    finalImg,
                    (box[0], box[1]),
                    (box[2], box[3]),
                    randomColor,
                    4,
                )
                (label_width, label_height), baseline = cv2.getTextSize(
                    f"{labelName}: {round(float(np.array(pred.boxes.conf)[0]), 2)}",
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    2,
                )
                cv2.rectangle(
                    finalImg,
                    (box[0], box[1]),
                    (box[0] + label_width, box[1] - label_height),
                    randomColor,
                    -1,
                )
                cv2.putText(
                    finalImg,
                    f"{labelName}: {round(float(np.array(pred.boxes.conf)[0]), 2)}",
                    (box[0], box[1]),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 0),
                    2,
                    cv2.LINE_AA,
                )

    cv2.imwrite('image.png', finalImg)


    # return finalImg as base64
    with open("image.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    
    return 'data:image/png;base64,' + encoded_string.decode('utf-8')

@app.route("/status")
def hello():
    global site_counter
    site_counter += 1
    templateData = {
        'image_name': "oatmeal.png",
        'accuracy': 1.0,
        'site_counter': site_counter,
        'oatmeal_date': latest_oatmeal_image['date'],
        'oatmeal_image': latest_oatmeal_image['base64'],
        'oatmeal_image_unprocessed': latest_oatmeal_image['base64_unprocessed']

    } # to be changed
    return render_template('index.html', **templateData)

@app.route("/publish", methods=['POST'])
def publish():
    global latest_oatmeal_image
    
    # The request sends it in as a JSON object
    # so we have to parse it out, the base64 image is in the 'image' field
    # of the JSON object
    image = request.json['image']

    # print("Got image from client")
    # print(image)

    cv_img = process_image(image)

    # print("Processed image")
    # print(cv_img)
    
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
    

if __name__ == '__main__':
    index_add_counter = 0
    app.app_context().push()
    g.site_counter = 0
    app.run(debug=True, port=80, host='0.0.0.0')

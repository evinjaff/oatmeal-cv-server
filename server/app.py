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

######

allItems = {
    "salt": False,
    "timer": False,
    "hot_pad": False,
    "oatmeal": False,
    "big_spoon": False,
    "measuring_spoons": False,
    "measuring_cup_1/2": False,
    "measuring_cup_coffee": False,
    "measuring_cup_full": False,
    "measuring_cup_1/3": False,
    "measuring_cup_1/4": False,
    "tongs": False,
    "scissors": False,
    "spatula": False,
    "bowl": False,
    "pan": False,
    "pepper": False,
    "measuring_cup_glass": False,
    "small_spoon": False,
    "measuring_cup_group": False,
    "glass": False,
}

allRequired = {
    "salt": False,
    "timer": False,
    "hot_pad": False,
    "oatmeal": False,
    "big_spoon": False,
    "measuring_spoons": False,
    "measuring_cup_1/2": False,
    "bowl": False,
    "pan": False,
    "measuring_cup_glass": False,
    "small_spoon": False,
}

allRequiredColors = {
    "salt": tuple(np.random.random(size=3) * 256),
    "timer": tuple(np.random.random(size=3) * 256),
    "hot_pad": tuple(np.random.random(size=3) * 256),
    "oatmeal": tuple(np.random.random(size=3) * 256),
    "big_spoon": tuple(np.random.random(size=3) * 256),
    "measuring_spoons": tuple(np.random.random(size=3) * 256),
    "measuring_cup_1/2": tuple(np.random.random(size=3) * 256),
    "bowl": tuple(np.random.random(size=3) * 256),
    "pan": tuple(np.random.random(size=3) * 256),
    "measuring_cup_glass": tuple(np.random.random(size=3) * 256),
    "small_spoon": tuple(np.random.random(size=3) * 256),
}

allDistractors = {
    "measuring_cup_coffee": False,
    "measuring_cup_full": False,
    "measuring_cup_1/3": False,
    "measuring_cup_1/4": False,
    "tongs": False,
    "scissors": False,
    "spatula": False,
    "pepper": False,
    "measuring_cup_group": False,
    "glass": False,
}

allDistractorsColors = {
    "measuring_cup_coffee": tuple(np.random.random(size=3) * 256),
    "measuring_cup_full": tuple(np.random.random(size=3) * 256),
    "measuring_cup_1/3": tuple(np.random.random(size=3) * 256),
    "measuring_cup_1/4": tuple(np.random.random(size=3) * 256),
    "tongs": tuple(np.random.random(size=3) * 256),
    "scissors": tuple(np.random.random(size=3) * 256),
    "spatula": tuple(np.random.random(size=3) * 256),
    "pepper": tuple(np.random.random(size=3) * 256),
    "measuring_cup_group": tuple(np.random.random(size=3) * 256),
    "glass": tuple(np.random.random(size=3) * 256),
}

allRequiredItems_state = False
someDistractions_state = False

current_image_in_mem = ""

######



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

    for allPreds in predictionObject:
                for pred in allPreds:
                    # get label
                    labelNum = np.array(pred.boxes.cls)[0]
                    labelName = allPreds.names[labelNum]

                    # change item foundDictionaries to true
                    if labelName in allRequired.keys():
                        # reset timer if new item added
                        if allRequired[labelName] == False:
                            start_time = time.time()

                        allRequired[labelName] = True
                        randomColor = allRequiredColors[labelName]

                    if labelName in allDistractors.keys():
                        allDistractors[labelName] = True
                        randomColor = allDistractorsColors[labelName]

                    # Draw bounding box for object
                    box = np.array(pred.boxes.xyxy).flatten().astype(int)

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

                # ========= TEXT DISPLAY ========#
                # Required Items
                cv2.rectangle(finalImg, (0, 0), (540, h), (255, 255, 255), -1)
                cv2.putText(
                    finalImg,
                    "Required Items",
                    (0, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (255, 0, 0),
                    4,
                    cv2.LINE_AA,
                )

                iter = 0
                for k, v in allRequired.items():
                    cv2.putText(
                        finalImg,
                        f"{k}: ",
                        (0, 50 + 40 + (30 * iter)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )

                    (label_width, label_height), baseline = cv2.getTextSize(
                        f"{k}: ", cv2.FONT_HERSHEY_SIMPLEX, 1, 2
                    )

                    if v == True:
                        cv2.putText(
                            finalImg,
                            "PRESENT",
                            (0 + label_width, 50 + 40 + (30 * iter)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 180, 0),
                            2,
                            cv2.LINE_AA,
                        )
                    else:
                        cv2.putText(
                            finalImg,
                            "ABSENT",
                            (0 + label_width, 50 + 40 + (30 * iter)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            2,
                            cv2.LINE_AA,
                        )
                    iter += 1

                # Distractor Items
                cv2.putText(
                    finalImg,
                    "Distractor Items",
                    (0, h - h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (255, 0, 0),
                    4,
                    cv2.LINE_AA,
                )

                iter = 0
                for k, v in allDistractors.items():
                    cv2.putText(
                        finalImg,
                        f"{k}: ",
                        (0, h - h // 2 + 40 + (30 * iter)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )

                    (label_width, label_height), baseline = cv2.getTextSize(
                        f"{k}: ", cv2.FONT_HERSHEY_SIMPLEX, 1, 2
                    )

                    if v == True:
                        cv2.putText(
                            finalImg,
                            "PRESENT",
                            (0 + label_width, h - h // 2 + 40 + (30 * iter)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 180, 0),
                            2,
                            cv2.LINE_AA,
                        )
                    else:
                        cv2.putText(
                            finalImg,
                            "ABSENT",
                            (0 + label_width, h - h // 2 + 40 + (30 * iter)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            (0, 0, 255),
                            2,
                            cv2.LINE_AA,
                        )
                    iter += 1
                
                if(allRequiredItems_state and someDistractions_state):
                    cv2.putText(
                        finalImg,
                        "All items present. Some distractors remain.",
                        (0, h - h // 2 - 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (0, 255, 0),
                        4,
                        cv2.LINE_AA,
                    )
                elif (allRequiredItems_state and not someDistractions_state):
                    cv2.putText(
                        finalImg,
                        "All items present.",
                        (0, h - h // 2 - 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (255, 0, 0),
                        4,
                        cv2.LINE_AA,
                    )


    cv2.imwrite('image.png', finalImg)

    if all(allRequired.values()):
        allRequiredItems_state = True

    if any(allDistractors.values()):
        someDistractions_state = True

    # if no distractors flip state back to false
    if not any(allDistractors.values()):
        someDistractions_state = False


    # return finalImg as base64
    with open("image.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    
    return 'data:image/png;base64,' + encoded_string.decode('utf-8')

@app.route("/status")
def hello():
    global frame_hit_counter
    frame_hit_counter += 1
    templateData = {
        'image_name': "oatmeal.png",
        'accuracy': 1.0,
        'site_counter': frame_hit_counter,
        'oatmeal_date': latest_oatmeal_image['date'],
        'oatmeal_image': latest_oatmeal_image['base64'],
        'oatmeal_image_unprocessed': latest_oatmeal_image['base64_unprocessed']

    } # to be changed

    audio_files = ["allpresent.mp3", "allpresentsomedistractors.mp3"]

    return render_template('index.html', **templateData, audio_files=audio_files)

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

@app.route("/current_image", methods=['GET'])
def get_current_image():
    global latest_oatmeal_image
    return latest_oatmeal_image["base64"]

@app.route("/query-item-status", methods=['GET'])
def query_item_status():
    global allRequiredItems_state
    global someDistractions_state
    global frame_hit_counter

    return {
        "allRequiredItems_state": allRequiredItems_state,
        "someDistractions_state": someDistractions_state,
        "frame_hit_counter": frame_hit_counter
    }


# @app.route("/audio/allpresent.mp3")
# def audio(filename):
#   return send_file(filename, as_attachment=True)


    

if __name__ == '__main__':
    index_add_counter = 0
    app.app_context().push()
    g.site_counter = 0
    app.run(debug=True, port=80, host='0.0.0.0')

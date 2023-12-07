
import requests
import base64
import cv2
import time

# Capture frame from webcam
cap = cv2.VideoCapture(0)



# set resolution arbitrarily high to get max resoultion
HIGH_VALUE = 10000
WIDTH = HIGH_VALUE
HEIGHT = HIGH_VALUE

capture.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(width,height)

print("width {}, height {}".format(width, height))

cap.set(cv2.CAP_PROP_EXPOSURE, 240) # set exposure to 40

while True:
	# try it again so the exposure is better
	ret, frame = cap.read()

	# Encode frame as base64 string
	_, buffer = cv2.imencode('.jpg', frame)
	img_str = base64.b64encode(buffer).decode('utf-8')
	# also include the prefix so that the base64 string can be decoded in html
	img_str = "data:image/jpeg;base64," + img_str

	# Specify URL to send POST request to
	url = "https://brown-jeans-relax.loca.lt/publish"

	# Set headers and data for POST request
	headers = {'Content-Type': 'application/json'}
	data = {'image': img_str}

	# Send POST request
	response = requests.post(url, headers=headers, json=data)

	# Print response status code
	print(response.status_code)

	# time.sleep(1)

	print("eep done")

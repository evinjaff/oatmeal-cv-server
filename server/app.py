from flask import Flask, render_template, request
from flask import g
import datetime
app = Flask(__name__) # you might change this

site_counter = 0

latest_oatmeal_image = {
    'image_name': "oatmeal.png",
    'base64': "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9h",
    'date': "2018-01-01 00:00:00"
}

@app.route("/status")
def hello():
    global site_counter
    site_counter += 1
    templateData = {
        'image_name': "oatmeal.png",
        'accuracy': 1.0,
        'site_counter': site_counter,
        'oatmeal_date': latest_oatmeal_image['date'],
        'oatmeal_image': latest_oatmeal_image['base64']

    } # to be changed
    return render_template('index.html', **templateData)

@app.route("/publish", methods=['POST'])
def publish():
    global latest_oatmeal_image
    
    # The request sends it in as a JSON object
    # so we have to parse it out, the base64 image is in the 'image' field
    # of the JSON object
    image = request.json['image']

    print("Got image from client")
    print(image)
    
    latest_oatmeal_image = {
        'image_name': "oatmeal.png",
        'base64': image,
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

import numpy as np
from keras.models import model_from_json
import operator
import cv2
import sys, os
import time
from flask import Flask,render_template,Response

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Loading the model

json_file = open("model-bw.json", "r")
model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(model_json)
# load weights into new model
loaded_model.load_weights("model-bw.h5")
print("Loaded model from disk")

def gen():

    cap = cv2.VideoCapture(0)

# Category dictionary
#categories = {0: 'ZERO', 1: 'ONE', 2: 'TWO', 3: 'THREE', 4: 'FOUR', 5: 'FIVE', 'c': 'c', 'f': 'f', 'i': 'i', 'l': 'l', 'o': 'o', 'y': 'y'}

    while True:
        _, frame = cap.read()
        # Simulating mirror image
        frame = cv2.flip(frame, 1)
    
        # Got this from collect-data.py
        # Coordinates of the ROI
        x1 = int(0.5*frame.shape[1])
        y1 = 10
        x2 = frame.shape[1]-10
        y2 = int(0.5*frame.shape[1])
        # Drawing the ROI
        # The increment/decrement by 1 is to compensate for the bounding box
        cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255,0,0) ,1)
        # Extracting the ROI
        roi = frame[y1:y2, x1:x2]
    
        # Resizing the ROI so it can be fed to the model for prediction
        roi = cv2.resize(roi, (64, 64)) 
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, test_image = cv2.threshold(roi, 120, 255, cv2.THRESH_BINARY)
        cv2.imshow("test", test_image)
        # Batch of 1
        result = loaded_model.predict(test_image.reshape(1, 64, 64, 1))
        prediction = {'ZERO': result[0][0], 
                      'ONE': result[0][1], 
                      'TWO': result[0][2],
                      'THREE': result[0][3],
                      'FOUR': result[0][4],
                      'FIVE': result[0][5],
                      'c': result[0][6],
                      'dance': result[0][7],
                      'f': result[0][8],
                      'g': result[0][9],
                      'hello': result[0][10],
                      'i': result[0][11],
                      'i love you': result[0][12],
                      'l': result[0][13],
                      'o': result[0][14],
                      'please': result[0][15],
                      'q': result[0][16],
                      'thankyou': result[0][17],
                      'y': result[0][18]
                      }
        # Sorting based on top prediction
        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
    
        # Displaying the predictions
        cv2.putText(frame, prediction[0][0], (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)    
        #cv2.imshow("Frame", frame)
    
        #interrupt = cv2.waitKey(10)
        #if interrupt & 0xFF == 27: # esc key
            #break
        frame=cv2.imencode('.jpg',frame)[1].tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' +frame+b'\r\n')
 
    #cap.release()
    #cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()

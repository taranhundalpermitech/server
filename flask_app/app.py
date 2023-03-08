
from celery import Celery


from db_utils import *
from distutils.log import debug
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from celery_utils.flask_celery import make_celery

import eventlet
from flask_cors import CORS


eventlet.monkey_patch()


# the app is an instance of the Flask class
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'there is no secret'
app.config.update(
CELERY_BROKER_URL = 'amqp://admin:mypass@rabbit:5672',  
CELERY_RESULT_BACKEND='mongodb://mongodb_container:27017/mydb'
)
# app.config.update takes the following parameters:
# CELERY_BROKER_URL is the URL where the message broker (RabbitMQ) is running
# CELERY_RESULT_BACKEND is required to keep track of task and store the status


# integrates Flask-SocketIO with the Flask application
socketio = SocketIO(app,cors_allowed_origins="*",message_queue='amqp://admin:mypass@rabbit:5672')
# the app is passed to meke_celery function, this function sets up celery in order to integrate with the flask application
celery = make_celery(app)

# route() decorator is used to define the URL where index() function is registered for
@app.route('/')
def index():
	return render_template('index.html')

# event handler for connection where the client recieves a confirmation message upon the connection to the socket 
@socketio.on('connect')
def confirmation_message():
	print("dsds")
	socketio.emit("message","hello from python")
# event handler for name submission by the client 


@socketio.on('pong')
def handle_data(data):
    print('Received data from client: ' + data)



@app.route("/prediction",methods=['Post'])
def prediction():
    req = request.get_json()
    source_url = req["StreamUrl"]
    resp = create_stream(req)
    if(resp["status"]==False):
        return({"message":"Can not create stream, limit reached. Delete streams to create new one."})
    celery.send_task('tasks.predict', kwargs={'source':source_url,'source_id':resp["id"]})
    return({"Message":"Stream Started","SourceId":str(resp['id'])})

@app.route("/ppeResults",methods=['Post'])
def ppeResults():
    req = request.get_json()
    ppeDetections = req["Results"]
    socketio.emit("pong",ppeDetections)
    return({"message":"Stream Started"})

@app.route("/deleteStream",methods=['Post'])
def deleteStream():
    req = request.get_json()
    streamId = req["StreamId"]
    stream_delete(streamId)
    return({"message":"Stream Deleted"})

@app.route("/getStreams",methods=['Get'])
def getStreams():
    streams =  get_streams()
    return(streams)

@app.route("/getPPEDetections",methods=['Post'])
def getPPEDetections():
    req = request.get_json()
    result = get_PPE_detections(req["SourceId"],req["Start"],req["End"])
    return(result)
if __name__ == "__main__":
#    socketio.run(app,debug=True,port=5000)
    socketio.run(app, host="0.0.0.0", port="5000", ssl_context=('cert.pem', 'key.pem'))


# cd flask_app
#celery -A app.celery worker -P eventlet -c 1 --loglevel=info 

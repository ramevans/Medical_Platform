from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db =SQLAlchemy(app)

class DevicesModel(db.Model):
    device_name = db.Column(db.String(), primary_key=True, nullable=False)
    device_MAC = db.Column(db.String(),nullable=False, primary_key= True)
    user= db.Column(db.String(),nullable=False)
    Temperature = db.Column(db.Integer,primary_key= True, nullable=False)

    def __repr__(self):
        return f"Devices(Device Name={device_name}, Device MAC Address={device_MAC}, User={user}, Temperature= {Temperature})"

db.create_all()


device_put_args = reqparse.RequestParser()
device_put_args.add_argument("Device Name", type=str, help="Name of the Device", required =True)
device_put_args.add_argument("Device MAC Address", type=str, help="Device MAC Address", required =True)
device_put_args.add_argument("User", type=str, help="User", required =True)
device_put_args.add_argument("Temperature", type=int, help="Name of the Device", required =True) # find out how to make this take int and float 

therometer = {}

def abort_nonexist(device_info):
    if device_info not in therometer:
        abort(404, message= "No Device Infomation Provided")

def abort_exist(device_info):
    if device_info in therometer:
        abort(409, message= "Device Already Exist ")
class Devices(Resource):
    def get(self, device_info):
        abort(device_info)
        return therometer[device_info]

    def put(self, device_info):
        abort_exist(device_info)
        args = device_put_args.parse_args()
        therometer[device_info] = args
        return therometer[device_info], 201
    def delete(self, device_info):
        abort_nonexist(device_info)
        del therometer[device_info]
        return '', 204

api.add_resource(Devices, "/Devices/<string:device_info>")

if __name__ == '__main__':
    app.run(debug=True)


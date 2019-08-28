from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from json import dumps
import json
import os
import random
import string
import logging
from datetime import date

# Creates a new package and store it.
class Create(Resource):
    def post(self):
        args = parser.parse_args()

        if not self.validateInputsForCreate(args):
            logging.error('Invalid Input for Create API')
            return "Invalid inputs"

        progress={
           'Date': date.today().strftime("%B %d, %Y"),
           'Location': args['Source'],
        }

        id=self.generateId()
        package={
            'Id':id,
            'Progress': [ progress ],
            'Status': 'Received',
            'Source': args['Source'],
            'Destination': args['Destination'],
        }

        fileName=getFilePath(id)
        try:
            with open(fileName, 'w+') as outfile:
                json.dump(package, outfile, indent=4)
            return "New package created: "+id, 200
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            return "Create operation failed. please try after some time."


    # Validates input field for Create API call.
    def validateInputsForCreate(self, args):
        if args.get('Source')==None or args.get('Destination')==None:
            return False
        if len(args.get('Source'))==0 or len(args.get('Destination'))==0:
            return False
        return True

    # Generates an Id number for new package.
    def generateId(self):
        while True:
            id = ''.join([random.choice(string.ascii_letters
                + string.digits) for n in range(10)])
            if not isFileExists(str(random)):
                return id


# For given package id, checks what locations package has travelled.
class CheckProgress(Resource):
    def get(self):
        # append entry to progress field of package.
        args = parser.parse_args()
        fileName=getFilePath(args['Id'])
        try:
            with open(fileName,'r+') as json_file:
                data = json.load(json_file)
                return data['Progress']
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            return "No such Package exists"

# Updates a package and add new <location, date> entry.
class Update(Resource):
    def put(self):
        args = parser.parse_args()

        if not self.validateInputsForUpdate(args):
            logging.error('Invalid Input for Update API')
            return "Invalid input for update"

        # create new progress entry.
        progress={
           'Date': args['Date'],
           'Location': args['Location']
        }

        # append entry to progress field of package.
        fileName=getFilePath(args['Id'])
        try:
            with open(fileName,'r+') as json_file:
                data = json.load(json_file)
                data['Progress'].append(progress)
                json_file.seek(0)
                json.dump(data, json_file, indent=4)

            return "Package updated ", 200
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            return "No such Package exists"

    # validates if input are valid for update API call.
    def validateInputsForUpdate(self,args):
        if args.get('Date')==None or args.get('Location')==None:
            return False

        if len(args.get('Date'))==0 or len(args.get('Location'))==0:
            return False
        return True

# For given package id, marks it as delivered
class MarkDelivery(Resource):
    def put(self):
        args = parser.parse_args()
        fileName=getFilePath(args['Id'])
        try:
            with open(fileName,'r+') as json_file:
                data = json.load(json_file)
                data['Status']="Delivered"
                json_file.seek(0)
                json.dump(data, json_file, indent=4)

            return "package is marked as Delivered: ", 200
        except Exception as e:
            logging.error("Exception occurred", exc_info=True)
            return "No such Package exists"


# Returns if given file exists at given path or not.
def isFileExists(filename):
    global dir
    return os.path.exists(dir+filename+".txt")

def getFilePath(name):
    global dir
    return dir+name+".txt"

def setupBasicConfigs():
    if not os.path.exists('adsstorage'):
        os.makedirs('adsstorage')

    if not os.path.exists(logDir):
        os.makedirs(logDir)
    with open(logPath, "a+"):pass

    #Create and configure logger
    logging.basicConfig(filename=logPath,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filemode='w')
def addResources(api):
    api.add_resource(Create, '/create')
    api.add_resource(CheckProgress, '/check_progress')
    api.add_resource(Update, '/update')
    api.add_resource(MarkDelivery, '/mark_delivery')

def setupParser():
    global parser
    parser = reqparse.RequestParser()
    parser.add_argument('Id')
    parser.add_argument('Location')
    parser.add_argument('Date')
    parser.add_argument('Status')
    parser.add_argument('Source')
    parser.add_argument('Destination')

dir="./adsstorage/"

#logFilePath="ads-logs/logs.txt"
logDir="ads-logs"
logFile="logs.txt"
logPath=logDir+"/"+logFile

if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)
    setupParser()
    addResources(api)

    # set-up directories and log files
    setupBasicConfigs()

    app.run(port='8081', debug=True)

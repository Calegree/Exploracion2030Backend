from flask import Flask
from flask_restful import Api
from resources.prediction import Prediction

app = Flask(__name__)
api = Api(app)

# Ruta /predict gestionada por clase Prediction
api.add_resource(Prediction, '/predict')

if __name__ == '__main__':
    app.run(debug=True)

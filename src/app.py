from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from resources.prediction import Prediction
from resources.download_fungis import DownloadImages

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)  # 👈 Activa Swagger

# Endpoints en Flask las rutas se llaman resources (Routes)
api.add_resource(Prediction, '/predict')
api.add_resource(DownloadImages, '/download')

if __name__ == '__main__':
    app.run(debug=True)

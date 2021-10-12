from flask import Flask

def create_app():
    app = Flask(__name__)

    from seoul_landprice_model.routes import main
    from seoul_landprice_model.routes import result
    app.register_blueprint(main.bp)
    app.register_blueprint(result.bp)

    return app

if __name__ ==  '__main__':
    app = create_app()
    app.run(debug=True)

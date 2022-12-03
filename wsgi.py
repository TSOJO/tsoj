from website import init_app
import logging

app = init_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run()

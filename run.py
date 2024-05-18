from config import app_config, app_active
from app import create_app

config = app_config[app_active]

if __name__ == '__main__':
    app = create_app(config)
    app.run(host=config.IP_HOST, port=config.PORT_HOST)

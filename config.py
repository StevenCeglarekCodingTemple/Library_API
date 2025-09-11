class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True
    PORT = 5001
    

class TestingConfig:
    pass


class ProductionConfig:
    pass
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('mysql+pymysql://doadmin:EatCxJLa62yQV5wh@db-mysql-fra1-44732-do-user-9796066-0.b.db.ondigitalocean.com:25060/defaultdb', connect_args={'ssl': {'ssl-mode': 'required'}}, pool_recycle=3600)
#engine = create_engine('sqlite:///database.db', convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)

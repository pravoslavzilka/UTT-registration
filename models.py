from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Time, LargeBinary
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from database import Base


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(128))
    rank = Column(Integer)

    def __init__(self, name=None, email=None, rank=None):
        self.name = name
        self.email = email
        self.rank = rank

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150), unique=True)
    password = Column(String(128))
    code = Column(Integer, unique=True)
    confirm = Column(Boolean)
    qr_code = Column(LargeBinary)

    tickets = relationship("Ticket", back_populates="user", foreign_keys="[Ticket.user_id]")

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return self.confirm

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.name


class Ticket(Base):
    __tablename__ = "ticket"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    ticket_type_id = Column(Integer, ForeignKey('ticket_type.id'))

    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    ticket_type = relationship("TicketType", back_populates="tickets", foreign_keys=[ticket_type_id])

    def __init__(self, ticket_type=None, user=None):
        self.ticket_type = ticket_type
        self.user = user


class TicketType(Base):
    __tablename__ = "ticket_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    speaker = Column(String(50))
    tickets = relationship("Ticket", back_populates="ticket_type")
    start = Column(Time)
    end = Column(Time)
    max_cap = Column(Integer)
    ticket_type_type_id = Column(Integer, ForeignKey('ticket_type_type.id'))

    ticket_type_type = relationship("TicketTypeType", back_populates="ticket_types", foreign_keys=[ticket_type_type_id])

    def __init__(self, name=None, speaker=None, max_cap=None):
        self.name = name
        self.speaker = speaker
        self.max_cap = max_cap


class TicketTypeType(Base):
    __tablename__ = "ticket_type_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(300))

    ticket_types = relationship("TicketType", back_populates="ticket_type_type")
from models import *
from database import db_session, init_db

init_db()

admin = Admin("Admin", "admin@localhost", 1)
admin.set_password("sigur")

user = User("Jožo Ráž", "jozo@raz")
user.set_password("sichuan")

ttt = TicketTypeType()
ttt.name = "workshop"

tt = TicketType("Workshop 1", "Vlado Kunis",40)
tt.ticket_type_type = ttt

t = Ticket(tt, user)

db_session.add(admin)
db_session.add(user)
db_session.add(ttt)
db_session.add(tt)
db_session.add(t)

db_session.commit()
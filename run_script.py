from models import *
from database import db_session, init_db
import uuid

init_db()

admin = Admin("Admin", "admin@localhost", 1)
admin.set_password("sigur")

user = User("Jožo Ráž", "dub@localhost")
user.set_password("shibajedoge")
user.code = uuid.uuid4().hex

ttt = TicketTypeType()
ttt.name = "Workshop I. BLOK"

ttt2 = TicketTypeType()
ttt2.name = "Workshop II. BLOK"

ttt3 = TicketTypeType()
ttt3.name = "Workshop III. BLOK"

ttt4 = TicketTypeType()
ttt4.name = "Ďaľší Program"

tt = TicketType("Workshop 1", "Vlado Kunis", 40, ttt)
tt.users.append(user)

t = Ticket(tt, user)

db_session.add(admin)
db_session.add(user)
db_session.add(ttt)
db_session.add(ttt2)
db_session.add(ttt3)
db_session.add(ttt4)
db_session.add(tt)
db_session.add(t)

db_session.commit()
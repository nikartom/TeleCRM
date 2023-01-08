import sqlite3 as sq
from plugins import id_generate

async def db_start():
    global db, cur

    db = sq.connect('base.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS profile(user_id INTEGER PRIMARY KEY, name TEXT, surname TEXT, nick TEXT)")
    cur.execute('''CREATE TABLE IF NOT EXISTS project
    (ID INTEGER PRIMARY KEY,
    User_id INTEGER,
    Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Street TEXT,
    Numb TEXT,
    Desc TEXT,
    File TEXT,
    FOREIGN KEY (User_id) REFERENCES profile (user_id))''')
    db.commit()

async def create_profile(user_id, nick):
    user = cur.execute("SELECT 1 FROM profile WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    if not user:
        cur.execute('INSERT INTO profile VALUES(?, ?, ?, ?)', (user_id, '', '', nick))
        db.commit()
    
async def update_profile(state, user_id):
    async with state.proxy() as data:
        cur.execute("UPDATE profile SET name = '{}', surname = '{}' WHERE user_id == '{}'".format(
            data['name'],
            data['surname'],
            user_id))
        db.commit()

async def create_project(state, user_id):
    async with state.proxy() as data:
        street = data['street']
        numb = data['numb']
        desc = data['desc']
        url = data['url']
        cur.execute(f"INSERT INTO project(User_id, Street, Numb, Desc, File) VALUES({user_id},'{street}','{numb}','{desc}','{url}')")
        db.commit()

# async def update_project(state, user_id):
#     async with state.proxy() as data:
#         cur.execute('''UPDATE project SET 
#         Street = '{}', 
#         Numb = '{}', 
#         Desc = '{}', 
#         File = '{}' 
#         WHERE user_id == '{}' '''.format(
#             data['Street'],
#             data['Numb'],
#             data['Desc'],
#             data['File'],
#             user_id))
#         db.commit()
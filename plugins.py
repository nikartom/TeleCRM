from datetime import datetime
import requests
import pytz
import json
import os

from config import TOKEN

URL = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}
public_key = 'ex+ssVuZSzO6zOyBCS9vQTNVihI7J135zErVA/5SdwjqG1iyBe8mCnHxL+ku7npaq/J6bpmRyOJonT3VoXnDag=='

def datetime_now():
    kras = pytz.timezone("Asia/Krasnoyarsk")
    time = datetime.now(kras)
    now = time.strftime("%H:%M")
    return now

def id_generate():
    time = datetime.now()
    id = time.strftime("%M%Y%H%M%S")
    return int(id)

def list_dir(path):
    r = requests.get(f'{URL}?path={path}', headers=headers)
    inf = json.loads(r.text)
    emb = inf['_embedded']['items']
    dirs = []
    for i in emb:
        dirs.append(i['name'])
    return dirs

def list_files(path):
    r = requests.get(f'{URL}?path={path}', headers=headers)
    inf = json.loads(r.text)
    emb = inf['_embedded']['items']
    dirs = []
    for i in emb:
        dirs.append(i['name'])
    return dirs
    # print(inf)

list_files("Объекты/")

def create_folder(path):
    requests.put(f'{URL}?path={path}', headers=headers)

def upload_file(loadfile, savefile, replace=False):
    """
    savefile: Путь к файлу на Диске
    loadfile: Путь к загружаемому файлу
    replace: true or false Замена файла на Диске
    upload_file(r'C:\myFiles\images.rar', 'hello world/images.rar')
    """
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file':f})
        except KeyError:
            print(res)
    os.remove(loadfile)
    



import os
import json
import requests

base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__))

def get_album_image(data):
    image_file = f"{base_path}/cover/{data['id']}.{data['name'].replace('|', '')}.png"
    if not os.path.exists(image_file):
        print(f"{data['name']}, save image: {image_file}")
        r = requests.get(data['cover'])
        with open(image_file, 'wb') as f:
            f.write(r.content)

if __name__ == "__main__":
    json_name = f'{base_path}/data/books.json'
    with open(json_name, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    for data in json_data['data']['resourceList']:
        get_album_image(data)
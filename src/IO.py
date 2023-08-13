import urllib, json
import os
from dotenv import load_dotenv

def load_data():
    load_dotenv()
    GMAPS_API_KEY=os.environ['GMAPS_API_KEY']
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())
    return data
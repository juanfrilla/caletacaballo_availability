from bs4 import BeautifulSoup
from scrapers.airbnb import (
    tokens_request,
    parse_tokens_json,
    check_availability,
)
from utils import save_json

response = tokens_request()
soup = BeautifulSoup(response.text, "html.parser")
tokens_json = parse_tokens_json(soup)
rjson = check_availability(tokens_json)
save_json("data/airbnb.json", rjson)

from bs4 import BeautifulSoup
from scrapers.booking import (
    tokens_request,
    parse_tokens_json,
    check_availability_booking,
)
from utils import save_json

response = tokens_request()
soup = BeautifulSoup(response.text, "html.parser")
tokens_json = parse_tokens_json(soup)
rjson = check_availability_booking(tokens_json)
save_json("data/booking.json", rjson)

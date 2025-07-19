import os
import json
import time
import datetime
import streamlit as st
from streamlit_calendar import calendar
from scrapers.airbnb import scrape as scrape_airbnb
from scrapers.booking import scrape as scrape_booking


CACHE_TTL_SECONDS = 3600
BOOKING_CACHE_PATH = "data/airbnb.json"
AIRBNB_CACHE_PATH = "data/booking.json"


calendar_options = {
    "initialView": "dayGridMonth",
    "firstDay": 1,
    "editable": True,
    "selectable": True,
    "dayMaxEvents": False,  # allow full event stack display
    "eventDisplay": "block",  # <--- FORCE events to show as blocks with text
    "locale": "es",
    "height": "auto",
    "contentHeight": "auto",
    "aspectRatio": 0.75,  # makes it taller on narrow screens
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek",
    },
    "buttonText": {
        "today": "Hoy",
        "month": "Mes",
        "week": "Semana",
        "day": "Día",
        "prev": "←",
        "next": "→",
    },
}


def create_calendar_event(date_str: str, is_available: bool):
    return {
        "title": "Libre" if is_available else "Ocupado",
        "start": date_str,
        "end": date_str,
        "backgroundColor": "#2ecc71" if is_available else "#e74c3c",
        "borderColor": "#2ecc71" if is_available else "#e74c3c",
        "textColor": "#ffffff",
    }


def load_cache(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        data = json.load(f)
    if time.time() - data["timestamp"] > CACHE_TTL_SECONDS:
        return None
    return data["payload"]


def save_cache(filepath, payload):
    with open(filepath, "w") as f:
        json.dump({"timestamp": time.time(), "payload": payload}, f)


def scrape_booking_cached():
    cached = load_cache(BOOKING_CACHE_PATH)
    if cached is not None:
        return cached
    scraped = scrape_booking()
    save_cache(BOOKING_CACHE_PATH, scraped)
    return scraped


def scrape_airbnb_cached():
    cached = load_cache(AIRBNB_CACHE_PATH)
    if cached is not None:
        return cached
    scraped = scrape_airbnb()
    save_cache(AIRBNB_CACHE_PATH, scraped)
    return scraped


def generate_calendar_events():
    booking_dict = scrape_booking_cached()
    airbnb_dict = scrape_airbnb_cached()
    calendar_events = []
    all_dates = set(booking_dict.keys()) | set(airbnb_dict.keys())

    for date_str in all_dates:
        booking_known = date_str in booking_dict
        airbnb_known = date_str in airbnb_dict

        if booking_known and airbnb_known:
            is_available = booking_dict[date_str] and airbnb_dict[date_str]
            calendar_events.append(create_calendar_event(date_str, is_available))
        else:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj >= datetime.date.today():
                calendar_events.append(
                    {
                        "title": "Desconocido",
                        "start": date_str,
                        "end": date_str,
                        "backgroundColor": "#808080",
                        "borderColor": "#808080",
                        "textColor": "#ffffff",
                    }
                )

    return calendar_events


calendar_data = calendar(
    events=generate_calendar_events(),
    options=calendar_options,
    key="calendar-ocupado-libre",
)

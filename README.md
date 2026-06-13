 ## 🏡 Airbnb & Booking Availability Scraper (No Browser Needed)
- Lightweight and fast scraper to check the availability of an apartment on Airbnb and Booking.com using pure HTTP requests — no browser, no Playwright, no Selenium.

- This project includes a custom AWS WAF challenge solver that generates the required validation cookie to bypass Booking’s bot protection.

## 🧠 AWS WAF Solver (Technical Overview)
- Booking.com uses AWS WAF to ensure you use browser.
- This project includes a hand‑crafted solver that:
  - Reproduces the computation required by AWS WAF
  - Generates the aws-waf-token validation cookie
  - Injects it into subsequent HTTP requests
- This allows the scraper to behave like a real browser without actually running one.


## 📦 Installation
- Clone the repository:

```bash
git clone https://github.com/juanfrilla/caletacaballo_availability
cd caletacaballo_availability
```
- Install dependencies:

```bash
uv venv .venv
uv pip install -r requirements.txt
streamlit run main.py
```

## 🌐 Live Demo
- See the project running here:

👉 https://caletacaballo.streamlit.app/

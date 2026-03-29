# Easter Food Order

A simple local-network web app for collecting Easter team building food orders and aggregating them for the buyer.

## How it works

1. Run the app on one machine connected to your office/home WiFi
2. Share the URL (`http://<your-ip>:5000`) with your team (up to ~10 people)
3. Everyone opens the link in their browser and submits what they want
4. The buyer opens `/orders` to see the full aggregated shopping list

## Setup

```bash
pip install flask
python app.py
```

The server starts on port 5000 and is accessible from any device on the same network.

## Pages

| URL | Purpose |
|-----|---------|
| `/` | Order form — each person fills this in |
| `/orders` | Aggregated shopping list for the buyer |

## Finding your IP address

- **Windows:** `ipconfig` in Command Prompt → look for IPv4 Address
- **Mac/Linux:** `ifconfig` or `ip addr` → look for `192.168.x.x`

Then share: `http://192.168.x.x:5000`

## Notes

- Orders are stored in `orders.db` (SQLite, created automatically)
- The `/orders` page has a "Clear all orders" button to reset between rounds
- No internet connection needed — fully local

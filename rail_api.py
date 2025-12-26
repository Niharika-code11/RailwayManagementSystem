import csv
from datetime import datetime

CSV_FILE = "regional_train_data.csv"

def get_trains(src, dest, date):
    trains = []
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['src_code'].lower() == src.lower() and row['dest_code'].lower() == dest.lower():
                trains.append({
                    "train_name": row["train_name"],
                    "train_number": row["train_number"],
                    "src_code": row["src_code"],
                    "dest_code": row["dest_code"]
                })
    return trains

# Dummy seat and fare info
def get_seat_availability(train_number, date, cls):
    return {
        "status": "AVAILABLE 20",
        "fare": 150 if cls == "SL" else 350 if cls == "3A" else 550
    }

def get_live_status(train_number):
    return "Running On Time"

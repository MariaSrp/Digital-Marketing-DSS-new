import time
import pandas as pd

SOURCE_FILE = "source_data.csv"
LIVE_FILE = "live_marketing_data.csv"
INTERVAL_SECONDS = 15  # seconds between new rows

def main():
    # Read full source data
    source = pd.read_csv(SOURCE_FILE)

    # If live file does not exist or is empty, create it with only header
    try:
        live = pd.read_csv(LIVE_FILE)
    except FileNotFoundError:
        source.head(0).to_csv(LIVE_FILE, index=False)
        live = pd.read_csv(LIVE_FILE)

    start_idx = len(live)  # how many rows are already in live file

    while start_idx < len(source):
        next_row = source.iloc[start_idx:start_idx + 1]
        next_row.to_csv(LIVE_FILE, mode="a", header=False, index=False)
        print(f"Appended row {start_idx}")
        start_idx += 1
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()

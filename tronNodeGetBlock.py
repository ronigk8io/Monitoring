import sys
import requests

def get_current_tron_block():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://api.trongrid.io"
    endpoint = "/wallet/getnowblock"
    url = base_url + endpoint

    try:
        response = requests.post(url, json={}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            current_block_number = data['block_header']['raw_data']['number']
            # Example output format: "TRON|current_block_number|Some additional info if needed"
            print(f"{current_block_number}")
        else:
            # If response is unsuccessful, output a formatted error message
            print(f"TRON|ERROR|Failed to fetch block. Status code: {response.status_code}")
    except Exception as e:
        # Output for unexpected errors
        print(f"TRON|EXCEPTION|{str(e)}")

if __name__ == '__main__':
    get_current_tron_block()

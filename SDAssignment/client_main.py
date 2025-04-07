# client_main.py
import requests

def search_from_master(query):
    url = "http://localhost:3000/api/search"
    try:
        response = requests.get(url, params={'q': query})
        if response.status_code == 200:
            results = response.json()
            if results:
                print(f"Found {len(results)} results:")
                for r in results:
                    print(f" - {r}")
            else:
                print("No results found.")
        else:
            print("Error:", response.status_code, response.text)
    except Exception as e:
        print("Could not connect to master node:", e)

if __name__ == "__main__":
    query = input("Enter search query: ")
    search_from_master(query)

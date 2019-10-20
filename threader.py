from concurrent.futures import ThreadPoolExecutor
from src.Client import BoxClient




if __name__ == "__main__":
    app_client = BoxClient()
    payload = app_client.generate_payload('excel', 'static/students_100.xlsx', 'students', None)

    def threader(function, payload):
        with ThreadPoolExecutor(max_workers=15) as executors:
            for _ in executors.map(function, payload):
                print("DONE")

    threader(app_client.create_user, payload)
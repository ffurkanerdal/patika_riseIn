from dotenv import load_dotenv, find_dotenv
import requests
import os
import uuid

load_dotenv(find_dotenv())

class Main:
    def __init__(self) -> None:
        self.base_url = "https://api.circle.com/v1/w3s/"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('API_KEY')}"
        }

    def get_app_id(self):
        try:
            url = f"{self.base_url}config/entity"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            return {"app_id": data["data"]["appId"]}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"msg": f"Error: {e}"}

    def create_new_user(self):
        url = f"{self.base_url}users"
        user_id = str(uuid.uuid4())
        data = {"userId": user_id}

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return {"code": response.status_code, "userId": user_id}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"msg": f"Error: {e}"}

    def acquire_session_token(self):
        url = f"{self.base_url}users/token"
        user_id = self.create_new_user().get("userId")

        data = {"userId": user_id}

        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            response_data = response.json()["data"]
            return {
                "userToken": response_data["userToken"],
                "encryptionKey": response_data["encryptionKey"]
            }
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"msg": f"Error: {e}"}

    def get_challenge_id(self):
        token = self.acquire_session_token().get("userToken")
        idempotency_key = str(uuid.uuid4())
        url = f"{self.base_url}user/initialize"
        headers = self.headers.copy()
        headers.update({"X-User-Token": token})

        data = {
            "idempotencyKey": idempotency_key,
            "blockchains": ["MATIC-AMOY"]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_data = response.json()
            return {"challenge_id": response_data["data"]["challengeId"]}
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            return {"msg": f"Error: {e}"}

# Örnek kullanım:
if __name__ == "__main__":
    main = Main()

    app_id = main.get_app_id()
    print("App ID:", app_id)

    challenge_id = main.get_challenge_id()
    print("Challenge ID:", challenge_id)

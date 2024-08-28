import requests
import json


class AlfieAssistant:
    def __init__(self):
        self.history = []
        self.current_conversation = []

    def _localAG_send_request(self, message):
        url = "http://localhost:2025/v1/chat/completions"

        # Your request payload
        payload = {
            "messages": [
                { "role": "user", "content": message }
            ],
            "temperature": 0.7,
            "max_tokens": -1,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        # Send POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Check for successful response
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Request failed with status code " + str(response.status_code)}

    def _localAG_process_response(self, response):
        try:
            choices = response.get("choices")
            if choices:
                message = choices[0].get("message").get("content")
                # Parse the response JSON
                parsed_response = json.loads(message)
                return parsed_response
            else:
                return {"error": "No response found in the API response"}

        except Exception as e:
            return {"error": str(e)}

    def _localAG_get_response(self, message):
        # Send the request to the API
        response = self._localAG_send_request(message)

        # Process the API response
        parsed_response = self._localAG_process_response(response)

        if "error" in parsed_response:
            print(f"Error: {parsed_response['error']}")
            return None

        return parsed_response


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        alfie = AlfieAssistant()
        response = alfie._localAG_get_response(user_input)
        if response:
            print("Bot:", json.dumps(response))
        else:
            print("Bot:", "Sorry, I couldn't get a response.")
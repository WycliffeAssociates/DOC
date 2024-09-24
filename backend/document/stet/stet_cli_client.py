import os
import requests
import time

base_url = os.getenv("BASE_URL", "http://localhost:5005")  # URL of the backend app
fileserver_url = os.getenv("FILESERVER_URL", "http://localhost:8089")

# Endpoint paths
document_request_endpoint = "/stet/documents_stet_docx"
task_status_endpoint = "/task_status/"

# Document request data
document_request_data = {
    "lang0_code": os.getenv("SOURCE_LANGUAGE", "en"),
    "lang1_code": os.getenv("TARGET_LANGUAGE", "abu"),
    "email_address": os.getenv("EMAIL_ADDRESS", "fake@example.com"),
}

# Submit document request
response = requests.post(
    f"{base_url}{document_request_endpoint}", json=document_request_data
)

if response.status_code == 200:
    task_id = response.json().get("task_id")
    print(f"Document request submitted successfully. Task ID: {task_id}")

    # Long polling for task completion
    while True:
        status_response = requests.get(f"{base_url}{task_status_endpoint}{task_id}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            state = status_data.get("state")
            print(f"Task Status: {state}")

            if state == "SUCCESS":
                result = status_data.get("result")
                print(
                    f"Task completed successfully. Result: {fileserver_url}/{result}.docx"
                )
                break
            elif state in ["FAILURE", "REVOKED"]:
                print(f"Task failed or was revoked. State: {state}")
                break
        else:
            print("Error fetching task status.")

        # Wait before polling again
        time.sleep(5)

else:
    print(f"Failed to submit document request. Status code: {response.status_code}")

import requests
import json
import time

def test_rag():
    url = "http://localhost:5000/chat"
    # Query about specific info in correctly added FAQ section
    query = "Is there power backup?"
    
    print(f"Sending query: {query}")
    try:
        response = requests.post(url, json={"message": query}, stream=True)
        
        full_response = ""
        print("Response stream:")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                try:
                    data = json.loads(decoded_line)
                    if "chunk" in data:
                        print(data["chunk"], end="", flush=True)
                        full_response += data["chunk"]
                    if "error" in data:
                        print(f"\nError: {data['error']}")
                except:
                    pass
        
        print("\n\n--- Verification ---")
        if "Yes" in full_response or "backup" in full_response or "elevators" in full_response:
            print("SUCCESS: Retrieved Power Backup info from FAQs.")
        else:
            print("WARNING: Did not find expected FAQ details in response.")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    # Wait a bit for server to be ready if run immediately after start
    time.sleep(5) 
    test_rag()

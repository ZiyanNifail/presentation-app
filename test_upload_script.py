import requests

# URL of your API
url = 'http://127.0.0.1:5000/api/upload'

# Data to send (Form fields)
data = {
    'userID': '1'
}

video_path = r"C:\Users\USER\Videos\test.mp4" 

try:
    # Open the file in binary mode
    with open(video_path, 'rb') as f:
        files = {'video': f}
        
        # Send the POST request
        print(f"Sending {video_path} to server...")
        response = requests.post(url, data=data, files=files)
        
        # Print the result
        print("Status Code:", response.status_code)
        print("Response:", response.text)

except FileNotFoundError:
    print("Error: Could not find the video file! Check the path.")
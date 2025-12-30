import requests
import json # To parse the JSON response
import smtplib
from email.message import EmailMessage

def send_email():
    msg = EmailMessage()
    msg["Subject"] = "Vacancy found"
    body = "Hi! This email is to inform vacancy has reported by kpsc."
    msg["From"] = "info@email.in"  # Your Namecheap email
    msg["To"] = "youremail@gmail.com"
    msg.set_content(body)

    # Use Namecheap SMTP
    with smtplib.SMTP_SSL("evzoneindia.in", 465) as server:
        server.login("info@domain.in", "password")
        server.send_message(msg)
    print("Email sent successfully!")



url = 'https://psc.kerala.gov.in/status/php/loadVacancy.php'

# The payload (body) for the POST request.
# The 'requests' library will automatically URL-encode this dictionary
# and set the 'Content-Type' header to 'application/x-www-form-urlencoded'
# if the 'data' parameter is used.
# The JavaScript body 'k=690%2F2022&dist=00' translates to the following dictionary:
payload = {
    'k': '690/2022',
    'dist': '00'
}

# Define the headers. Note that 'Content-Type' will be automatically set
# by requests when using the 'data' parameter for form-urlencoded data,
# but it's good practice to define other relevant headers.
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,ml;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'DNT': '1', # Do Not Track header
    'Host': 'psc.kerala.gov.in',
    'Origin': 'https://psc.kerala.gov.in',
    'Pragma': 'no-cache',
    'Referer': 'https://psc.kerala.gov.in/status/',
    'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1'
    # Sensitive 'Cookie' header should be added here if necessary for authentication
    # 'Cookie': '<your_cookie_value>'
}

try:
    # Send the POST request
    response = requests.post(url, headers=headers, data=payload) # 'data' parameter for form-urlencoded
    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

    # Check if the response content type is JSON, despite the header stating text/html
    # The original request's response body was JSON, so we attempt to parse it as such.
    try:
        data = response.json()
        print("Response JSON data:")
        #print(json.dumps(data, indent=2))
        print("{:<20} {}".format("FIELD", "VALUE"))
        print("-" * 35)

        for  value in data:
            #if not key.isdigit():   # skip numeric keys
                print(value["sl_no"],value["vcy_type"],value["vcy_dt"])
                if int(value["sl_no"]) > 4:
                    print("New Found")
                    send_email()
                    with open("report.txt", "w") as file:
                        file.write("{} {} {}\n".format(value["sl_no"], value["vcy_type"], value["vcy_dt"]))
                        
                    
                        
        
    except json.JSONDecodeError:
        print("Response is not valid JSON, printing raw text:")
        print(response.text)

except requests.exceptions.HTTPError as errh:
    print(f"Http Error: {errh}")
except requests.exceptions.ConnectionError as errc:
    print(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    print(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    print(f"Something went wrong: {err}")


from twilio.rest import Client

account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"

client = Client(account_sid, auth_token)

def send_sms(phone, message):
    client.messages.create(
        body=message,
        from_="+17126428590",  # your Twilio number
        to=phone
    )
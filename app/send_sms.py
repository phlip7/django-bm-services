import os
from twilio.rest import Client


def send_sms(msg, target_number):
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        server_number = os.environ['TWILIO_NUMBER']
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=msg,
            from_=server_number,
            to=target_number
        )
        print(message.sid)
        return True
    except Exception as e:
        print("==Sending Error==", e)
        return False

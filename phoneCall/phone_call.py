from twilio.rest import Client

# Twilio account credentials
TWILIO_ACCOUNT_SID = 'AC7.............................'
TWILIO_AUTH_TOKEN = '956.............................'
#TWILIO_PHONE_NUMBER = '+168....3371'
TWILIO_PHONE_NUMBER = '+160....5115'

# List of phone numbers to call
PHONE_NUMBERS = ['+97254....435']
#PHONE_NUMBERS = ['+9725........5', '+972xxxxxxxxx']

def make_phone_call(to_number):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=to_number,
        from_=TWILIO_PHONE_NUMBER,
        url='http://demo.twilio.com/docs/voice.xml'  # Default Twilio demo message
    )
    print('Call made to {}: {}'.format(to_number, call.sid))

def make_calls_to_all_numbers():
    for number in PHONE_NUMBERS:
        make_phone_call(number)


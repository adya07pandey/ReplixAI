import base64

def get_new_messages(service, history_id):
    response = service.users().history().list(
        userId='me',
        startHistoryId=history_id,
        historyTypes=['messageAdded']
    ).execute()

    messages = []

    for record in response.get('history', []):
        for msg in record.get('messagesAdded', []):
            messages.append(msg['message']['id'])

    return messages


def extract_email(service, msg_id):
    msg = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    headers = msg['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "")
    sender = next((h['value'] for h in headers if h['name'] == 'From'), "")

    body = ""

    payload = msg['payload']

    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] in ['text/plain', 'text/html']:
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode()
                    break
    else:
        data = payload['body'].get('data')
        if data:
            body = base64.urlsafe_b64decode(data).decode()

    return {
        "sender": sender,
        "subject": subject,
        "body": body,
        "gmail_message_id": msg['id'],
        "gmail_thread_id": msg['threadId']
    }
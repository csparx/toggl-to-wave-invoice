import requests

WAVE_API_TOKEN = 'your_wave_api_token' #your_wave_api_token
TOGGL_API_TOKEN = 'your_toggl_api_token' #your_toggl_api_token

WAVE_API_BASE_URL = 'https://api.waveapps.com/'
TOGGL_API_BASE_URL = 'https://api.track.toggl.com/api/v8'

headers_wave = {
    'Authorization': f'Bearer {WAVE_API_TOKEN}',
    'Content-Type': 'application/json',
}

headers_toggl = {
    'Authorization': f'Basic {TOGGL_API_TOKEN}',
}

client_name = 'Client Name'

def get_or_create_wave_client(client_name):
    # Check if the client already exists in Wave
    response = requests.get(f'{WAVE_API_BASE_URL}/v1/contacts', headers=headers_wave)
    contacts = response.json()['contacts']

    client_id = next((contact['id'] for contact in contacts if contact['name'] == client_name), None)

    # If the client doesn't exist, create a new client
    if not client_id:
        payload = {
            'name': client_name,
        }

        response = requests.post(f'{WAVE_API_BASE_URL}/v1/contacts', headers=headers_wave, json=payload)

        if response.status_code == 201:
            client_id = response.json()['contact']['id']
            print(f'Wave: Client created. Client ID: {client_id}')
        else:
            print(f'Wave: Failed to create client. Status code: {response.status_code}, Error: {response.text}')

    else:
        print(f'Wave: Client already exists. Client ID: {client_id}')

    return client_id

def fetch_toggl_tasks():
    # Fetch new tasks from Toggl
    response = requests.get(f'{TOGGL_API_BASE_URL}/time_entries', headers=headers_toggl)
    tasks = response.json()
    return tasks

def create_or_update_invoice(client_id, items):
    # Check if an open invoice exists for the client in Wave
    response = requests.get(f'{WAVE_API_BASE_URL}/v1/invoices', headers=headers_wave)
    invoices = response.json()['invoices']

    open_invoices = [invoice for invoice in invoices if invoice['status'] == 'DRAFT' and invoice['contact']['id'] == client_id]

    if open_invoices:
        # If an open invoice exists, add the items to it
        invoice_id = open_invoices[0]['id']
        for item in items:
            response = requests.post(f'{WAVE_API_BASE_URL}/v1/invoices/{invoice_id}/items', headers=headers_wave, json=item)
            if response.status_code != 201:
                print(f'Wave: Failed to add item to invoice. Status code: {response.status_code}, Error: {response.text}')

        print(f'Wave: Items added to existing invoice (ID: {invoice_id}).')

    else:
        # If no open invoice exists, create a new invoice and add the items
        payload = {
            'invoice': {
                'customer': client_id,
                'items': items,
            }
        }

        response = requests.post(f'{WAVE_API_BASE_URL}/v1/invoices', headers=headers_wave, json=payload)

        if response.status_code == 201:
            invoice_id = response.json()['id']
            print(f'Wave: New invoice created (ID: {invoice_id}) with the items.')
        else:
            print(f'Wave: Failed to create invoice. Status code: {response.status_code}, Error: {response.text}')

def main():
    # Get or create the client in Wave
    client_id = get_or_create_wave_client(client_name)

    # Fetch new tasks from Toggl
    toggl_tasks = fetch_toggl_tasks()

    # Prepare items based on Toggl tasks (replace with your own logic)
    items = []
    for task in toggl_tasks:
        item_description = task['description']
        item_quantity = 1
        item_price = 100.00  # Replace with your own pricing logic
        items.append({
            'name': item_description,
            'quantity': item_quantity,
            'unit_price': {
                'amount': item_price,
                'currency': 'USD',  # Replace with your desired currency
            }
        })

    # Create or update the invoice in Wave
    create_or_update_invoice(client_id, items)

if __name__ == "__main__":
    main()

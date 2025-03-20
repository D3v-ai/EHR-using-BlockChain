from flask import Flask, render_template, request, session, redirect, url_for
from web3 import Web3
import json

app = Flask(__name__)
app.secret_key = 'EHR_WEBSITE_SECRET'  # Replace with a strong secret key

# Replace with your network URL (Ganache)
w3 = Web3(Web3.HTTPProvider('HTTP://0.0.0.0:8545'))

# Replace with your ABI (from EHR.json)
contract_abi = json.loads('''[
    {
      "inputs": [],
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_data",
          "type": "string"
        }
      ],
      "name": "addRecord",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_providerAddress",
          "type": "address"
        }
      ],
      "name": "authorizeProvider",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_patientAddress",
          "type": "address"
        },
        {
          "internalType": "uint256",
          "name": "_recordIndex",
          "type": "uint256"
        }
      ],
      "name": "getRecord",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_patientAddress",
          "type": "address"
        },
        {
          "internalType": "address",
          "name": "_providerAddress",
          "type": "address"
        }
      ],
      "name": "isAuthorized",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "",
          "type": "address"
        }
      ],
      "name": "patients",
      "outputs": [
        {
          "internalType": "uint256",
          "name": "recordCount",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "address",
          "name": "_providerAddress",
          "type": "address"
        }
      ],
      "name": "revokeProvider",
      "outputs": [],
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]''')

# Replace with your contract address
contract_address = '0x6c721A979e7E2B51156b485250D564eC78E8C7c3'

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def get_account():
    # Replace with your account management logic
    # For now, we'll use a placeholder
    return '0x6c721A979e7E2B51156b485250D564eC78E8C7c3'  # Replace with your account address

def add_record_to_blockchain(data):
    account = get_account()
    if account:
        tx_hash = contract.functions.addRecord(data).transact({'from': account})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    return False

def get_record_from_blockchain(patient_address, record_index):
    account = get_account()
    if account:
        record_data, timestamp = contract.functions.getRecord(patient_address, record_index).call({'from': account})
        return record_data, timestamp
    return None, None

def authorize_provider(provider_address):
    account = get_account()
    if account:
        tx_hash = contract.functions.authorizeProvider(provider_address).transact({'from': account})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    return False

def revoke_provider(provider_address):
    account = get_account()
    if account:
        tx_hash = contract.functions.revokeProvider(provider_address).transact({'from': account})
        w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    return False

def is_provider_authorized(patient_address, provider_address):
    account = get_account()
    if account:
        return contract.functions.isAuthorized(patient_address, provider_address).call({'from': account})
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        data = request.form['data']
        if add_record_to_blockchain(data):
            return redirect(url_for('index'))
        else:
            return "Failed to add record."
    return render_template('add_record.html')

@app.route('/view_record', methods=['GET', 'POST'])
def view_record():
    if request.method == 'POST':
        patient_address = request.form['patient_address']
        record_index = int(request.form['record_index'])
        record_data, timestamp = get_record_from_blockchain(patient_address, record_index)
        if record_data:
            return render_template('view_record.html', data=record_data, timestamp=timestamp)
        else:
            return "Record not found or not authorized."
    return render_template('view_record.html')

@app.route('/authorize', methods=['GET', 'POST'])
def authorize():
    if request.method == 'POST':
        provider_address = request.form['provider_address']
        if authorize_provider(provider_address):
            return redirect(url_for('index'))
        else:
            return "Failed to authorize provider."
    return render_template('authorize.html')

# Add similar routes for revoke_provider and is_provider_authorized

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify
from web3 import Web3
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = 'EHR_WEBSITE_SECRET'  # Replace with a strong secret key

# Replace with your network URL (Ganache)
ganache_url = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(ganache_url))

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
contract_address = os.getenv("CONTRACT_ADDRESS")
if not contract_address:
    raise ValueError("CONTRACT_ADDRESS not found in .env file")

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def get_account_from_private_key(private_key):
    try:
        account = w3.eth.account.from_key(private_key)
        return account
    except Exception as e:
        print(f"Error getting account: {e}")
        return None

# Routes for rendering HTML pages
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_record")
def add_record_page():
    return render_template("add_record.html")

@app.route("/view_record")
def view_record_page():
    return render_template("view_record.html")

@app.route("/authorize")
def authorize_page():
    return render_template("authorize.html")

@app.route("/revoke")
def revoke_page():
    return render_template("revoke_provider.html")

@app.route("/test_web3", methods=["GET"])
def test_web3():
    try:
        block_number = w3.eth.block_number
        return jsonify({"block_number": block_number})
    except Exception as e:
        print(f"Error in test_web3: {e}")
        return jsonify({"error": str(e)})

# Routes for form submissions (JSON responses)
@app.route("/add_record_submit", methods=["POST"])
def add_record_submit():
    data = request.get_json()
    try:
        account = get_account_from_private_key(data["privateKey"])
        if account:
            nonce = w3.eth.get_transaction_count(account.address)
            tx = contract.functions.addRecord(data["record"]).build_transaction({
                'gas': 200,
                'gasPrice': w3.eth.gas_price,
                'nonce': nonce,
            })
            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction())
            return jsonify({"tx_hash": tx_hash.hex()})
        else:
            return jsonify({"error": "Invalid private key."})
    except Exception as e:
        print(f"Error in add_record_submit: {e}")
        return jsonify({"error": str(e)})

@app.route("/get_record_submit", methods=["POST"])
def get_record_submit():
    data = request.get_json()
    try:
        record, timestamp = contract.functions.getRecord(data["patientAddress"], int(data["recordIndex"])).call({'from': data['providerAddress']})
        return jsonify({"record": record, "timestamp": timestamp})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/authorize_provider_submit", methods=["POST"])
def authorize_provider_submit():
    data = request.get_json()
    account = get_account_from_private_key(data["privateKey"])
    if account:
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.authorizeProvider(data["providerAddress"]).build_transaction({
            'gas': 200,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return jsonify({"tx_hash": tx_hash.hex()})
    else:
        return jsonify({"error": "Invalid private key."})

@app.route("/revoke_provider_submit", methods=["POST"])
def revoke_provider_submit():
    data = request.get_json()
    account = get_account_from_private_key(data["privateKey"])
    if account:
        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.revokeProvider(data["providerAddress"]).build_transaction({
            'gas': 200,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return jsonify({"tx_hash": tx_hash.hex()})
    else:
        return jsonify({"error": "Invalid private key."})

if __name__ == '__main__':
    app.run(debug=True)
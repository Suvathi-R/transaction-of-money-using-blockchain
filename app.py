from flask import Flask, render_template, request, redirect, url_for
import hashlib
import datetime
import json
import logging

app = Flask(__name__)

# Set up logging to console
logging.basicConfig(level=logging.DEBUG)

# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        # Create the genesis block
        self.create_block(proof=1, previous_hash='0')

    def create_block(self, proof, previous_hash, data=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'data': data
        }
        block_hash = self.hash(block)
        block['hash'] = block_hash  # Add the block hash to the block
        self.chain.append(block)
        app.logger.debug(f"New block created: {block}")  # Log the block creation
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while not check_proof:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self):
        previous_block = self.chain[0]
        block_index = 1
        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/')
def index():
    app.logger.debug(f"Current blockchain: {blockchain.chain}")  # Log the blockchain state
    return render_template('index.html', chain=blockchain.chain)

@app.route('/submit_transaction', methods=['POST'])
def submit_transaction():
    payee_name = request.form['payeeName']
    amount_transfer = request.form['amountTransfer']
    data = {
        'PayeeName': payee_name,
        'AmountTransfer': amount_transfer
    }
    previous_block = blockchain.get_previous_block()
    proof = blockchain.proof_of_work(previous_block['proof'])
    previous_hash = previous_block['hash']
    block = blockchain.create_block(proof, previous_hash, data)
    
    # Print the transaction details along with the hash in the terminal
    app.logger.debug(f"New transaction submitted:")
    app.logger.debug(f"PayeeName: {payee_name}")
    app.logger.debug(f"AmountTransfer: {amount_transfer}")
    app.logger.debug(f"Block Hash: {block['hash']}")
    app.logger.debug(f"Previous Hash: {previous_hash}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

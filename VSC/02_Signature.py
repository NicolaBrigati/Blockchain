from hashlib import sha256
import json
from ecdsa import SigningKey, VerifyingKey, SECP256k1
from datetime import datetime
import pickle

# Class to represent a transaction
class Transaction:
    def __init__(self, from_address, to_address, amount):
        """
        Initialize a transaction with sender address, recipient address, and amount.
        :param from_address: The sender's address (public key of the wallet).
        :param to_address: The recipient's address (public key of the wallet).
        :param amount: The amount of currency being transferred.
        """
        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount

    def calculate_hash(self):
        """
        Calculate a unique hash based on the transaction data.
        :return: The computed hash as a hexadecimal string.
        """
        hash_str = self.from_address + self.to_address + str(self.amount)
        return sha256(hash_str.encode('utf-8')).hexdigest()

    def sign_transaction(self, signing_key):
        """
        Sign the transaction using the sender's private key.
        :param signing_key: The sender's private key in hexadecimal format.
        """
        signing_key = SigningKey.from_string(bytearray.fromhex(signing_key), curve=SECP256k1)
        if signing_key.get_verifying_key().to_string().hex() != self.from_address:
            raise ValueError("You cannot sign this transaction.")

        hash_str = self.calculate_hash()
        self.signature = signing_key.sign(hash_str.encode('utf-8')).hex()

    def is_valid(self):
        """
        Validate the transaction by verifying the signature.
        :return: True if the transaction is valid, otherwise False.
        """
        if self.from_address is None:  # Mining rewards have no sender
            return True
        if not hasattr(self, 'signature') or len(self.signature) == 0:
            raise ValueError("Missing signature!")

        public_key = VerifyingKey.from_string(bytearray.fromhex(self.from_address), curve=SECP256k1)
        try:
            return public_key.verify(bytes.fromhex(self.signature), self.calculate_hash().encode('utf-8'))
        except Exception as e:
            print(e)
            return False


# Class to represent a block
class Block:
    def __init__(self, timestamp, transactions, previous_hash=''):
        """
        Initialize a block with a timestamp, transactions, and the hash of the previous block.
        :param timestamp: The time when the block is created.
        :param transactions: A list of transactions included in the block.
        :param previous_hash: The hash of the previous block in the chain.
        """
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.count = 0  # Used for proof-of-work (mining)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calculate a unique hash for the block based on its content.
        :return: The computed hash as a hexadecimal string.
        """
        hash_str = self.timestamp + json.dumps([tx.__dict__ for tx in self.transactions]) + self.previous_hash + str(self.count)
        return sha256(hash_str.encode('utf-8')).hexdigest()

    def mine_block(self, difficulty):
        """
        Perform proof-of-work to find a hash that starts with a specific number of zeros.
        :param difficulty: The number of leading zeros required in the hash.
        """
        while self.hash[:difficulty] != '0' * difficulty:
            self.count += 1
            self.hash = self.calculate_hash()

    def has_valid_transactions(self):  # Create has_valid_transactions to verify the chain
        for trans in self.__dict__['transactions']:
            if trans.is_valid() == False:
                return False
        return True

    def content(self):
        """
        Display the block's content in a readable format.
        """
        msg = self.__dict__.copy()  # Create content of the block
        msg_transactions = []
        for trans in msg['transactions']:
            if self.previous_hash != '0':
                msg_transactions.append(trans.__dict__)
        msg['transactions'] = msg_transactions
        
        print(json.dumps(msg, indent=2, default=str))
        print('----------------------------')


# Class to represent the blockchain
class Blockchain:
    def __init__(self):
        """
        Initialize the blockchain with a genesis block and set mining parameters.
        """
        self.chain = [self.generate_genesis_block()]
        self.pending_transactions = []
        self.reward = 100  # Mining reward
        self.difficulty = 3  # Number of leading zeros required in the hash for proof-of-work

    def generate_genesis_block(self):
        """
        Generate the genesis block (the first block in the chain).
        :return: The genesis block.
        """
        return Block("26/01/2025", [], "0")

    def mine_pending_transactions(self, mining_reward_address):
        """
        Mine all pending transactions and add the block to the chain.
        :param mining_reward_address: The address of the miner to receive the reward.
        """
        # Reward transaction for the miner
        reward_transaction = Transaction(None, mining_reward_address, self.reward)
        self.pending_transactions.append(reward_transaction)

        # Create a new block
        block = Block(datetime.now().strftime("%d/%m/%Y"), self.pending_transactions, self.chain[-1].hash)
        block.mine_block(self.difficulty)
        print("Block mined successfully!")
        self.chain.append(block)

        # Clear pending transactions after mining
        self.pending_transactions = []

    def add_transaction(self, transaction):
        """
        Add a new transaction to the list of pending transactions after validation.
        :param transaction: The transaction to be added.
        """
        if not transaction.from_address or not transaction.to_address:
            raise ValueError("Transaction must include from and to address.")

        if not transaction.is_valid():
            raise ValueError("Invalid transaction.")

        self.pending_transactions.append(transaction)

    def get_balance(self, address):  # Get visibility of the wallet's balance
        balance = 0
        for block in self.chain[1:]:  # Iterate over the blocks
            for trans in block.transactions:
                trans = trans.__dict__
                if trans['from_address'] == address:
                    balance -= trans['amount']
                elif trans['to_address'] == address:
                    balance += trans['amount']
        return balance

    def is_chain_valid(self):
        """
        Verify the integrity of the blockchain.
        :return: True if the chain is valid, otherwise False.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            if i == 0:
                if current_block.previous_hash != "0":
                    raise ValueError('Previous hash of first block is not 0!')
            else:
                previous_block = self.chain[i - 1]

            if current_block.has_valid_transactions() == False:
                self.chain = pickle.load(open('chain', 'rb'))  # Open file if an error is encountered
                raise ValueError(f'Current block {current_block.hash[0:8]} has invalid transactions')

            if current_block.hash != current_block.calculate_hash():
                self.chain = pickle.load(open('chain', 'rb'))  # Open file if an error is encountered
                raise ValueError(f"Block {i}: Current hash does not match calculated hash.")

            if current_block.previous_hash != previous_block.hash:
                self.chain = pickle.load(open('chain', 'rb'))  # Open file if an error is encountered
                raise ValueError(f"Block {i}: Previous hash does not match.")

        # Save the valid blockchain
        pickle.dump(self.chain, open('chain', 'wb'))
        print("Blockchain is valid.")

    def content(self):
        """
        Display the content of the entire blockchain.
        """
        for block in self.chain:
            block.content()

##################################
nic_chain = Blockchain() #create the chain

##################################
private_key_nic = SigningKey.generate(SECP256k1) #create the encripting
public_key_nic = private_key_nic.get_verifying_key()

private_key_nic = private_key_nic.to_string().hex()#transform keys as a string
public_key_nic = public_key_nic.to_string().hex()

private_key_kevin = SigningKey.generate(SECP256k1) #create the encripting
public_key_kevin = private_key_kevin.get_verifying_key()

private_key_kevin = private_key_kevin.to_string().hex()#transform keys as a string
public_key_kevin = public_key_kevin.to_string().hex()

private_key_bruce = SigningKey.generate(SECP256k1) #create the encripting
public_key_bruce = private_key_bruce.get_verifying_key()

private_key_bruce = private_key_bruce.to_string().hex()#transform keys as a string
public_key_bruce = public_key_bruce.to_string().hex()

#print(private_key_nic)
#print(public_key_nic)
#print(private_key_kevin)
#print(public_key_kevin)
#print(private_key_bruce)
#print(public_key_bruce)

########################################
# Create and sign transactions
tx1 = Transaction(public_key_nic, public_key_kevin, 100)
tx1.sign_transaction(private_key_nic)  # Sign the transaction with Nic's private key
nic_chain.add_transaction(tx1)

tx2 = Transaction(public_key_kevin, public_key_nic, 30)
tx2.sign_transaction(private_key_kevin)  # Sign the transaction with Kevin's private key
nic_chain.add_transaction(tx2)

# Mine the pending transactions
nic_chain.mine_pending_transactions(public_key_bruce)  # Reward Bruce for mining

########################################
nic_chain.content()

########################################
print('The amount in the wallet of Nic is', nic_chain.get_balance(public_key_nic))
print('The amount in the wallet of Kevin is', nic_chain.get_balance(public_key_kevin))
print('The amount in the wallet of Bruce is', nic_chain.get_balance(public_key_bruce))

#######################################
nic_chain.chain[1].transactions[0].amount = 200 #amend the chain, changing the amount

#######################################
nic_chain.is_chain_valid() #get error for invaliud blockchain after the amend


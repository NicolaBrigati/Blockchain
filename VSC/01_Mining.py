from hashlib import sha256 
import json  # to see the content of the block

class Block:  # create the class block
    def __init__(self, index, timestamp, data, previous_hash=''):  # create constructor and vars in the block
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.count = 0 #add function for mining and add it to the hash calculation
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()  # create the hash of this block

    # generate hash to represent the data of the block
    def calculate_hash(self):
        hash_str = str(self.index) + self.timestamp + self.data + self.previous_hash + str(self.count) # Combine data to create the string to hash
        return sha256(hash_str.encode('utf-8')).hexdigest()  # hash the string

    # generate a funciotn fo mining and add it to the block as a calculation of a new block
    def mining_block(self, difficulty): #add difficulty as a number for how many 0 we want into the ahsh number
        while self.hash[0:difficulty] != '0'*difficulty:
            self.count += 1
            self.hash = self.calculate_hash()
        print(f'Block Mined')
        
    def content(self):  # see the content of the block as a dictionary
        print(json.dumps(self.__dict__, indent=2, default=str))  # Use json.dumps instead of dump, fixed typo in 'self'

class Blockchain:  # create the class Blockchain (BC)
    def __init__(self):
        self.chain = [self.generate_genesis_block()]  # create series of blocks to insert into the BC. Considering the genesis block
        self.difficulty = 2 #set the difficulty for the blockchain
  
    def generate_genesis_block(self):
        return Block(0, '26/01/2025', 'Genesis Block')  # create genesis block, the previous_hash (Block) considering like null
    
    def add_block(self, new_block):  # create function to add block
        new_block.previous_hash = self.chain[-1].hash
        #new_block.hash = new_block.calculate_hash()
        new_block.mining_block(self.difficulty)
        self.chain.append(new_block)  # Fixed error: 'new.block' should be 'new_block'

    def is_chain_valid(self):  # Define a method to validate the blockchain
        for i in range(1, len(self.chain)):  # Iterate over the chain starting from the second block
            current_block = self.chain[i]  # Get the current block
            previous_block = self.chain[i-1]  # Get the previous block
        
            # Check if the current block's hash matches the calculated hash
            if current_block.hash != current_block.calculate_hash():  
                raise ValueError(f'current_block.hash != current_block.calculate_hash()')  # Raise an error if the hashes don't match
        
            # Check if the current block's `previous_hash` matches the hash of the previous block
            elif current_block.previous_hash != previous_block.hash:  
                raise ValueError(f'current_block.previous_hash != previous_block.hash')  # Raise an error if the previous hashes don't match
        
        print('Valid Blockchain')  # If all checks pass, the blockchain is valid

    def content(self):  # Added method to print content of the blockchain
        for block in self.chain:
            block.content()  # Function to see what's inside the block created after the hash


####################
nic_chain = Blockchain() #create the chain
####################
block1 = Block(1, '27/01/2025','Transaction Number 1') #add a block to the chain
nic_chain.add_block(block1)

block2 = Block(2, '27/01/2025','Transaction Number 2') #add another block to the chain
nic_chain.add_block(block2)
####################
nic_chain.is_chain_valid()
####################
nic_chain.content()
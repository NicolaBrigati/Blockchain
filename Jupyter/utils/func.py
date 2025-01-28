import os
import yaml

with open('./config.yaml') as f: #recall the function yaml
    config = yaml.safe_load(f)

def get_keys(owner):
    with open(os.path.join(config['path_credentials'], 'keys_'+owner), 'r') as file:
        for line in file:
            if 'private_key' in line:
                private_key = line.split(':') [-1].strip() #split the key with : to get the key, see the credentials file of the users
            if 'public_key' in line:
                public_key = line.split(':') [-1].strip() #split the key with : to get the key, see the credentials file of the users 
    return private_key, public_key
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import sys

def generate_key(owner):  #owner is the user that has the private and public keys
    private_key = SigningKey.generate(SECP256k1)
    public_key = private_key.get_verifying_key()
    private_key = private_key.to_string().hex()
    public_key = public_key.to_string().hex()
    
    output = f"""
private_key: {private_key}
public_key : {public_key}
    """
    text_file = open('keys_'+owner, 'w')
    text_file.write(output)
    text_file.close

if __name__ == '__main__':
    generate_key(sys.argv[1])
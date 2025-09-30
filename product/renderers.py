import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from rest_framework.renderers import BaseRenderer
import json
from Crypto.Util.Padding import unpad

# here the string gotten from the environmental variable is converted to bytes
AES_SECRET_KEY = "WSxxfrhpbtRXrfSiq9Mho25SOcjdZmug"
AES_IV = "whsbdhgntkgngmhk"

class CustomAesRenderer(BaseRenderer):
    media_type = 'application/octet-stream'
    format = 'aes'

    def render(self, data, media_type=None, renderer_context=None):
        plaintext = json.dumps(data)
        padded_plaintext = pad(plaintext.encode(), 16)
        cipher = AES.new(AES_SECRET_KEY.encode("utf8"), AES.MODE_CBC, AES_IV.encode("utf8"))
        ciphertext = cipher.encrypt(padded_plaintext)
        ciphertext_b64 = base64.b64encode(ciphertext).decode()
        response = {'ciphertext': ciphertext_b64}
        return json.dumps(response)



def decrypt_data(data):
    encrypted_data = data['ciphertext']
    enc = base64.b64decode(encrypted_data)
    cipher = AES.new(AES_SECRET_KEY.encode("utf8"), AES.MODE_CBC, AES_IV.encode("utf8"))
    try:
        decrypted_data = unpad(cipher.decrypt(enc),16)
        decrypted_data = json.loads(decrypted_data)
        data = {
            "data" : decrypted_data
        }
        print(data)
    except Exception as e:
        print(e)
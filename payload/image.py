import io
import PIL
from PIL import Image


# Path is the path to the image you wish to send
def packet_creation(path):
    im = Image.open(path)
    
    # Pack image data into
    
    data = im.tobytes()
    packed_data = [str(data[i:i+8], "hex") for i in range(0, len(data), 8)]
    return packed_data

def get_image_from_array(data):
    byte_data = bytearray(data, "hex")

    #for piece in data:
     #   byte_data = (byte_data << 8) + int.from_bytes(piece, "big")

    size = [512,341]
    im = PIL.Image.frombytes("RGB", size, byte_data)

    im.show()

packets = packet_creation("data/test_image.jpeg")
get_image_from_array(packets)
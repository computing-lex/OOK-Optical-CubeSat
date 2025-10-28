from PIL import Image
import PIL

# Path is the path to the image you wish to send
def packet_creation(path):
    im = Image.open(path)
    
    # Pack image data into
    data = im.tobytes()
    packed_data = [data[i:i+8] for i in range(0, len(data), 8)]
    return packed_data

def get_image_from_array(data):
    combined_data = []
    for piece in data:
        combined_data = combined_data + [piece]
    im = PIL.Image.frombytes(combined_data)

    im.show()

packets = packet_creation("data/test_image.jpeg")
get_image_from_array(packets)
import os
import json
import random
from PIL import Image, ImageChops
import threading
from concurrent.futures import ThreadPoolExecutor
import webbrowser

def read_parameters():
    with open("parameters.json", "r") as file:
        parameters = json.load(file)
    return parameters

def color_element(layer_path, overlay_color):
    image = Image.open(layer_path).convert("RGBA")
    color_layer = Image.new("RGBA", image.size, overlay_color)
    alpha = image.getchannel('A')
    alpha_thresh = alpha.point(lambda p: p if p > 0 else 0)
    color_layer.putalpha(alpha_thresh)
    result_image = ImageChops.overlay(image, color_layer)
    return result_image

def resize_image(image, target_size):
    width, height = image.size
    if width > height:
        new_width = target_size
        new_height = int(target_size * height / width)
    else:
        new_height = target_size
        new_width = int(target_size * width / height)
    return image.resize((new_width, new_height), Image.LANCZOS)

def generate_image(order, background_color, body_type, body_color, accent_color, eyes_type, mouth_type):
    generation_dir = "generation"
    background_path = os.path.join("assets", "background.png")
    body_type_path = os.path.join("assets", "body-type", f"{body_type}.png")
    
    outline_asset = "outline_black" if accent_color == "#181818" else "outline_white"
    eyes_asset = f"{eyes_type}.png"
    mouth_asset = f"{mouth_type}.png"
    
    outline_path = os.path.join("assets", f"{outline_asset}.png")
    eyes_path = os.path.join("assets", "eyes-type_black" if accent_color == "#181818" else "eyes-type_white", eyes_asset)
    mouth_path = os.path.join("assets", "mouth-type_black" if accent_color == "#181818" else "mouth-type_white", mouth_asset)

    print(f"Order: {order}")

    background_image = color_element(background_path, background_color)

    body_image = Image.open(body_type_path).convert("RGBA")
    body_image = color_element(body_type_path, body_color)
    background_image.paste(body_image, (0, 0), body_image)

    outline_image = Image.open(outline_path).convert("RGBA")
    eyes_image = Image.open(eyes_path).convert("RGBA")
    mouth_image = Image.open(mouth_path).convert("RGBA")

    background_image.paste(outline_image, (0, 0), outline_image)
    background_image.paste(eyes_image, (0, 0), eyes_image)
    background_image.paste(mouth_image, (0, 0), mouth_image)

    # Save the full-resolution image as WEBP in the generation directory
    output_image_path = os.path.join(generation_dir, f"{order}.webp")
    background_image.save(output_image_path, format="WEBP")
    print(f"Saved full-resolution image: {output_image_path}")

    # Resize the image to 120x120 pixels
    resized_image = resize_image(background_image, 120)

    # Save the resized image as PNG in the 25ks directory
    output_image_path = os.path.join("25ks", f"{order}.png")
    resized_image.save(output_image_path, format="PNG")
    print(f"Saved resized image: {output_image_path}")

    metadata = {
        "Artwork Number": f"#{order}",
        "Background Color": background_color,
        "Body Type": f"#{os.path.splitext(os.path.basename(body_type_path))[0]}",
        "Body Color": body_color,
        "Accent Color": accent_color,
        "Eyes Type": f"#{eyes_asset[:-4]}",
        "Mouth Type": f"#{mouth_asset[:-4]}"
    }
    output_metadata_path = os.path.join("metadata", f"{order}.json")
    with open(output_metadata_path, "w") as file:
        json.dump(metadata, file)
    print(f"Saved metadata: {output_metadata_path}")


def clear_directories():
    for directory in ["generation", "metadata", "25ks"]:
        if os.path.exists(directory):
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            os.makedirs(directory)

def generate_images(num_images):
    parameters = read_parameters()
    background_colors = parameters["background_color"]
    body_colors = parameters["body_color"]
    accent_colors = parameters["accent_color"]

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(1, num_images + 1):
            background_color = random.choice(background_colors)
            body_color = random.choice(body_colors)
            accent_color = random.choice(accent_colors)
            body_type = random.randint(1, 34)
            eyes_type = random.randint(1, 8)
            mouth_type = random.randint(1, 22)
            executor.submit(generate_image, i, background_color, body_type, body_color, accent_color, eyes_type, mouth_type)

    print("Generation complete.")

if __name__ == "__main__":
    print("""
                ░░░░░░  ░░░░░░░░                                    
            ░░░░░░░░░░░░░░░░░░                                      
          ░░░░░░░░░░░░░░░░░░░░      ░░░░░░                          
        ░░░░░░░░░░░░░░░░░░░░░░░░  ░░░░░░                            
      ░░░░    ░░░░    ░░░░░░░░░░░░░░░░                              
      ░░  ██  ░░  ██  ░░░░░░░░░░░░░░░░                              
      ░░  ████    ████  ░░░░░░░░░░░░░░                              
      ░░░░    ░░░░      ░░░░░░░░░░░░░░                              
      ░░▓▓░░░░░░░░░░░░░░▓▓░░░░░░░░░░░░                              
      ░░░░▓▓▓▓░░░░░░▓▓▓▓░░░░░░░░  ░░░░                              
        ░░░░░░▓▓▓▓▓▓░░░░░░░░░░    ░░░░░░                            
            ░░░░░░░░░░░░░░░░        ░░░░░░                          
                        ░░░░░░                   
    ░▒█▀▀█░▒█▀▀▀█░▒█░░░░▒█▀▀▄░▒█▀▀▀░▀█▀░▒█▀▀▀█░▒█░▒█░░░░▒█▀▀█░▒█░░▒█
    ░▒█░▄▄░▒█░░▒█░▒█░░░░▒█░▒█░▒█▀▀░░▒█░░░▀▀▀▄▄░▒█▀▀█░▄▄░▒█▄▄█░▒▀▄▄▄▀
    ░▒█▄▄▀░▒█▄▄▄█░▒█▄▄█░▒█▄▄█░▒█░░░░▄█▄░▒█▄▄▄█░▒█░▒█░▀▀░▒█░░░░░░▒█░░
    """)
    clear_directories()
    generate_images(2100)  # Specify the number of images to generate


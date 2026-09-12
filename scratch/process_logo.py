import os
from PIL import Image

def process_logo(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size

    datas = img.getdata()
    new_data = []

    # Filter out checkerboard background pixels (shades of light gray/white grid)
    # The checkerboard consists of light gray (~204,204,204 / #ccc) and pure white (255,255,255)
    for item in datas:
        r, g, b, a = item
        # Check if color is part of the checkerboard grid background (high brightness, low saturation gray or white)
        is_gray_checker = (abs(r - g) < 15 and abs(g - b) < 15 and r > 180 and g > 180 and b > 180)
        is_white_checker = (r > 240 and g > 240 and b > 240)

        if is_gray_checker or is_white_checker:
            new_data.append((255, 255, 255, 0)) # Make transparent
        else:
            new_data.append((r, g, b, a))

    img.putdata(new_data)

    # Crop to non-transparent bounding box
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    # Add small 10px padding around cropped logo
    padded_w = img.width + 20
    padded_h = img.height + 20
    padded_img = Image.new("RGBA", (padded_w, padded_h), (255, 255, 255, 0))
    padded_img.paste(img, (10, 10))

    padded_img.save(output_path, "PNG")
    print(f"Processed logo saved to {output_path}. Size: {padded_img.size}")

if __name__ == "__main__":
    src = r"C:\Users\HP\.gemini\antigravity-ide\brain\c964fcef-2a2a-4e93-baeb-1427a02df900\.user_uploaded\media_1789187583139.png"
    dst = r"c:\Users\HP\OneDrive\Desktop\ProjectPartner\frontend\static\images\logo.png"
    process_logo(src, dst)

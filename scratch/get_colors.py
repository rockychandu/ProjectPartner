from PIL import Image

img = Image.open(r"c:\Users\HP\OneDrive\Desktop\ProjectPartner\frontend\static\images\logo.png").convert("RGBA")
colors = img.getcolors(maxcolors=600000)
# Sort by count
colors.sort(key=lambda x: x[0], reverse=True)

print("Top dominant non-transparent colors:")
count = 0
for cnt, col in colors:
    r, g, b, a = col
    if a > 200 and not (r > 230 and g > 230 and b > 230):
        print(f"Hex: #{r:02x}{g:02x}{b:02x} | RGB: ({r},{g},{b}) | Count: {cnt}")
        count += 1
        if count >= 10:
            break

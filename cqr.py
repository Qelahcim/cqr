import argparse
import qrcode
import qrcode.image.svg as svg
from lxml import etree
import base64

def generate_qr(url, output_file, fg_color, bg_color, logo_path, logo_scale=1.0):
    # Create QR code with specified colors
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create SVG image
    factory = svg.SvgPathImage
    img = qr.make_image(fill_color=fg_color, back_color=bg_color, image_factory=factory)
    
    # Save or modify SVG
    if logo_path:
        add_logo_to_svg(img, output_file, logo_path, logo_scale)
    else:
        img.save(output_file)

def add_logo_to_svg(img, output_file, logo_path, logo_scale=1.0):
    # Get SVG as bytes
    svg_bytes = img.to_string()
    
    try:
        # Parse QR SVG
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        root = etree.fromstring(svg_bytes, parser=parser)
        
        # Get QR dimensions from viewBox
        viewbox = root.get('viewBox')
        if viewbox:
            _, _, qr_width, qr_height = map(float, viewbox.split())
        else:
            # Fallback to width/height attributes
            qr_width = float(root.get('width', 100))
            qr_height = float(root.get('height', 100))
        
        # Calculate base logo size (15% of QR size) and apply scale
        base_logo_size = min(qr_width, qr_height) * 0.15
        logo_size = base_logo_size * logo_scale
        x_position = (qr_width - logo_size) / 2
        y_position = (qr_height - logo_size) / 2
        
        # Read logo file content
        with open(logo_path, 'rb') as f:
            logo_data = f.read()
        
        # Create image element with embedded logo
        image_element = etree.Element("image")
        image_element.set("x", str(x_position))
        image_element.set("y", str(y_position))
        image_element.set("width", str(logo_size))
        image_element.set("height", str(logo_size))
        image_element.set("preserveAspectRatio", "xMidYMid meet")
        
        # Create data URI for the logo
        if logo_path.lower().endswith('.svg'):
            mime_type = 'image/svg+xml'
            encoded_logo = base64.b64encode(logo_data).decode('utf-8')
        else:
            mime_type = 'image/png'
            encoded_logo = base64.b64encode(logo_data).decode('utf-8')
        
        data_uri = f"data:{mime_type};base64,{encoded_logo}"
        image_element.set("href", data_uri)
        
        # Add the image to the QR code
        root.append(image_element)
        
        # Save the modified SVG
        with open(output_file, 'wb') as f:
            f.write(etree.tostring(root, pretty_print=True))
            
    except Exception as e:
        print(f"Error adding logo: {e}")
        # Fallback to saving QR without logo
        with open(output_file, 'wb') as f:
            f.write(svg_bytes)
        print("Saved QR code without logo due to error")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='QR Code Generator')
    parser.add_argument('-u', '--url', required=True, help='URL to encode')
    parser.add_argument('-o', '--output', default='qrcode.svg', help='Output file (default: qrcode.svg)')
    parser.add_argument('-f', '--fg', default='#000000', help='Foreground color (default: #000000)')
    parser.add_argument('-b', '--bg', default='#FFFFFF', help='Background color (default: #FFFFFF)')
    parser.add_argument('-l', '--logo', help='Path to SVG or PNG logo')
    parser.add_argument('-ls', '--logo-scale', type=float, default=1.0,
                        help='Logo size scaling factor (default: 1.0). 1.0 = 15%% of QR size, 1.2 = 120%% of that size, etc.')
    
    args = parser.parse_args()
    
    generate_qr(
        args.url,
        args.output,
        fg_color=args.fg,
        bg_color=args.bg,
        logo_path=args.logo,
        logo_scale=args.logo_scale
    )
    print(f'QR code generated: {args.output}')
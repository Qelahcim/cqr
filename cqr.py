import argparse
import qrcode
import qrcode.image.svg as svg
from lxml import etree

def generate_qr(url, output_file, fg_color, bg_color, logo_path):
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
        add_logo_to_svg(img, output_file, logo_path)
    else:
        img.save(output_file)

def add_logo_to_svg(img, output_file, logo_path):
    # Get SVG as string
    svg_str = img.to_string()
    root = etree.fromstring(svg_str.encode('utf-8'))
    
    # Add logo to center
    with open(logo_path, 'rb') as f:
        logo = etree.parse(f)
        logo_root = logo.getroot()
        
        # Scale and position logo (15% size, centered)
        qr_size = int(root.get('width'))
        logo_size = int(qr_size * 0.15)
        position = (qr_size - logo_size) // 2
        
        logo_root.set('width', str(logo_size))
        logo_root.set('height', str(logo_size))
        logo_root.set('x', str(position))
        logo_root.set('y', str(position))
        
        root.append(logo_root)
    
    # Save modified SVG
    with open(output_file, 'wb') as f:
        f.write(etree.tostring(root))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='QR Code Generator')
    parser.add_argument('-u', '--url', required=True, help='URL to encode')
    parser.add_argument('-o', '--output', default='qrcode.svg', help='Output file (default: qrcode.svg)')
    parser.add_argument('-f', '--fg', default='#000000', help='Foreground color (default: #000000)')
    parser.add_argument('-b', '--bg', default='#FFFFFF', help='Background color (default: #FFFFFF)')
    parser.add_argument('-l', '--logo', help='Path to SVG logo')
    
    args = parser.parse_args()
    
    generate_qr(
        args.url,
        args.output,
        fg_color=args.fg,
        bg_color=args.bg,
        logo_path=args.logo
    )
    print(f'QR code generated: {args.output}')
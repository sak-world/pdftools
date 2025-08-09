#!/usr/bin/env python3
"""
Robust Watermark Generator - Complete Solution
Generate images in selected sizes with optional watermarks (center or ribbon style)
"""

"""
YOUR COMPLETE TOOLKIT - Command Reference

For Testing & Development:
    python robust_generator.py print-size.png --interactive
    Choose "single size" + "ribbon watermarks" to test quickly

For Etsy Production:
    python robust_generator.py print-size.png --sizes popular --ribbon --text "eliteblings.etsy.com" --ribbons 6 --angle 0 --opacity 140
    Gets your 4 main selling sizes ready fast

For Complete Packages:
    python robust_generator.py print-size.png --all --ribbon --text "eliteblings.etsy.com" --ribbons 6 --angle 0 --opacity 140
    Full 9-size professional package

For Customer Delivery:
    python robust_generator.py print-size.png --all --no-watermark
    Clean files for paying customers

PERFECT ETSY WORKFLOW:
1. 🧪 Test: Interactive mode → single size → ribbon settings
2. 📸 Preview: Popular sizes → for Etsy listing photos  
3. 📦 Package: All sizes → complete digital download
4. ✨ Clean: All sizes → customer delivery files

Size Options:
    --all           All 9 sizes
    --sizes popular 4 popular sizes (5×7, 8×10, 11×14, 16×20)
    --sizes small   3 small sizes (5×7, 8×10, 8.5×11)
    --sizes large   4 large sizes (16×20, 18×24, 20×24, 24×36)
    --sizes single  Choose 1 size interactively

Watermark Options:
    --no-watermark  Clean images (for customers)
    --center        Single center watermark
    --ribbon        Horizontal ribbon watermarks

Ribbon Settings:
    --ribbons 3-10  Number of ribbon stripes
    --angle 0       Horizontal ribbons (0°)
    --angle -15     Slightly angled ribbons
    --opacity 120   Subtle watermarks
    --opacity 180   Strong watermarks
"""

from PIL import Image, ImageDraw, ImageFont
import os
import sys
import math

def load_font(font_size):
    """Load the best available font"""
    
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                continue
    
    return ImageFont.load_default()

def add_center_watermark(image, text="eliteblings.etsy.com", opacity=120):
    """Add a simple center watermark"""
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Font size based on image size
    font_size = max(30, int(image.width * 0.05))
    font = load_font(font_size)
    
    # Get text size
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width, text_height = draw.textsize(text, font=font)
    
    # Center position
    x = (image.width - text_width) // 2
    y = (image.height - text_height) // 2
    
    # Draw with shadow
    shadow_offset = max(2, font_size // 20)
    draw.text((x + shadow_offset, y + shadow_offset), text, 
              font=font, fill=(0, 0, 0, opacity // 2))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))
    
    watermarked = Image.alpha_composite(image, overlay)
    return watermarked.convert('RGB')

def add_ribbon_watermarks(image, text="eliteblings.etsy.com", opacity=120, ribbon_count=5, angle=0):
    """Add horizontal ribbon watermarks with equal spacing"""
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    
    # Font size based on image size
    font_size = max(20, int(image.width * 0.025))
    font = load_font(font_size)
    
    # Set colors
    text_color = (255, 255, 255, opacity)
    shadow_color = (0, 0, 0, opacity // 3)
    
    # Calculate ribbon spacing
    vertical_spacing = image.height // (ribbon_count + 1)
    
    # Create each ribbon
    for i in range(ribbon_count):
        ribbon_y = vertical_spacing * (i + 1)
        
        # Create the ribbon watermark
        ribbon_img = create_ribbon_watermark(
            image.width, text, font, angle, text_color, shadow_color, font_size
        )
        
        # Calculate paste position
        paste_x = 0
        paste_y = ribbon_y - ribbon_img.height // 2
        paste_y = max(0, min(paste_y, image.height - ribbon_img.height))
        
        # Paste the ribbon
        overlay.paste(ribbon_img, (paste_x, paste_y), ribbon_img)
    
    # Combine layers
    watermarked = Image.alpha_composite(image, overlay)
    return watermarked.convert('RGB')

def create_ribbon_watermark(image_width, text, font, angle, text_color, shadow_color, font_size):
    """Create a single horizontal ribbon with repeating text"""
    
    # Measure text
    temp_img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    temp_draw = ImageDraw.Draw(temp_img)
    
    try:
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        text_width, text_height = temp_draw.textsize(text, font=font)
    
    # Calculate repetitions
    text_spacing = text_width + 60
    ribbon_width = int(image_width * 1.5)
    ribbon_height = max(80, text_height + 40)
    
    ribbon_img = Image.new('RGBA', (ribbon_width, ribbon_height), (0, 0, 0, 0))
    ribbon_draw = ImageDraw.Draw(ribbon_img)
    
    # Draw repeated text
    current_x = 0
    y = (ribbon_height - text_height) // 2
    
    while current_x < ribbon_width:
        # Draw shadow
        shadow_offset = max(1, font_size // 30)
        ribbon_draw.text((current_x + shadow_offset, y + shadow_offset), 
                        text, font=font, fill=shadow_color)
        # Draw main text
        ribbon_draw.text((current_x, y), text, font=font, fill=text_color)
        current_x += text_spacing
    
    # Rotate if needed
    if angle != 0:
        ribbon_img = ribbon_img.rotate(angle, expand=True)
    
    return ribbon_img

def prompt_size_selection():
    """Interactive prompt for size selection"""
    
    print("\n🎯 Size Selection")
    print("=" * 50)
    print("Choose which sizes to generate:")
    print("1. All 9 sizes (recommended for Etsy)")
    print("2. Popular sizes only (5×7, 8×10, 11×14, 16×20)")
    print("3. Small sizes (5×7, 8×10, 8.5×11)")
    print("4. Large sizes (16×20, 18×24, 20×24, 24×36)")
    print("5. Custom selection")
    print("6. Single size only")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == "1":
                return "all", None
            elif choice == "2":
                return "popular", ["5x7", "8x10", "11x14", "16x20"]
            elif choice == "3":
                return "small", ["5x7", "8x10", "8.5x11"]
            elif choice == "4":
                return "large", ["16x20", "18x24", "20x24", "24x36"]
            elif choice == "5":
                return prompt_custom_selection()
            elif choice == "6":
                return prompt_single_size()
            else:
                print("❌ Please enter a number between 1-6")
                
        except KeyboardInterrupt:
            print("\n\n👋 Cancelled by user")
            return None, None

def prompt_custom_selection():
    """Let user select specific sizes"""
    
    all_sizes = ["5x7", "8x10", "8.5x11", "11x14", "12x16", "16x20", "18x24", "20x24", "24x36"]
    
    print("\n📏 Available sizes:")
    for i, size in enumerate(all_sizes, 1):
        print(f"{i:2}. {size}")
    
    print("\nEnter size numbers separated by commas (e.g., 1,2,4,6)")
    print("Or enter ranges (e.g., 1-4,6,8-9)")
    
    while True:
        try:
            selection = input("Your selection: ").strip()
            
            if not selection:
                print("❌ Please enter at least one size")
                continue
            
            selected_sizes = []
            parts = selection.split(',')
            
            for part in parts:
                part = part.strip()
                
                if '-' in part:
                    # Handle ranges
                    start, end = part.split('-')
                    start_idx = int(start) - 1
                    end_idx = int(end) - 1
                    
                    if 0 <= start_idx < len(all_sizes) and 0 <= end_idx < len(all_sizes):
                        for i in range(start_idx, end_idx + 1):
                            if all_sizes[i] not in selected_sizes:
                                selected_sizes.append(all_sizes[i])
                    else:
                        print(f"❌ Invalid range: {part}")
                        break
                else:
                    # Handle single numbers
                    idx = int(part) - 1
                    if 0 <= idx < len(all_sizes):
                        if all_sizes[idx] not in selected_sizes:
                            selected_sizes.append(all_sizes[idx])
                    else:
                        print(f"❌ Invalid size number: {part}")
                        break
            else:
                if selected_sizes:
                    print(f"✓ Selected sizes: {', '.join(selected_sizes)}")
                    return "custom", selected_sizes
                else:
                    print("❌ No valid sizes selected")
                    
        except ValueError:
            print("❌ Invalid input. Use numbers and commas only")
        except KeyboardInterrupt:
            print("\n\n👋 Cancelled by user")
            return None, None

def prompt_single_size():
    """Let user select a single size"""
    
    all_sizes = ["5x7", "8x10", "8.5x11", "11x14", "12x16", "16x20", "18x24", "20x24", "24x36"]
    
    print("\n📏 Choose a single size:")
    for i, size in enumerate(all_sizes, 1):
        print(f"{i}. {size}")
    
    while True:
        try:
            choice = input("\nEnter size number (1-9): ").strip()
            idx = int(choice) - 1
            
            if 0 <= idx < len(all_sizes):
                selected_size = all_sizes[idx]
                print(f"✓ Selected: {selected_size}")
                return "single", [selected_size]
            else:
                print("❌ Please enter a number between 1-9")
                
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n👋 Cancelled by user")
            return None, None

def prompt_watermark_options():
    """Interactive prompt for watermark options"""
    
    print("\n💧 Watermark Options")
    print("=" * 50)
    print("Choose watermark style:")
    print("1. No watermarks (clean images)")
    print("2. Center watermark (single text in center)")
    print("3. Ribbon watermarks (horizontal stripes)")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                return {"style": "none"}
            elif choice == "2":
                return prompt_center_watermark_options()
            elif choice == "3":
                return prompt_ribbon_watermark_options()
            else:
                print("❌ Please enter a number between 1-3")
                
        except KeyboardInterrupt:
            print("\n\n👋 Cancelled by user")
            return None

def prompt_center_watermark_options():
    """Get center watermark settings"""
    
    print("\n🎯 Center Watermark Settings")
    
    # Get text
    text = input("Watermark text (default: 'eliteblings.etsy.com'): ").strip()
    if not text:
        text = "eliteblings.etsy.com"
    
    # Get opacity
    while True:
        try:
            opacity_input = input("Opacity 50-255 (default: 150): ").strip()
            if not opacity_input:
                opacity = 150
                break
            opacity = int(opacity_input)
            if 50 <= opacity <= 255:
                break
            else:
                print("❌ Opacity must be between 50-255")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return {
        "style": "center",
        "text": text,
        "opacity": opacity
    }

def prompt_ribbon_watermark_options():
    """Get ribbon watermark settings"""
    
    print("\n🎗️ Ribbon Watermark Settings")
    
    # Get text
    text = input("Watermark text (default: 'eliteblings.etsy.com'): ").strip()
    if not text:
        text = "eliteblings.etsy.com"
    
    # Get opacity
    while True:
        try:
            opacity_input = input("Opacity 50-255 (default: 120): ").strip()
            if not opacity_input:
                opacity = 120
                break
            opacity = int(opacity_input)
            if 50 <= opacity <= 255:
                break
            else:
                print("❌ Opacity must be between 50-255")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Get ribbon count
    while True:
        try:
            ribbons_input = input("Number of ribbons 3-10 (default: 5): ").strip()
            if not ribbons_input:
                ribbon_count = 5
                break
            ribbon_count = int(ribbons_input)
            if 3 <= ribbon_count <= 10:
                break
            else:
                print("❌ Ribbon count must be between 3-10")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Get angle
    while True:
        try:
            angle_input = input("Ribbon angle -45 to 45 degrees (default: 0): ").strip()
            if not angle_input:
                angle = 0
                break
            angle = int(angle_input)
            if -45 <= angle <= 45:
                break
            else:
                print("❌ Angle must be between -45 and 45")
        except ValueError:
            print("❌ Please enter a valid number")
    
    return {
        "style": "ribbon",
        "text": text,
        "opacity": opacity,
        "ribbon_count": ribbon_count,
        "angle": angle
    }

def create_images(input_image_path, interactive=False, watermark_options=None, size_options=None):
    """
    Main function to create images with selected sizes and watermarks
    """
    
    # All available print sizes
    all_print_sizes = {
        "5x7": (1500, 2100),
        "8x10": (2400, 3000),
        "8.5x11": (2550, 3300),
        "11x14": (3300, 4200),
        "12x16": (3600, 4800),
        "16x20": (4800, 6000),
        "18x24": (5400, 7200),
        "20x24": (6000, 7200),
        "24x36": (7200, 10800)
    }
    
    # Determine sizes to create
    if interactive:
        if size_options is None:
            selection_type, selected_sizes = prompt_size_selection()
            if selection_type is None:
                return
        else:
            selection_type, selected_sizes = size_options
        
        if selection_type == "all":
            print_sizes = all_print_sizes
            size_description = "all 9 sizes"
        else:
            print_sizes = {size: all_print_sizes[size] for size in selected_sizes if size in all_print_sizes}
            size_description = f"{len(print_sizes)} selected sizes"
        
        # Get watermark options
        if watermark_options is None:
            watermark_config = prompt_watermark_options()
            if watermark_config is None:
                return
        else:
            watermark_config = watermark_options
            
    else:
        # Non-interactive: use defaults
        print_sizes = all_print_sizes
        size_description = "all 9 sizes"
        watermark_config = watermark_options or {"style": "none"}
    
    # Create output folder
    base_name = os.path.splitext(os.path.basename(input_image_path))[0]
    
    if watermark_config["style"] == "none":
        output_folder = f"{base_name}_clean_prints"
    elif watermark_config["style"] == "center":
        output_folder = f"{base_name}_center_watermarked"
    else:
        output_folder = f"{base_name}_ribbon_watermarked"
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Display settings
    print(f"\n🖼️  Processing: {input_image_path}")
    print(f"📏 Creating: {size_description}")
    print(f"💧 Watermark: {watermark_config['style']}")
    
    if watermark_config["style"] != "none":
        print(f"💫 Text: '{watermark_config['text']}'")
        print(f"🎨 Opacity: {watermark_config['opacity']}")
        
        if watermark_config["style"] == "ribbon":
            print(f"🎗️ Ribbons: {watermark_config['ribbon_count']}, Angle: {watermark_config['angle']}°")
    
    print(f"📁 Output folder: {output_folder}")
    print("=" * 70)
    
    try:
        with Image.open(input_image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
                print("✓ Converted to RGB")
            
            # Process each selected size
            for size_name, (width, height) in print_sizes.items():
                print(f"\n📏 Creating {size_name} ({width}×{height} pixels)...")
                
                # Resize image
                resized = img.resize((width, height), Image.Resampling.LANCZOS)
                
                # Apply watermark based on style
                if watermark_config["style"] == "center":
                    final_image = add_center_watermark(
                        resized,
                        watermark_config["text"],
                        watermark_config["opacity"]
                    )
                elif watermark_config["style"] == "ribbon":
                    final_image = add_ribbon_watermarks(
                        resized,
                        watermark_config["text"],
                        watermark_config["opacity"],
                        watermark_config["ribbon_count"],
                        watermark_config["angle"]
                    )
                else:
                    # No watermark
                    final_image = resized
                
                # Save
                if watermark_config["style"] == "none":
                    filename = f"{base_name}_{size_name}_300dpi_clean.jpg"
                else:
                    filename = f"{base_name}_{size_name}_300dpi_watermarked.jpg"
                    
                filepath = os.path.join(output_folder, filename)
                final_image.save(filepath, 'JPEG', quality=95, dpi=(300, 300))
                
                print(f"  ✅ Saved: {filename}")
        
        print("=" * 70)
        print(f"🎉 SUCCESS! Created {len(print_sizes)} images")
        
        if len(print_sizes) < len(all_print_sizes):
            print(f"💡 Generated {len(print_sizes)} of {len(all_print_sizes)} possible sizes")
        
        print(f"📂 Files saved in: {output_folder}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    if len(sys.argv) < 2:
        print("🎨 Robust Watermark Generator - Complete Solution")
        print("\nUsage:")
        print("  python robust_generator.py image.png --interactive")
        print("  python robust_generator.py image.png --all --no-watermark")
        print("  python robust_generator.py image.png --sizes popular --center --text 'SAMPLE' --opacity 150")
        print("  python robust_generator.py image.png --sizes single --ribbon --ribbons 5 --angle 0")
        print("\nModes:")
        print("  --interactive         Full interactive mode (recommended)")
        print("\nNon-Interactive Options:")
        print("  --all                 Generate all 9 sizes")
        print("  --sizes popular       Popular sizes (5×7, 8×10, 11×14, 16×20)")
        print("  --sizes small         Small sizes (5×7, 8×10, 8.5×11)")
        print("  --sizes large         Large sizes (16×20, 18×24, 20×24, 24×36)")
        print("  --sizes single        Single size (will prompt)")
        print("\nWatermark Options:")
        print("  --no-watermark        No watermarks (clean images)")
        print("  --center              Center watermark")
        print("  --ribbon              Ribbon watermarks")
        print("  --text 'text'         Watermark text")
        print("  --opacity 50-255      Watermark opacity")
        print("  --ribbons 3-10        Number of ribbons (ribbon style)")
        print("  --angle -45 to 45     Ribbon angle (ribbon style)")
        print("\nExamples:")
        print("  Interactive mode (easiest):")
        print("    python robust_generator.py image.png --interactive")
        print("\n  Clean images, all sizes:")
        print("    python robust_generator.py image.png --all --no-watermark")
        print("\n  Popular sizes with center watermark:")
        print("    python robust_generator.py image.png --sizes popular --center --text 'MyShop.etsy.com'")
        print("\n  Single size with ribbon watermarks:")
        print("    python robust_generator.py image.png --sizes single --ribbon --ribbons 6 --angle 0")
        return
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    # Check for interactive mode
    if "--interactive" in sys.argv:
        create_images(input_file, interactive=True)
        return
    
    # Parse non-interactive options
    size_options = None
    watermark_options = {"style": "none"}
    
    # Parse size options
    if "--all" in sys.argv:
        size_options = ("all", None)
    elif "--sizes" in sys.argv:
        idx = sys.argv.index("--sizes")
        if idx + 1 < len(sys.argv):
            size_type = sys.argv[idx + 1]
            if size_type == "popular":
                size_options = ("popular", ["5x7", "8x10", "11x14", "16x20"])
            elif size_type == "small":
                size_options = ("small", ["5x7", "8x10", "8.5x11"])
            elif size_type == "large":
                size_options = ("large", ["16x20", "18x24", "20x24", "24x36"])
            elif size_type == "single":
                size_options = prompt_single_size()
    
    # Parse watermark options
    if "--no-watermark" in sys.argv:
        watermark_options = {"style": "none"}
    elif "--center" in sys.argv:
        text = "eliteblings.etsy.com"
        opacity = 150
        
        if "--text" in sys.argv:
            idx = sys.argv.index("--text")
            if idx + 1 < len(sys.argv):
                text = sys.argv[idx + 1]
        
        if "--opacity" in sys.argv:
            idx = sys.argv.index("--opacity")
            if idx + 1 < len(sys.argv):
                try:
                    opacity = int(sys.argv[idx + 1])
                    opacity = max(50, min(255, opacity))
                except ValueError:
                    opacity = 150
        
        watermark_options = {
            "style": "center",
            "text": text,
            "opacity": opacity
        }
    elif "--ribbon" in sys.argv:
        text = "eliteblings.etsy.com"
        opacity = 120
        ribbon_count = 5
        angle = 0
        
        if "--text" in sys.argv:
            idx = sys.argv.index("--text")
            if idx + 1 < len(sys.argv):
                text = sys.argv[idx + 1]
        
        if "--opacity" in sys.argv:
            idx = sys.argv.index("--opacity")
            if idx + 1 < len(sys.argv):
                try:
                    opacity = int(sys.argv[idx + 1])
                    opacity = max(50, min(255, opacity))
                except ValueError:
                    opacity = 120
        
        if "--ribbons" in sys.argv:
            idx = sys.argv.index("--ribbons")
            if idx + 1 < len(sys.argv):
                try:
                    ribbon_count = int(sys.argv[idx + 1])
                    ribbon_count = max(3, min(10, ribbon_count))
                except ValueError:
                    ribbon_count = 5
        
        if "--angle" in sys.argv:
            idx = sys.argv.index("--angle")
            if idx + 1 < len(sys.argv):
                try:
                    angle = int(sys.argv[idx + 1])
                    angle = max(-45, min(45, angle))
                except ValueError:
                    angle = 0
        
        watermark_options = {
            "style": "ribbon",
            "text": text,
            "opacity": opacity,
            "ribbon_count": ribbon_count,
            "angle": angle
        }
    
    # Use defaults if nothing specified
    if size_options is None:
        size_options = ("all", None)
    
    create_images(input_file, False, watermark_options, size_options)

if __name__ == "__main__":
    main()
  
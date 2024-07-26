import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import base64
from content_generator import ContentGenerator
from content_moderator import ContentModerator
from image_moderator import ImageModerator
from community_guidelines import CommunityGuidelines
import google.generativeai as genai
from dotenv import load_dotenv
import os
import colorsys
import webcolors
import random

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_color):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb_color[0]), int(rgb_color[1]), int(rgb_color[2]))

def generate_matching_colors(base_color):
    try:
        if base_color.startswith('#'):
            rgb = hex_to_rgb(base_color)
        else:
            rgb = webcolors.name_to_rgb(base_color)
        
        r, g, b = [x/255.0 for x in rgb]
        
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        
        comp_h = (h + 0.5) % 1
        comp_rgb = colorsys.hsv_to_rgb(comp_h, s, v)
        complementary = rgb_to_hex([int(x * 255) for x in comp_rgb])
        
        analog1_h = (h + 0.1) % 1
        analog2_h = (h - 0.1) % 1
        analog1_rgb = colorsys.hsv_to_rgb(analog1_h, s, v)
        analog2_rgb = colorsys.hsv_to_rgb(analog2_h, s, v)
        analogous1 = rgb_to_hex([int(x * 255) for x in analog1_rgb])
        analogous2 = rgb_to_hex([int(x * 255) for x in analog2_rgb])
        
        return rgb_to_hex(rgb), complementary, analogous1, analogous2
    except ValueError:
        raise ValueError(f"Invalid color input: {base_color}. Please use a valid color name or hexadecimal value.")

def create_solid_color_post(text, background_color, width=500, height=500, font_color="#FFFFFF", font=None, font_size=36):
    image = Image.new('RGB', (width, height), color=background_color)
    draw = ImageDraw.Draw(image)
    
    if font is None:
        font = ImageFont.load_default()
    
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top
    
    position = ((width-text_width)/2, (height-text_height)/2)
    draw.text(position, text, font=font, fill=font_color)
    return image

def create_gradient_post(text, color1, color2, width=500, height=500, font_color="#FFFFFF", font=None, font_size=36):
    image = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(image)
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    for y in range(height):
        r = r1 + (r2 - r1) * y / height
        g = g1 + (g2 - g1) * y / height
        b = b1 + (b2 - b1) * y / height
        draw.line([(0, y), (width, y)], fill=(int(r), int(g), int(b)))
    
    if font is None:
        font = ImageFont.load_default()
    
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top
    
    position = ((width-text_width)/2, (height-text_height)/2)
    draw.text(position, text, font=font, fill=font_color)
    return image

def apply_text_effect(draw, text, position, font, fill, effect):
    x, y = position
    if effect == "Shadow":
        shadow_color = "black"
        shadow_position = (x+2, y+2)
        draw.text(shadow_position, text, font=font, fill=shadow_color)
    elif effect == "Outline":
        outline_color = "black"
        for adj in range(-1, 2):
            for adj2 in range(-1, 2):
                draw.text((x+adj, y+adj2), text, font=font, fill=outline_color)
    draw.text(position, text, font=font, fill=fill)

def create_post(text, background_type, bg_color=None, color1=None, color2=None, bg_image=None, font_color="#FFFFFF", font=None, font_size=36, text_effect="None", text_position="center"):
    width, height = 500, 500
    if background_type == "Solid Color":
        image = Image.new('RGB', (width, height), color=bg_color)
    elif background_type == "Gradient":
        image = create_gradient_post(text, color1, color2, width, height)
    elif background_type == "Image":
        image = bg_image.copy()
        image = image.resize((width, height), Image.LANCZOS)
    
    draw = ImageDraw.Draw(image)
    
    if font is None:
        font = ImageFont.load_default()
    
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top
    
    if text_position == "center":
        position = ((width-text_width)/2, (height-text_height)/2)
    elif text_position == "left":
        position = (10, (height-text_height)/2)
    elif text_position == "right":
        position = (width-text_width-10, (height-text_height)/2)
    else:  # Custom position
        position = text_position
    
    apply_text_effect(draw, text, position, font, font_color, text_effect)
    
    return image
def chat_with_ai(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text

def main():
    # Toggle for light mode and dark mode
    dark_mode = st.checkbox("Dark Mode", False)

    # Custom CSS for light mode
    light_mode_css = """
    <style>
    .big-font {
        font-size: 36px !important;
        font-weight: bold;
        color: #0080FF; 
        text-align: center;
    }
    .stApp {
        background-color: #F0F0F0; 
        color: #333333 !important; 
    }
    body {
        color: #333333; 
    }
    p, .stMarkdown, .stText {
        color: #333333 !important; 
    }
    .stButton>button {
        background-color: #0080FF; 
        color: white;
    }
    .stSelectbox {
        background-color: #CCCCCC;
    }
    </style>
    """

    # Custom CSS for dark mode
    dark_mode_css = """
    <style>
    .big-font {
        font-size: 36px !important;
        font-weight: bold;
        color: #333333; 
        text-align: center;
    }
    .stApp {
        background-color: #1E1E1E; 
        color: #FFFFFF !important; 
    }
    body {
        color: #FFFFFF; 
    }
    p, .stMarkdown, .stText {
        color: #000000 !important; 
    }
    .stButton>button {
        background-color: #1E90FF; 
        color: white;
    }
    .stSelectbox {
        background-color: #333333; 
    }
    </style>
    """

    # Apply light mode or dark mode CSS based on the checkbox
    if dark_mode:
        st.markdown(dark_mode_css, unsafe_allow_html=True)
    else:
        st.markdown(light_mode_css, unsafe_allow_html=True)

    # Example content for the Streamlit app
    st.markdown('<p class="big-font">cookie AI</p>', unsafe_allow_html=True)
    

    st.sidebar.header("Features")
    options = [
        "Community Guidelines",
        "Generate Content",
        "Moderate Text Content",
        "Moderate Image",
        "Color Scheme Generator",
        "Generate Post",
        "Chat with AI"
    ]
    selected_option = st.sidebar.radio("Choose an option", options)

    content_generator = ContentGenerator()
    content_moderator = ContentModerator()
    image_moderator = ImageModerator()

    if selected_option == "Community Guidelines":
        st.subheader("Community Guidelines")
        st.text(CommunityGuidelines.get_guidelines())

    elif selected_option == "Generate Content":
        st.subheader("Generate Content")
        prompt = st.text_input("Enter a topic or interest for content generation")
        content_type = st.selectbox("Select content type", ("post", "comment", "response"))
        if st.button("Generate"):
            generated_content = content_generator.generate_content(prompt, content_type)
            st.text_area("Generated Content", generated_content, height=200)
            moderation_result = content_moderator.moderate_content(generated_content)
            st.text_area("Moderation Result", moderation_result, height=100)
           
            
    elif selected_option == "Moderate Text Content":
        st.subheader("Moderate Text Content")
        user_content = st.text_area("Enter the content you want to moderate", height=200)
        if st.button("Moderate"):
            moderation_result = content_moderator.moderate_content(user_content)
            st.text_area("Moderation Result", moderation_result, height=100)

    elif selected_option == "Moderate Image":
        st.subheader("Moderate Image")
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption='Uploaded Image', use_column_width=True)
                if st.button("Moderate Image"):
                    try:
                        moderation_result = image_moderator.moderate_image(image)
                        st.text_area("Moderation Result", moderation_result, height=100)
                    except Exception as e:
                        st.error(f"An error occurred during image moderation: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred while processing the image: {str(e)}")

    elif selected_option == "Color Scheme Generator":
        st.subheader("Color Scheme Generator")
        base_color = st.color_picker("Choose a base color", "#FFC0CB")
        if st.button("Generate Color Scheme"):
            try:
                base, complementary, analogous1, analogous2 = generate_matching_colors(base_color)
                st.write(f"Base Color: {base}")
                st.write(f"Complementary Color: {complementary}")
                st.write(f"Analogous Color 1: {analogous1}")
                st.write(f"Analogous Color 2: {analogous2}")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.color_picker("Base", base, key="base_display")
                with col2:
                    st.color_picker("Complementary", complementary, key="complementary_display")
                with col3:
                    st.color_picker("Analogous 1", analogous1, key="analogous1_display")
                with col4:
                    st.color_picker("Analogous 2", analogous2, key="analogous2_display")
            except ValueError as e:
                st.error(str(e))

    elif selected_option == "Generate Post":
        st.subheader("Generate Custom Post")
        post_text = st.text_input("Enter the text for your post", "Don't give up")
        background_type = st.radio("Choose background type", ("Solid Color", "Gradient", "Image"))
        
        # Font upload
        uploaded_font = st.file_uploader("Upload a custom font (TTF format)", type="ttf")
        if uploaded_font:
            font_path = "temp_font.ttf"
            with open(font_path, "wb") as f:
                f.write(uploaded_font.getbuffer())
            font = ImageFont.truetype(font_path, size=36)
        else:
            font_options = ["arial.ttf", "times.ttf", "calibri.ttf", "verdana.ttf"]
            selected_font = st.selectbox("Choose a font", font_options)
            font = ImageFont.truetype(selected_font, size=36)
        
        font_size = st.slider("Font size", 12, 72, 36)
        font_color = st.color_picker("Choose font color", "#000000")
        
        # Text effects
        text_effect = st.selectbox("Choose text effect", ("None", "Shadow", "Outline"))
        
        # Text position
        text_position = st.selectbox("Choose text position", ("center", "left", "right", "custom"))
        if text_position == "custom":
            x_pos = st.slider("X position", 0, 500, 250)
            y_pos = st.slider("Y position", 0, 500, 250)
            text_position = (x_pos, y_pos)
        
        if background_type == "Solid Color":
            bg_color = st.color_picker("Choose background color", "#FFC0CB")
        elif background_type == "Gradient":
            color1 = st.color_picker("Choose first color for gradient", "#FFC0CB")
            color2 = st.color_picker("Choose second color for gradient", "#87CEEB")
        else:  # Image background
            uploaded_file = st.file_uploader("Choose a background image...", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                bg_image = Image.open(uploaded_file)
                
                # Image editing tools
                st.subheader("Image Editing Tools")
                crop = st.checkbox("Crop image")
                if crop:
                    aspect_ratio = st.selectbox("Aspect ratio", ("1:1", "4:3", "16:9"))
                    if aspect_ratio == "1:1":
                        bg_image = bg_image.crop((0, 0, min(bg_image.size), min(bg_image.size)))
                    elif aspect_ratio == "4:3":
                        new_height = int(bg_image.width * 3 / 4)
                        bg_image = bg_image.crop((0, 0, bg_image.width, new_height))
                    elif aspect_ratio == "16:9":
                        new_height = int(bg_image.width * 9 / 16)
                        bg_image = bg_image.crop((0, 0, bg_image.width, new_height))
                
                brightness = st.slider("Brightness", 0.0, 2.0, 1.0)
                contrast = st.slider("Contrast", 0.0, 2.0, 1.0)
                bg_image = ImageEnhance.Brightness(bg_image).enhance(brightness)
                bg_image = ImageEnhance.Contrast(bg_image).enhance(contrast)
                
                filter_option = st.selectbox("Apply filter", ("None", "Blur", "Sharpen"))
                if filter_option == "Blur":
                    bg_image = bg_image.filter(ImageFilter.BLUR)
                elif filter_option == "Sharpen":
                    bg_image = bg_image.filter(ImageFilter.SHARPEN)
        
        if st.button("Generate Post"):
            if background_type == "Solid Color":
                post_image = create_post(post_text, background_type, bg_color=bg_color, font_color=font_color, font=font, font_size=font_size, text_effect=text_effect, text_position=text_position)
            elif background_type == "Gradient":
                post_image = create_post(post_text, background_type, color1=color1, color2=color2, font_color=font_color, font=font, font_size=font_size, text_effect=text_effect, text_position=text_position)
            else:
                post_image = create_post(post_text, background_type, bg_image=bg_image, font_color=font_color, font=font, font_size=font_size, text_effect=text_effect, text_position=text_position)
            
            st.image(post_image, caption="Generated Post", use_column_width=True)
            
            buf = io.BytesIO()
            post_image.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.download_button(
                label="Download Post",
                data=byte_im,
                file_name="custom_post.png",
                mime="image/png"
            )

    
    elif selected_option == "Chat with AI":
        st.subheader("Chat with AI")
        user_input = st.text_input("Ask me anything about colors, design, or content creation:")
        if st.button("Send"):
            if user_input:
                response = chat_with_ai(user_input)
                st.text_area("AI Response", response, height=200)
            else:
                st.warning("Please enter a question or prompt.")

if __name__ == "__main__":
    main()

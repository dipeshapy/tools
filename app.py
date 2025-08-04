# Create this as 'app.py' file
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import io
import zipfile
import base64
import os
from datetime import datetime

st.set_page_config(
    page_title="🖼️ Advanced Image Processor",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        color: #155724;
    }
    .stDownloadButton > button {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

class ImageProcessor:
    def __init__(self):
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🖼️ Advanced Image Processor</h1>
            <p>Professional image editing and batch processing • Free & Online</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        st.sidebar.header("🎛️ Control Panel")
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🖼️ Single Image", 
            "📁 Batch Process", 
            "🎨 Effects & Filters", 
            "🛠️ Advanced Tools"
        ])
        
        with tab1:
            self.single_image_tab()
        
        with tab2:
            self.batch_processing_tab()
        
        with tab3:
            self.effects_tab()
        
        with tab4:
            self.tools_tab()
    
    def single_image_tab(self):
        st.header("📁 Upload & Process Single Image")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            help="Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP"
        )
        
        if uploaded_file:
            # Display original image
            image = Image.open(uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📷 Original Image")
                st.image(image, caption=f"Size: {image.width} × {image.height}", use_column_width=True)
                
                # Image info
                st.markdown(f"""
                <div class="feature-box">
                    <h4>📊 Image Information</h4>
                    <p><strong>Filename:</strong> {uploaded_file.name}</p>
                    <p><strong>Dimensions:</strong> {image.width} × {image.height} pixels</p>
                    <p><strong>Format:</strong> {image.format}</p>
                    <p><strong>Mode:</strong> {image.mode}</p>
                    <p><strong>File Size:</strong> {uploaded_file.size / 1024 / 1024:.2f} MB</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.subheader("⚙️ Processing Options")
                
                # Resize options
                resize_method = st.radio("Resize Method:", ["Custom Dimensions", "Scale Percentage", "Presets"])
                
                if resize_method == "Custom Dimensions":
                    col_w, col_h = st.columns(2)
                    with col_w:
                        new_width = st.number_input("Width (px)", min_value=1, max_value=5000, value=image.width)
                    with col_h:
                        new_height = st.number_input("Height (px)", min_value=1, max_value=5000, value=image.height)
                    
                    maintain_ratio = st.checkbox("🔒 Maintain Aspect Ratio", value=True)
                    
                    if maintain_ratio:
                        ratio = min(new_width / image.width, new_height / image.height)
                        final_width = int(image.width * ratio)
                        final_height = int(image.height * ratio)
                    else:
                        final_width, final_height = new_width, new_height
                
                elif resize_method == "Scale Percentage":
                    scale = st.slider("Scale Percentage", 10, 500, 100, 5)
                    final_width = int(image.width * scale / 100)
                    final_height = int(image.height * scale / 100)
                
                else:  # Presets
                    preset_category = st.selectbox("Preset Category:", ["Standard Sizes", "Social Media"])
                    
                    if preset_category == "Standard Sizes":
                        presets = {
                            "Thumbnail": (150, 150),
                            "Small": (400, 300),
                            "Medium": (800, 600),
                            "Large": (1200, 900),
                            "HD": (1920, 1080),
                            "4K": (3840, 2160)
                        }
                    else:
                        presets = {
                            "Instagram Post": (1080, 1080),
                            "Instagram Story": (1080, 1920),
                            "Facebook Cover": (1200, 630),
                            "Twitter Header": (1200, 675),
                            "YouTube Thumbnail": (1280, 720),
                            "LinkedIn Banner": (1200, 627)
                        }
                    
                    selected_preset = st.selectbox("Choose Preset:", list(presets.keys()))
                    final_width, final_height = presets[selected_preset]
                
                # Quality and format settings
                st.subheader("🎯 Output Settings")
                col_q, col_f = st.columns(2)
                
                with col_q:
                    quality = st.slider("Quality", 10, 100, 95, help="Higher quality = larger file size")
                
                with col_f:
                    output_format = st.selectbox("Output Format", ["JPEG", "PNG", "WebP"])
                
                # Preview final size
                st.info(f"📐 Final size will be: **{final_width} × {final_height}** pixels")
                
                # Process button
                if st.button("🚀 Process Image", type="primary", use_container_width=True):
                    processed_image = self.process_image(image, final_width, final_height, quality, output_format)
                    
                    # Show processed image
                    st.subheader("✅ Processed Image")
                    st.image(processed_image, caption=f"Processed: {final_width} × {final_height}", use_column_width=True)
                    
                    # Download button
                    img_buffer = io.BytesIO()
                    processed_image.save(img_buffer, format=output_format, quality=quality, optimize=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"processed_{final_width}x{final_height}_{timestamp}.{output_format.lower()}"
                    
                    st.download_button(
                        label="📥 Download Processed Image",
                        data=img_buffer.getvalue(),
                        file_name=filename,
                        mime=f"image/{output_format.lower()}",
                        use_container_width=True
                    )
                    
                    st.success(f"✅ Image processed successfully! Final size: {final_width} × {final_height}")
    
    def batch_processing_tab(self):
        st.header("📁 Batch Image Processing")
        
        # Multiple file upload
        uploaded_files = st.file_uploader(
            "Choose multiple image files",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            accept_multiple_files=True,
            help="Select multiple images for batch processing"
        )
        
        if uploaded_files:
            st.success(f"📊 {len(uploaded_files)} images uploaded")
            
            # Show thumbnails
            cols = st.columns(min(len(uploaded_files), 5))
            for i, file in enumerate(uploaded_files):
                with cols[i % 5]:
                    img = Image.open(file)
                    st.image(img, caption=file.name[:15] + "...", width=100)
            
            # Batch settings
            st.subheader("⚙️ Batch Processing Settings")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                batch_width = st.number_input("Target Width", min_value=50, max_value=3000, value=800)
                batch_height = st.number_input("Target Height", min_value=50, max_value=3000, value=600)
            
            with col2:
                batch_quality = st.slider("Quality", 10, 100, 85)
                batch_format = st.selectbox("Output Format", ["JPEG", "PNG", "WebP"], key="batch_format")
            
            with col3:
                maintain_batch_ratio = st.checkbox("🔒 Maintain Aspect Ratio", value=True, key="batch_ratio")
                operation_type = st.selectbox("Operation", ["Resize Only", "Resize + Enhance", "Resize + Compress"])
            
            # Process batch
            if st.button("🔄 Process All Images", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Create ZIP file
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for i, file in enumerate(uploaded_files):
                        # Update progress
                        progress = (i + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {file.name}... ({i+1}/{len(uploaded_files)})")
                        
                        # Process image
                        image = Image.open(file)
                        
                        if maintain_batch_ratio:
                            ratio = min(batch_width / image.width, batch_height / image.height)
                            final_width = int(image.width * ratio)
                            final_height = int(image.height * ratio)
                        else:
                            final_width, final_height = batch_width, batch_height
                        
                        processed = self.process_image(image, final_width, final_height, batch_quality, batch_format, operation_type)
                        
                        # Save to ZIP
                        img_buffer = io.BytesIO()
                        processed.save(img_buffer, format=batch_format, quality=batch_quality, optimize=True)
                        
                        # Generate filename
                        original_name = os.path.splitext(file.name)[0]
                        new_filename = f"{original_name}_processed_{final_width}x{final_height}.{batch_format.lower()}"
                        zip_file.writestr(new_filename, img_buffer.getvalue())
                
                # Download ZIP
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                zip_filename = f"batch_processed_images_{timestamp}.zip"
                
                st.download_button(
                    label="📥 Download ZIP File (All Processed Images)",
                    data=zip_buffer.getvalue(),
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True
                )
                
                st.success(f"✅ Successfully processed {len(uploaded_files)} images!")
    
    def effects_tab(self):
        st.header("🎨 Image Effects & Filters")
        
        uploaded_file = st.file_uploader("Upload image for effects", type=['png', 'jpg', 'jpeg'], key="effects_upload")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📷 Original")
                st.image(image, use_column_width=True)
            
            with col2:
                st.subheader("🎨 Effects Controls")
                
                # Enhancement controls
                brightness = st.slider("💡 Brightness", 0.1, 3.0, 1.0, 0.1)
                contrast = st.slider("⚡ Contrast", 0.1, 3.0, 1.0, 0.1)
                saturation = st.slider("🌈 Saturation", 0.0, 3.0, 1.0, 0.1)
                sharpness = st.slider("🔪 Sharpness", 0.0, 3.0, 1.0, 0.1)
                
                # Filters
                filter_effect = st.selectbox("🎭 Filter Effects", [
                    "None", "Blur", "Detail", "Edge Enhance", "Emboss", 
                    "Find Edges", "Smooth", "Sharpen", "Black & White", "Vintage"
                ])
                
                # Transform
                rotation = st.slider("🔄 Rotation", -180, 180, 0)
                flip_horizontal = st.checkbox("↔️ Flip Horizontal")
                flip_vertical = st.checkbox("↕️ Flip Vertical")
                
                if st.button("✨ Apply Effects", type="primary"):
                    processed = self.apply_effects(
                        image, brightness, contrast, saturation, sharpness,
                        filter_effect, rotation, flip_horizontal, flip_vertical
                    )
                    
                    st.subheader("✅ With Effects")
                    st.image(processed, use_column_width=True)
                    
                    # Download
                    img_buffer = io.BytesIO()
                    processed.save(img_buffer, format="PNG", quality=95)
                    
                    st.download_button(
                        "📥 Download Effect Image",
                        img_buffer.getvalue(),
                        f"effects_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        "image/png"
                    )
    
    def tools_tab(self):
        st.header("🛠️ Advanced Tools")
        
        tool_type = st.selectbox("Choose Tool:", [
            "🏷️ Add Watermark", 
            "🖼️ Add Border", 
            "✂️ Crop Image", 
            "📊 Image Analysis"
        ])
        
        uploaded_file = st.file_uploader("Upload image for tools", type=['png', 'jpg', 'jpeg'], key="tools_upload")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            
            if tool_type == "🏷️ Add Watermark":
                self.watermark_tool(image)
            elif tool_type == "🖼️ Add Border":
                self.border_tool(image)
            elif tool_type == "✂️ Crop Image":
                self.crop_tool(image)
            elif tool_type == "📊 Image Analysis":
                self.analysis_tool(image)
    
    def process_image(self, image, width, height, quality, format, operation="Resize Only"):
        """Process single image with given parameters"""
        processed = image.resize((width, height), Image.Resampling.LANCZOS)
        
        if operation == "Resize + Enhance":
            enhancer = ImageEnhance.Sharpness(processed)
            processed = enhancer.enhance(1.2)
            enhancer = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(1.1)
        elif operation == "Resize + Compress":
            # Compression handled by quality parameter
            pass
        
        return processed
    
    def apply_effects(self, image, brightness, contrast, saturation, sharpness, filter_effect, rotation, flip_h, flip_v):
        """Apply various effects to image"""
        processed = image.copy()
        
        # Apply enhancements
        if brightness != 1.0:
            enhancer = ImageEnhance.Brightness(processed)
            processed = enhancer.enhance(brightness)
        
        if contrast != 1.0:
            enhancer = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(contrast)
        
        if saturation != 1.0:
            enhancer = ImageEnhance.Color(processed)
            processed = enhancer.enhance(saturation)
        
        if sharpness != 1.0:
            enhancer = ImageEnhance.Sharpness(processed)
            processed = enhancer.enhance(sharpness)
        
        # Apply filters
        if filter_effect == "Blur":
            processed = processed.filter(ImageFilter.BLUR)
        elif filter_effect == "Detail":
            processed = processed.filter(ImageFilter.DETAIL)
        elif filter_effect == "Edge Enhance":
            processed = processed.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_effect == "Emboss":
            processed = processed.filter(ImageFilter.EMBOSS)
        elif filter_effect == "Find Edges":
            processed = processed.filter(ImageFilter.FIND_EDGES)
        elif filter_effect == "Smooth":
            processed = processed.filter(ImageFilter.SMOOTH)
        elif filter_effect == "Sharpen":
            processed = processed.filter(ImageFilter.SHARPEN)
        elif filter_effect == "Black & White":
            processed = processed.convert('L').convert('RGB')
        elif filter_effect == "Vintage":
            # Simple vintage effect
            enhancer = ImageEnhance.Color(processed)
            processed = enhancer.enhance(0.8)
            enhancer = ImageEnhance.Contrast(processed)
            processed = enhancer.enhance(1.2)
        
        # Apply transformations
        if rotation != 0:
            processed = processed.rotate(rotation, expand=True)
        
        if flip_h:
            processed = processed.transpose(Image.FLIP_LEFT_RIGHT)
        
        if flip_v:
            processed = processed.transpose(Image.FLIP_TOP_BOTTOM)
        
        return processed
    
    def watermark_tool(self, image):
        st.subheader("🏷️ Watermark Tool")
        # Simplified watermark implementation
        st.info("Watermark feature - add your text watermark")
    
    def border_tool(self, image):
        st.subheader("🖼️ Border Tool")
        # Simplified border implementation
        st.info("Border feature - add decorative borders")
    
    def crop_tool(self, image):
        st.subheader("✂️ Crop Tool")
        # Simplified crop implementation
        st.info("Crop feature - precise image cropping")
    
    def analysis_tool(self, image):
        st.subheader("📊 Image Analysis")
        
        # Basic analysis
        st.markdown(f"""
        **Image Statistics:**
        - Dimensions: {image.width} × {image.height} pixels
        - Format: {image.format}
        - Mode: {image.mode}
        - Total Pixels: {image.width * image.height:,}
        """)

# Initialize the app
if __name__ == "__main__":
    ImageProcessor()

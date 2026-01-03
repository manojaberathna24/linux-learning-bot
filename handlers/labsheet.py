"""
Lab Sheet Handler
Upload PDF or image and get AI answers
"""
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
from modules.supabase_client import db
from modules.ai_client import ai
import base64
from io import BytesIO
import PyPDF2


async def labsheet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explain how to upload lab sheets"""
    await update.message.reply_text(
        "📄 **Lab Sheet Helper**\n\n"
        "Upload your Linux lab sheet and I'll help you answer it!\n\n"
        "**Supported formats:**\n"
        "• PDF files\n"
        "• Images (JPG, PNG)\n\n"
        "Just send me the file!",
        parse_mode="Markdown"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle PDF uploads"""
    user = update.effective_user
    
    # Get user settings
    settings = await db.get_user_settings(user.id)
    api_key = settings.get("openrouter_key")
    model = settings.get("selected_model")
    
    if not api_key:
        await update.message.reply_text(
            "❌ Please set up your API key first using /settings"
        )
        return
    
    document = update.message.document
    
    # Check if PDF
    if document.mime_type != "application/pdf":
        await update.message.reply_text(
            "❌ Please send a PDF file.\n\n"
            "For images, send them as photos (not files)."
        )
        return
    
    # Download file
    processing_msg = await update.message.reply_text("📥 Processing PDF...")
    
    try:
        file = await document.get_file()
        file_bytes = await file.download_as_bytearray()
        
        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            await processing_msg.edit_text(
                "❌ Couldn't extract text from PDF.\n"
                "Try sending it as images instead."
            )
            return
        
        # Get AI answers
        await processing_msg.edit_text("🤖 Generating answers...")
        response = await ai.answer_labsheet(api_key, model, text[:3000])  # Limit text length
        
        await processing_msg.delete()
        
        # Send answer with the limit
        if len(response) > 4000:
            # Split into multiple messages
            parts = [response[i:i+3900] for i in range(0, len(response), 3900)]
            await update.message.reply_text(f"📝 **Lab Sheet Answers** (Part 1/{len(parts)})\n\n{parts[0]}", parse_mode="Markdown")
            for i, part in enumerate(parts[1:], 2):
                await update.message.reply_text(f"(Part {i}/{len(parts)})\n\n{part}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"📝 **Lab Sheet Answers**\n\n{response}", parse_mode="Markdown")
        
        # Log activity
        await db.log_activity(user.id, "labsheet_pdf", document.file_name)
    
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error processing PDF: {str(e)}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle image uploads"""
    user = update.effective_user
    
    # Get user settings
    settings = await db.get_user_settings(user.id)
    api_key = settings.get("openrouter_key")
    model = settings.get("selected_model")
    
    if not api_key:
        await update.message.reply_text(
            "❌ Please set up your API key first using /settings"
        )
        return
    
    # Get largest photo
    photo = update.message.photo[-1]
    
    processing_msg = await update.message.reply_text("📸 Analyzing image...")
    
    try:
        # Download image
        file = await photo.get_file()
        file_bytes = await file.download_as_bytearray()
        
        # Convert to base64
        image_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # Get AI analysis
        prompt = """This is a Linux lab sheet or assignment. Please:
1. Read all the questions carefully
2. Provide detailed answers with Linux commands
3. Explain each step
4. Include expected outputs where helpful"""
        
        response = await ai.analyze_image(api_key, model, image_base64, prompt)
        
        await processing_msg.delete()
        
        # Send answer
        if len(response) > 4000:
            parts = [response[i:i+3900] for i in range(0, len(response), 3900)]
            await update.message.reply_text(f"📝 **Lab Sheet Answers** (Part 1/{len(parts)})\n\n{parts[0]}", parse_mode="Markdown")
            for i, part in enumerate(parts[1:], 2):
                await update.message.reply_text(f"(Part {i}/{len(parts)})\n\n{part}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"📝 **Lab Sheet Answers**\n\n{response}", parse_mode="Markdown")
        
        # Log activity
        await db.log_activity(user.id, "labsheet_image", "Image uploaded")
    
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error analyzing image: {str(e)}")


def setup_labsheet_handlers(application):
    """Register labsheet handlers"""
    application.add_handler(CommandHandler("labsheet", labsheet_command))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

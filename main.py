import os
import re
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Web Server for Render Health Checks ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"SEO Slug Generator Engine is Active!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()

# --- SEO Slug Generator Core Logic ---
def generate_seo_slug(text: str) -> str:
    """Converts a raw string string title into a clean, search-engine friendly URL slug."""
    # 1. Convert to lower case
    slug = text.lower().strip()
    
    # 2. Replace accented characters/symbols commonly found in copy
    # (Optional expansion if targeting multilingual text variations)
    
    # 3. Replace spaces, underscores, or slashes with dashes
    slug = re.sub(r'[\s_\/]+', '-', slug)
    
    # 4. Strip out any remaining non-alphanumeric or non-dash characters (removes !, ?, @, # etc)
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    
    # 5. Remove any accidental double dashes '---' or '--' and trim boundary edges
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    
    return slug

# --- Bot Commands and Event Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔗 **Welcome to the SEO Slug Generator Bot!**\n\n"
        "Send me any article title, product headline, or text string, and I will "
        "instantly generate a clean, lowercase, URL-safe slug optimized for search engines.\n\n"
        "👉 **Paste your text below to generate an SEO URL:**",
        parse_mode="Markdown"
    )

async def handle_slug_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Ensure user didn't just paste whitespace or symbols
    if not user_text.strip():
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Generate clean URL slug
        seo_slug = generate_seo_slug(user_text)
        
        if not seo_slug:
            await update.message.reply_text(
                "⚠️ *Could not generate a valid slug from that text.* Please include alphanumeric text parameters.",
                parse_mode="Markdown"
            )
            return

        # Format message with fixed-width typography so users can tap to copy instantly
        response_text = (
            f"✅ **Generated SEO URL Slug:**\n\n"
            f"`{seo_slug}`\n\n"
            f"💡 *Tip: Tap the code block above to copy the slug directly to your clipboard.*"
        )
        
        await update.message.reply_text(response_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Slug Generator Exception: {e}")
        await update.message.reply_text("❌ An error occurred while parsing your text format.")

async def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("Missing TELEGRAM_TOKEN environment target variable.")

    # Start the mandatory internal server framework loop for Render
    threading.Thread(target=run_health_server, daemon=True).start()

    # Build the Application framework mapping sequences
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_slug_conversion))
    
    print("SEO URL Slug engine polling sequence active...")
    
    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())

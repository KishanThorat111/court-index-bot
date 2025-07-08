# # # telegram_bot.py 
# import os
# import re
# import logging
# from datetime import datetime
# from telegram import Update
# from telegram.ext import (
#     ApplicationBuilder, CommandHandler, MessageHandler,
#     ContextTypes, filters
# )
# from dotenv import load_dotenv
# from generate_index import generate_index_pdf
# from textwrap import wrap

# # Load .env file for bot token
# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")

# # Set up logging for better error tracking
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# # Dictionary to store user session data (for multi-step input)
# user_sessions = {}
# # Required fields for generating the PDF
# REQUIRED_FIELDS = ["case_number", "court_name", "claimants", "defendants", "index_title", "hearing_date"]

# # Prompts for each field, designed to be attractive and clear
# PROMPTS = {
#     "case_number": "📌 What is the *case number* for this filing?",
#     "court_name": "🏛️ What is the *full name of the court*? Please type it exactly as you'd like it to appear (e.g., 'IN THE FAMILY COURT sitting at The Royal Courts of Justice').",
#     "claimants": "👤 Who are the *claimants* (applicants)? If there's more than one, please separate their names with commas (e.g., 'Mr. John Doe, Ms. Jane Smith').",
#     "defendants": "👥 Who are the *defendants* (respondents)? Again, use commas for multiple names (e.g., 'ABC Company Ltd, Mr. David Green').",
#     "index_title": "📝 What is the *hearing or index title*? (e.g., 'FDR HEARING', 'CASE MANAGEMENT CONFERENCE').",
#     "hearing_date": "🗓️ What is the *hearing date*? Please use a clear format like '4th July 2024'."
# }

# # Sample prompt for bulk input
# SAMPLE_PROMPT = (
#     "📋 To get started, you can paste all the details at once in this handy format:\n\n"
#     "```\n"
#     "Case Number: 1664-7423-0110-8918\n"
#     "Court Name: IN THE FAMILY COURT sitting at The Royal Courts of Justice\n"
#     "Claimants: Mr. ABCD, Ms. ABCD\n"
#     "Defendants: Ms. XYZ, Mr. XYZ\n"
#     "Index Title: FDR HEARING\n"
#     "Hearing Date: 4th July 2024\n"
#     "```\n\n"
#     "✅ For multiple claimants/defendants, just use commas (e.g., `Ms. X, Ms. Y`).\n"
#     "✅ I will automatically add numbers like (1), (2) to the names on the final PDF!"
# )

# def normalize_date(text):
#     """
#     Normalizes a date string into a consistent format (e.g., '4th July 2024').
#     Handles various ordinal indicators (st, nd, rd, th).
#     """
#     try:
#         # Remove common closing parenthesis if present and trim whitespace
#         cleaned_text = text.strip().rstrip(')')
#         # Remove ordinal suffixes (st, nd, rd, th) for parsing
#         cleaned = re.sub(r"(st|nd|rd|th)", "", cleaned_text, flags=re.IGNORECASE)
#         dt = datetime.strptime(cleaned, "%d %B %Y")
#         day = dt.day
#         # Determine correct ordinal suffix for display
#         if 11 <= day <= 13: # Special case for 11th, 12th, 13th
#             suffix = "th"
#         else:
#             suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
#         return dt.strftime(f"{day}{suffix} %B %Y")
#     except ValueError:
#         return None

# def extract_info_from_lines(lines):
#     """
#     Parses a block of text lines to extract relevant information.
#     Handles different ways users might phrase the fields.
#     """
#     info = {}
#     for line in lines:
#         if ":" not in line:
#             continue # Skip lines without a colon
#         key, val = map(str.strip, line.split(":", 1))
#         key_lower = key.lower().strip()

#         if "case number" in key_lower:
#             info["case_number"] = val or "Not Provided"
#         elif "court name" in key_lower:
#             info["court_name"] = val or "Not Provided"
#         elif "claimant" in key_lower:
#             info["claimants"] = [v.strip() for v in val.split(",")] if val else ["Not Provided"]
#         elif "defendant" in key_lower:
#             info["defendants"] = [v.strip() for v in val.split(",")] if val else ["Not Provided"]
#         elif "index title" in key_lower:
#             info["index_title"] = val or "Not Provided"
#         elif "hearing date" in key_lower:
#             parsed = normalize_date(val)
#             if parsed:
#                 info["hearing_date"] = parsed
#             else:
#                 info["invalid_date"] = val # Flag for invalid date
#     return info

# def get_missing_fields(session):
#     """Identifies which required fields are still missing from the session."""
#     return [f for f in REQUIRED_FIELDS if f not in session or session[f] in ["", [], "Not Provided"]]

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handles the /start command, greeting the user and providing the sample prompt."""
#     user_id = update.effective_user.id
#     user_sessions[user_id] = {} # Start with a clean session for the user
#     await update.message.reply_text(
#         "👋 Hello there! I'm your friendly Court Index Page Generator Bot. "
#         "I can swiftly create professional index covers for your legal documents.\n\n"
#         "Let's get started right away! " + SAMPLE_PROMPT,
#         parse_mode="Markdown"
#     )

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Processes all incoming text messages. It intelligently handles multi-line input,
#     individual field responses, and confirms data before generating the PDF.
#     """
#     user_id = update.effective_user.id
#     text = update.message.text.strip()
#     lowered_text = text.lower()
#     session = user_sessions.setdefault(user_id, {})

#     # --- Command-like Keyword Handling ---
#     if lowered_text == 'clear':
#         session.clear() # Reset the session
#         await update.message.reply_text(
#             "🔄 Alright, your session has been cleared. We can start fresh!\n\n" + SAMPLE_PROMPT,
#             parse_mode="Markdown"
#         )
#         return

#     if any(kw in lowered_text for kw in ["format", "template", "example", "help"]):
#         await update.message.reply_text(SAMPLE_PROMPT, parse_mode="Markdown")
#         return

#     # --- Confirmation Logic ---
#     if session.get("state") == "confirming":
#         if lowered_text in ["yes", "y", "correct"]:
#             try:
#                 await update.message.reply_text("📄 Excellent! Generating your professional Index PDF now... This might take a moment!")
#                 pdf_path = generate_index_pdf(
#                     session["case_number"], session["court_name"],
#                     session["claimants"], session["defendants"],
#                     session["index_title"], session["hearing_date"]
#                 )
#                 with open(pdf_path, "rb") as pdf_file:
#                     await update.message.reply_document(pdf_file, caption="✅ Your Index PDF is ready! Hope it perfectly meets your requirements.")
#                 user_sessions.pop(user_id, None)  # Clear session after successful generation
#                 await update.message.reply_text("✨ You can type /start or 'clear' anytime to generate another Index PDF. Let me know if you need anything else!")
#             except Exception as e:
#                 logger.error(f"Failed to generate or send PDF for user {user_id}. Error: {e}", exc_info=True)
#                 await update.message.reply_text(
#                     "🚨 Oh dear! It seems I encountered an issue while creating the PDF. "
#                     "Don't worry, these things happen. Please try again by typing 'clear' or /start."
#                 )
#                 user_sessions.pop(user_id, None) # Clear session to allow a fresh start after failure
#             return
#         elif lowered_text in ["no", "n", "wrong"]:
#             session.clear() # Clear session if user says no to confirmation
#             await update.message.reply_text(
#                 "🔄 No problem at all! Let's refine the details. "
#                 "Please provide them again, perhaps using the full format, or one by one if preferred:\n\n" + SAMPLE_PROMPT,
#                 parse_mode="Markdown"
#             )
#             return
#         else:
#             await update.message.reply_text(
#                 "🤔 I didn't quite catch that. Please respond with 'yes' or 'no' to confirm the details."
#             )
#             return

#     # --- Data Collection Logic ---
#     last_asked_for = session.get("last_asked_for")
    
#     # 1. If the bot previously asked a specific question (last_asked_for is set)
#     # AND the user's current message is a simple answer (no ':')
#     if last_asked_for and ":" not in text:
#         if last_asked_for == "hearing_date":
#             parsed_date = normalize_date(text)
#             if parsed_date:
#                 session[last_asked_for] = parsed_date
#             else:
#                 await update.message.reply_text(
#                     "❌ That doesn't look like a valid date format. "
#                     "Please use 'Dayth Month Year' (e.g., '4th July 2024')."
#                 )
#                 return # Stay in this state, wait for a valid date
#         elif last_asked_for in ["claimants", "defendants"]:
#             session[last_asked_for] = [v.strip() for v in text.split(",")]
#         else:
#             session[last_asked_for] = text
#         session.pop("last_asked_for", None) # Clear the flag once we have the info

#     # 2. If the user provides a block of text containing key-value pairs (colon indicates this)
#     elif ":" in text:
#         parsed_info = extract_info_from_lines(text.splitlines())
#         if "invalid_date" in parsed_info:
#             await update.message.reply_text(
#                 f"❌ I couldn't understand the hearing date: '{parsed_info['invalid_date']}'. "
#                 f"Please use a format like '4th July 2024' or type 'clear' to restart."
#             )
#             session["last_asked_for"] = "hearing_date" # Re-ask for date specifically
#             return
#         session.update(parsed_info) # Add extracted info to the session

#     # --- Determine Next Action: Ask for Missing Info or Confirm ---
#     missing_fields = get_missing_fields(session)
#     if missing_fields:
#         next_field_to_ask = missing_fields[0]
#         session["last_asked_for"] = next_field_to_ask  # Set what we are currently asking for
#         await update.message.reply_text(PROMPTS[next_field_to_ask], parse_mode="Markdown")
#     else:
#         # All fields are collected, proceed to confirmation with an glamorous preview
#         session["state"] = "confirming"
        
#         # Fixed width that seems to work well for Telegram monospace.
#         # This is often found through trial and error.
#         PREVIEW_FIXED_WIDTH = 60 # This value is crucial for alignment

#         # Calculate padding for right alignment of Case No.
#         case_no_text = f"Case No: {session['case_number']}"
#         padding_case_no = PREVIEW_FIXED_WIDTH - len(case_no_text)

#         # Calculate padding for Applicant(s) and Respondent(s)
#         # This needs to be precisely aligned to the right, similar to Case No.
#         padding_role = PREVIEW_FIXED_WIDTH - len("Applicant(s)")

#         # Calculate padding for "Vs" (center alignment)
#         padding_vs = (PREVIEW_FIXED_WIDTH - len("Vs")) // 2

#         # Calculate padding for main title (center alignment)
#         main_title_preview = f"INDEX FOR {session['index_title'].upper()} ON {session['hearing_date'].upper()}"
#         padding_main_title = (PREVIEW_FIXED_WIDTH - len(main_title_preview)) // 2

#         # Horizontal line for title block
#         preview_line_separator = "=" * PREVIEW_FIXED_WIDTH

#         # Prepare Claimant/Defendant names, centered and with bullets.
#         # We need to find the maximum length of a name line (including bullet and number)
#         # to properly center them all as a block.
#         max_name_len = 0
#         formatted_claimants = []
#         for i, name in enumerate(session['claimants']):
#             formatted_name = f"• {name.strip()} ({i+1})"
#             formatted_claimants.append(formatted_name)
#             if len(formatted_name) > max_name_len:
#                 max_name_len = len(formatted_name)

#         formatted_defendants = []
#         for i, name in enumerate(session['defendants']):
#             formatted_name = f"• {name.strip()} ({i+1})"
#             formatted_defendants.append(formatted_name)
#             if len(formatted_name) > max_name_len:
#                 max_name_len = len(formatted_name)
        
#         # Now center each formatted name based on the max_name_len and the PREVIEW_FIXED_WIDTH
#         centered_claimants = "\n".join([
#             ' ' * ((PREVIEW_FIXED_WIDTH - len(name)) // 2) + name for name in formatted_claimants
#         ])
#         centered_defendants = "\n".join([
#             ' ' * ((PREVIEW_FIXED_WIDTH - len(name)) // 2) + name for name in formatted_defendants
#         ])

#         preview = (
#             f"📋 *Excellent! Just one more step. Please carefully review the details below:*\n\n"
#             f"  *Case Number:* `{session['case_number']}`\n"
#             f"  *Court Name:* `{session['court_name']}`\n"
#             f"  *Claimants:* `{', '.join(session['claimants'])}`\n"
#             f"  *Defendants:* `{', '.join(session['defendants'])}`\n"
#             f"  *Index Title:* `{session['index_title']}`\n"
#             f"  *Hearing Date:* `{session['hearing_date']}`\n\n"
#             f"--- *Your Index Title Page will be formatted like this:* ---\n\n"
#             f"```\n" # Use a code block for fixed-width font and precise alignment
#             f"{' ' * padding_case_no}{case_no_text}\n" # Right align Case No.
#             f"\n"
#             f"{session['court_name']}\n"
#             f"\n"
#             f"BETWEEN:\n"
#             f"{centered_claimants}\n" # Centered Claimant names
#             f"{' ' * padding_role}Applicant(s)\n" # Right align Applicant(s)
#             f"\n"
#             f"{' ' * padding_vs}Vs\n" # Center align Vs
#             f"\n"
#             f"{centered_defendants}\n" # Centered Defendant names
#             f"{' ' * padding_role}Respondent(s)\n" # Right align Respondent(s)
#             f"\n"
#             f"{preview_line_separator}\n"
#             f"{' ' * padding_main_title}{main_title_preview}\n" # Center main title
#             f"{preview_line_separator}\n"
#             f"```\n\n"
#         )
#         await update.message.reply_text(f"{preview}\n*Does everything look absolutely correct and ready to go?* (Type 'yes' or 'no')", parse_mode="Markdown")

# def main():
#     """Starts the bot."""
#     app = ApplicationBuilder().token(BOT_TOKEN).build()
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#     logger.info("🤖 Court Index Bot running...")
#     app.run_polling()

# if __name__ == "__main__":
#     main()



# # # telegram_bot.py

# import os
# import re
# import logging
# from datetime import datetime
# from telegram import Update
# from telegram.ext import (
#     ApplicationBuilder, CommandHandler, MessageHandler,
#     ContextTypes, filters
# )
# from dotenv import load_dotenv
# from generate_index import generate_index_pdf
# from textwrap import wrap

# # Load .env file for bot token
# load_dotenv()
# BOT_TOKEN = os.getenv("BOT_TOKEN")

# # --- Get Render's environment variables for webhooks ---
# WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_HOSTNAME") # Render provides this as the hostname
# PORT = int(os.getenv("PORT", "8080")) # Render provides a PORT env var, default to 8080 if not found

# # Logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)

# user_sessions = {}
# REQUIRED_FIELDS = ["case_number", "court_name", "claimants", "defendants", "index_title", "hearing_date"]

# PROMPTS = {
#     "case_number": "📌 What is the *case number* for this filing?",
#     "court_name": "🏛️ What is the *full name of the court*? Please type it exactly as you'd like it to appear (e.g., 'IN THE FAMILY COURT sitting at The Royal Courts of Justice').",
#     "claimants": "👤 Who are the *claimants* (applicants)? If there's more than one, please separate their names with commas (e.g., 'Mr. John Doe, Ms. Jane Smith').",
#     "defendants": "👥 Who are the *defendants* (respondents)? Again, use commas for multiple names (e.g., 'ABC Company Ltd, Mr. David Green').",
#     "index_title": "📝 What is the *hearing or index title*? (e.g., 'FDR HEARING', 'CASE MANAGEMENT CONFERENCE').",
#     "hearing_date": "🗓️ What is the *hearing date*? Please use a clear format like '4th July 2024'."
# }

# SAMPLE_PROMPT = (
#     "📋 To get started, you can paste all the details at once in this handy format:\n\n"
#     "```\n"
#     "Case Number: 1664-7423-0110-8918\n"
#     "Court Name: IN THE FAMILY COURT sitting at The Royal Courts of Justice\n"
#     "Claimants: Mr. ABCD, Ms. ABCD\n"
#     "Defendants: Ms. XYZ, Mr. XYZ\n"
#     "Index Title: FDR HEARING\n"
#     "Hearing Date: 4th July 2024\n"
#     "```\n\n"
#     "✅ For multiple claimants/defendants, just use commas (e.g., `Ms. X, Ms. Y`).\n"
#     "✅ I will automatically add numbers like (1), (2) to the names on the final PDF!"
# )

# def normalize_date(text):
#     """
#     Normalizes a date string into a consistent format (e.g., '4th July 2024').
#     Handles various ordinal indicators (st, nd, rd, th).
#     """
#     try:
#         cleaned_text = text.strip().rstrip(')')
#         cleaned = re.sub(r"(st|nd|rd|th)", "", cleaned_text, flags=re.IGNORECASE)
#         dt = datetime.strptime(cleaned, "%d %B %Y")
#         day = dt.day
#         if 11 <= day <= 13:
#             suffix = "th"
#         else:
#             suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
#         return dt.strftime(f"{day}{suffix} %B %Y")
#     except ValueError:
#         return None

# def extract_info_from_lines(lines):
#     """
#     Parses a block of text lines to extract relevant information.
#     Handles different ways users might phrase the fields.
#     """
#     info = {}
#     for line in lines:
#         if ":" not in line:
#             continue
#         key, val = map(str.strip, line.split(":", 1))
#         key_lower = key.lower().strip()

#         if "case number" in key_lower:
#             info["case_number"] = val or "Not Provided"
#         elif "court name" in key_lower:
#             info["court_name"] = val or "Not Provided"
#         elif "claimant" in key_lower:
#             info["claimants"] = [v.strip() for v in val.split(",")] if val else ["Not Provided"]
#         elif "defendant" in key_lower:
#             info["defendants"] = [v.strip() for v in val.split(",")] if val else ["Not Provided"]
#         elif "index title" in key_lower:
#             info["index_title"] = val or "Not Provided"
#         elif "hearing date" in key_lower:
#             parsed = normalize_date(val)
#             if parsed:
#                 info["hearing_date"] = parsed
#             else:
#                 info["invalid_date"] = val
#     return info

# def get_missing_fields(session):
#     """Identifies which required fields are still missing from the session."""
#     return [f for f in REQUIRED_FIELDS if f not in session or session[f] in ["", [], "Not Provided"]]

# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Handles the /start command, greeting the user and providing the sample prompt."""
#     user_id = update.effective_user.id
#     user_sessions[user_id] = {}
#     await update.message.reply_text(
#         "👋 Hello there! I'm your friendly Court Index Page Generator Bot. "
#         "I can swiftly create professional index covers for your legal documents.\n\n"
#         "Let's get started right away! " + SAMPLE_PROMPT,
#         parse_mode="Markdown"
#     )

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Processes all incoming text messages. It intelligently handles multi-line input,
#     individual field responses, and confirms data before generating the PDF.
#     """
#     user_id = update.effective_user.id
#     text = update.message.text.strip()
#     lowered_text = text.lower()
#     session = user_sessions.setdefault(user_id, {})

#     # --- Command-like Keyword Handling ---
#     if lowered_text == 'clear':
#         session.clear()
#         await update.message.reply_text(
#             "🔄 Alright, your session has been cleared. We can start fresh!\n\n" + SAMPLE_PROMPT,
#             parse_mode="Markdown"
#         )
#         return

#     if any(kw in lowered_text for kw in ["format", "template", "example", "help"]):
#         await update.message.reply_text(SAMPLE_PROMPT, parse_mode="Markdown")
#         return

#     # --- Confirmation Logic ---
#     if session.get("state") == "confirming":
#         if lowered_text in ["yes", "y", "correct"]:
#             try:
#                 await update.message.reply_text("📄 Excellent! Generating your professional Index PDF now... This might take a moment!")
#                 pdf_path = generate_index_pdf(
#                     session["case_number"], session["court_name"],
#                     session["claimants"], session["defendants"],
#                     session["index_title"], session["hearing_date"]
#                 )
#                 with open(pdf_path, "rb") as pdf_file:
#                     await update.message.reply_document(pdf_file, caption="✅ Your Index PDF is ready! Hope it perfectly meets your requirements.")
#                 user_sessions.pop(user_id, None)
#                 await update.message.reply_text("✨ You can type /start or 'clear' anytime to generate another Index PDF. Let me know if you need anything else!")
#             except Exception as e:
#                 logger.error(f"Failed to generate or send PDF for user {user_id}. Error: {e}", exc_info=True)
#                 await update.message.reply_text(
#                     "🚨 Oh dear! It seems I encountered an issue while creating the PDF. "
#                     "Don't worry, these things happen. Please try again by typing 'clear' or /start."
#                 )
#                 user_sessions.pop(user_id, None)
#             return
#         elif lowered_text in ["no", "n", "wrong"]:
#             session.clear()
#             await update.message.reply_text(
#                 "🔄 No problem at all! Let's refine the details. "
#                 "Please provide them again, perhaps using the full format, or one by one if preferred:\n\n" + SAMPLE_PROMPT,
#                 parse_mode="Markdown"
#             )
#             return
#         else:
#             await update.message.reply_text(
#                 "🤔 I didn't quite catch that. Please respond with 'yes' or 'no' to confirm the details."
#             )
#             return

#     # --- Data Collection Logic ---
#     last_asked_for = session.get("last_asked_for")
    
#     if last_asked_for and ":" not in text:
#         if last_asked_for == "hearing_date":
#             parsed_date = normalize_date(text)
#             if parsed_date:
#                 session[last_asked_for] = parsed_date
#             else:
#                 await update.message.reply_text(
#                     "❌ That doesn't look like a valid date format. "
#                     "Please use 'Dayth Month Year' (e.g., '4th July 2024')."
#                 )
#                 return
#         elif last_asked_for in ["claimants", "defendants"]:
#             session[last_asked_for] = [v.strip() for v in text.split(",")]
#         else:
#             session[last_asked_for] = text
#         session.pop("last_asked_for", None)

#     elif ":" in text:
#         parsed_info = extract_info_from_lines(text.splitlines())
#         if "invalid_date" in parsed_info:
#             await update.message.reply_text(
#                 f"❌ I couldn't understand the hearing date: '{parsed_info['invalid_date']}'. "
#                 f"Please use a format like '4th July 2024' or type 'clear' to restart."
#             )
#             session["last_asked_for"] = "hearing_date"
#             return
#         session.update(parsed_info)

#     # --- Determine Next Action: Ask for Missing Info or Confirm ---
#     missing_fields = get_missing_fields(session)
#     if missing_fields:
#         next_field_to_ask = missing_fields[0]
#         session["last_asked_for"] = next_field_to_ask
#         await update.message.reply_text(PROMPTS[next_field_to_ask], parse_mode="Markdown")
#     else:
#         session["state"] = "confirming"
        
#         PREVIEW_FIXED_WIDTH = 60

#         case_no_text = f"Case No: {session['case_number']}"
#         padding_case_no = PREVIEW_FIXED_WIDTH - len(case_no_text)

#         padding_role = PREVIEW_FIXED_WIDTH - len("Applicant(s)")

#         padding_vs = (PREVIEW_FIXED_WIDTH - len("Vs")) // 2

#         main_title_preview = f"INDEX FOR {session['index_title'].upper()} ON {session['hearing_date'].upper()}"
#         padding_main_title = (PREVIEW_FIXED_WIDTH - len(main_title_preview)) // 2

#         preview_line_separator = "=" * PREVIEW_FIXED_WIDTH

#         max_name_len = 0
#         formatted_claimants = []
#         for i, name in enumerate(session['claimants']):
#             formatted_name = f"• {name.strip()} ({i+1})"
#             formatted_claimants.append(formatted_name)
#             if len(formatted_name) > max_name_len:
#                 max_name_len = len(formatted_name)

#         formatted_defendants = []
#         for i, name in enumerate(session['defendants']):
#             formatted_name = f"• {name.strip()} ({i+1})"
#             formatted_defendants.append(formatted_name)
#             if len(formatted_name) > max_name_len:
#                 max_name_len = len(formatted_name)
        
#         centered_claimants = "\n".join([
#             ' ' * ((PREVIEW_FIXED_WIDTH - len(name)) // 2) + name for name in formatted_claimants
#         ])
#         centered_defendants = "\n".join([
#             ' ' * ((PREVIEW_FIXED_WIDTH - len(name)) // 2) + name for name in formatted_defendants
#         ])

#         preview = (
#             f"📋 *Excellent! Just one more step. Please carefully review the details below:*\n\n"
#             f"  *Case Number:* `{session['case_number']}`\n"
#             f"  *Court Name:* `{session['court_name']}`\n"
#             f"  *Claimants:* `{', '.join(session['claimants'])}`\n"
#             f"  *Defendants:* `{', '.join(session['defendants'])}`\n"
#             f"  *Index Title:* `{session['index_title']}`\n"
#             f"  *Hearing Date:* `{session['hearing_date']}`\n\n"
#             f"--- *Your Index Title Page will be formatted like this:* ---\n\n"
#             f"```\n"
#             f"{' ' * padding_case_no}{case_no_text}\n"
#             f"\n"
#             f"{session['court_name']}\n"
#             f"\n"
#             f"BETWEEN:\n"
#             f"{centered_claimants}\n"
#             f"{' ' * padding_role}Applicant(s)\n"
#             f"\n"
#             f"{' ' * padding_vs}Vs\n"
#             f"\n"
#             f"{centered_defendants}\n"
#             f"{' ' * padding_role}Respondent(s)\n"
#             f"\n"
#             f"{preview_line_separator}\n"
#             f"{' ' * padding_main_title}{main_title_preview}\n"
#             f"{preview_line_separator}\n"
#             f"```\n\n"
#         )
#         await update.message.reply_text(f"{preview}\n*Does everything look absolutely correct and ready to go?* (Type 'yes' or 'no')", parse_mode="Markdown")

# def main():
#     """Starts the bot."""
#     # --- MODIFIED FOR WEBHOOKS ---
#     # The ApplicationBuilder is now configured for webhooks.
#     # It will listen on the specified PORT and expose a URL path.
#     # The URL for Telegram will be constructed using RENDER_EXTERNAL_HOSTNAME.

#     # Ensure WEBHOOK_URL is available for the bot to set itself up with Telegram
#     if not WEBHOOK_URL:
#         logger.error("RENDER_EXTERNAL_HOSTNAME environment variable is not set. Cannot run in webhook mode.")
#         logger.info("Falling back to polling mode for local development. This is not recommended for Render deployment.")
#         app = ApplicationBuilder().token(BOT_TOKEN).build()
#         app.add_handler(CommandHandler("start", start))
#         app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#         logger.info("🤖 Court Index Bot running in polling mode...")
#         app.run_polling()
#         return

#     # Build the Application object first
#     app = ApplicationBuilder().token(BOT_TOKEN).build()

#     # Set the webhook URL after building the application
#     # The webhook_url should be the full URL including the path
#     full_webhook_url = f"https://{WEBHOOK_URL}/telegram"

#     # Add handlers
#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     # Start the webhook server
#     logger.info(f"🤖 Court Index Bot running in webhook mode on port {PORT} at path /telegram...")
#     # The run_webhook method takes the URL, listen address, and port
#     app.run_webhook(
#         listen="0.0.0.0",
#         port=PORT,
#         url_path="telegram",
#         webhook_url=full_webhook_url # Pass the full URL here
#     )

# if __name__ == "__main__":
#     main()













# # # telegram_bot.py

import os
import re
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv
from generate_index import generate_index_pdf
from textwrap import wrap

# Load .env file for bot token
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Get Render's environment variables for webhooks ---
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_HOSTNAME") # Render provides this as the hostname
PORT = int(os.getenv("PORT", "8080")) # Render provides a PORT env var, default to 8080 if not found

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

user_sessions = {}
REQUIRED_FIELDS = ["case_number", "court_name", "claimants", "defendants", "index_title", "hearing_date"]

PROMPTS = {
    "case_number": "📌 What is the *case number* for this filing?",
    "court_name": "🏛️ What is the *full name of the court*? Please type it exactly as you'd like it to appear (e.g., 'IN THE FAMILY COURT sitting at The Royal Courts of Justice').",
    "claimants": "👤 Who are the *claimants* (applicants)? If there's more than one, please separate their names with commas (e.g., 'Mr. John Doe, Ms. Jane Smith').",
    "defendants": "👥 Who are the *defendants* (respondents)? Again, use commas for multiple names (e.g., 'ABC Company Ltd, Mr. David Green').",
    "index_title": "📝 What is the *hearing or index title*? (e.g., 'FDR HEARING', 'CASE MANAGEMENT CONFERENCE').",
    "hearing_date": "🗓️ What is the *hearing date*? Please use a clear format like '4th July 2024'."
}

SAMPLE_PROMPT = (
    "📋 To get started, you can paste all the details at once in this handy format:\n\n"
    "```\n"
    "Case Number: 1664-7423-0110-8918\n"
    "Court Name: IN THE FAMILY COURT sitting at The Royal Courts of Justice\n"
    "Claimants: Mr. ABCD, Ms. ABCD\n"
    "Defendants: Ms. XYZ, Mr. XYZ\n"
    "Index Title: FDR HEARING\n"
    "Hearing Date: 4th July 2024\n"
    "```\n\n"
    "✅ For multiple claimants/defendants, just use commas (e.g., `Ms. X, Ms. Y`).\n"
    "✅ I will automatically add numbers like (1), (2) to the names on the final PDF!"
)

def normalize_date(text):
    """
    Normalizes a date string into a consistent format (e.g., '4th July 2024').
    Handles various ordinal indicators (st, nd, rd, th) and month abbreviations,
    and different common date formats.
    """
    # Initial cleaning: strip whitespace, remove trailing ')' (if any), and common punctuation
    original_text = text.strip().rstrip(')').replace('.', '').replace(',', '').strip()
    
    # Remove ordinal indicators (st, nd, rd, th) more robustly
    # This regex looks for the ordinal at the end of a digit sequence and ensures it's followed by a word boundary
    cleaned_ordinal = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", original_text, flags=re.IGNORECASE).strip()

    # Define a comprehensive list of common date formats to try
    # Order matters: try more specific/common formats first
    date_formats = [
        # Formats with full month names
        "%d %B %Y",  # "5 August 2025"
        "%d-%B-%Y",  # "05-August-2025"
        "%d/%B/%Y",  # "05/August/2025"
        "%B %d, %Y", # "August 5, 2025"
        
        # Formats with abbreviated month names
        "%d %b %Y",  # "5 Aug 2025"
        "%d-%b-%Y",  # "05-Aug-2025"
        "%d/%b/%Y",  # "05/Aug/2025"
        "%b %d, %Y", # "Aug 5, 2025"

        # Numeric formats
        "%d-%m-%Y",  # "05-08-2025"
        "%d/%m/%Y",  # "05/08/2025"
        "%m-%d-%Y",  # "08-05-2025" (US format)
        "%m/%d/%Y",  # "08/05/2025" (US format)
        "%Y-%m-%d",  # "2025-08-05"
        "%Y/%m/%d",  # "2025/08/05"
    ]

    dt = None
    # Try parsing the cleaned string (without ordinals) first
    for fmt in date_formats:
        try:
            dt = datetime.strptime(cleaned_ordinal, fmt)
            break # Found a valid format, break the loop
        except ValueError:
            continue # Try next format

    # If still not parsed, try parsing the original text (in case ordinal removal was too aggressive for some edge case)
    # This handles cases where the ordinal might be part of a non-standard but recognizable pattern
    if dt is None:
        for fmt in date_formats:
            try:
                dt = datetime.strptime(original_text, fmt)
                break
            except ValueError:
                continue

    if dt is None:
        return None # No valid format found after trying all patterns

    # Calculate ordinal suffix for the output format
    day = dt.day
    if 11 <= day <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    
    # Always return with full month name for consistency in output
    return dt.strftime(f"{day}{suffix} %B %Y")


def extract_info_from_lines(lines):
    """
    Parses a block of text lines to extract relevant information.
    Handles different ways users might phrase the fields.
    """
    info = {}
    for line in lines:
        if ":" not in line:
            continue
        key, val = map(str.strip, line.split(":", 1))
        key_lower = key.lower().strip()

        if "case number" in key_lower:
            info["case_number"] = val or "Not Provided"
        elif "court name" in key_lower:
            info["court_name"] = val or "Not Provided"
        elif "claimant" in key_lower:
            info["claimants"] = [v.strip() for v in val.split(",")] if val else ["Not Provided"]
        elif "defendant" in key_lower:
            info["defendants"] = [v.strip() for v in val.split(",")] if val else ["Not Provided"]
        elif "index title" in key_lower:
            info["index_title"] = val or "Not Provided"
        elif "hearing date" in key_lower:
            parsed = normalize_date(val)
            if parsed:
                info["hearing_date"] = parsed
            else:
                info["invalid_date"] = val
    return info

def get_missing_fields(session):
    """Identifies which required fields are still missing from the session."""
    return [f for f in REQUIRED_FIELDS if f not in session or session[f] in ["", [], "Not Provided"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command, greeting the user and providing the sample prompt."""
    user_id = update.effective_user.id
    user_sessions[user_id] = {}
    await update.message.reply_text(
        "👋 Hello there! I'm your friendly Court Index Page Generator Bot. "
        "I can swiftly create professional index covers for your legal documents.\n\n"
        "Let's get started right away! " + SAMPLE_PROMPT,
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes all incoming text messages. It intelligently handles multi-line input,
    individual field responses, and confirms data before generating the PDF.
    """
    user_id = update.effective_user.id
    text = update.message.text.strip()
    lowered_text = text.lower()
    session = user_sessions.setdefault(user_id, {})

    # --- Command-like Keyword Handling ---
    if lowered_text == 'clear':
        session.clear()
        await update.message.reply_text(
            "🔄 Alright, your session has been cleared. We can start fresh!\n\n" + SAMPLE_PROMPT,
            parse_mode="Markdown"
        )
        return

    if any(kw in lowered_text for kw in ["format", "template", "example", "help"]):
        await update.message.reply_text(SAMPLE_PROMPT, parse_mode="Markdown")
        return

    # --- Confirmation Logic ---
    if session.get("state") == "confirming":
        if lowered_text in ["yes", "y", "correct"]:
            try:
                await update.message.reply_text("📄 Excellent! Generating your professional Index PDF now... This might take a moment!")
                pdf_path = generate_index_pdf(
                    session["case_number"], session["court_name"],
                    session["claimants"], session["defendants"],
                    session["index_title"], session["hearing_date"]
                )
                with open(pdf_path, "rb") as pdf_file:
                    await update.message.reply_document(pdf_file, caption="✅ Your Index PDF is ready! Hope it perfectly meets your requirements.")
                user_sessions.pop(user_id, None)
                await update.message.reply_text("✨ You can type /start or 'clear' anytime to generate another Index PDF. Let me know if you need anything else!")
            except Exception as e:
                logger.error(f"Failed to generate or send PDF for user {user_id}. Error: {e}", exc_info=True)
                await update.message.reply_text(
                    "🚨 Oh dear! It seems I encountered an issue while creating the PDF. "
                    "Don't worry, these things happen. Please try again by typing 'clear' or /start."
                )
                user_sessions.pop(user_id, None)
            return
        elif lowered_text in ["no", "n", "wrong"]:
            session.clear()
            await update.message.reply_text(
                "🔄 No problem at all! Let's refine the details. "
                "Please provide them again, perhaps using the full format, or one by one if preferred:\n\n" + SAMPLE_PROMPT,
                parse_mode="Markdown"
            )
            return
        else:
            await update.message.reply_text(
                "🤔 I didn't quite catch that. Please respond with 'yes' or 'no' to confirm the details."
            )
            return

    # --- Data Collection Logic ---
    last_asked_for = session.get("last_asked_for")
    
    if last_asked_for and ":" not in text:
        if last_asked_for == "hearing_date":
            parsed_date = normalize_date(text)
            if parsed_date:
                session[last_asked_for] = parsed_date
            else:
                await update.message.reply_text(
                    "❌ That doesn't look like a valid date format. "
                    "Please use 'Dayth Month Year' (e.g., '4th July 2024')."
                )
                return
        elif last_asked_for in ["claimants", "defendants"]:
            session[last_asked_for] = [v.strip() for v in text.split(",")]
        else:
            session[last_asked_for] = text
        session.pop("last_asked_for", None)

    elif ":" in text:
        parsed_info = extract_info_from_lines(text.splitlines())
        if "invalid_date" in parsed_info:
            await update.message.reply_text(
                f"❌ I couldn't understand the hearing date: '{parsed_info['invalid_date']}'. "
                f"Please use a format like '4th July 2024' or type 'clear' to restart."
            )
            session["last_asked_for"] = "hearing_date"
            return
        session.update(parsed_info)

    # --- Determine Next Action: Ask for Missing Info or Confirm ---
    missing_fields = get_missing_fields(session)
    if missing_fields:
        next_field_to_ask = missing_fields[0]
        session["last_asked_for"] = next_field_to_ask
        await update.message.reply_text(PROMPTS[next_field_to_ask], parse_mode="Markdown")
    else:
        session["state"] = "confirming"
        
        PREVIEW_FIXED_WIDTH = 60

        case_no_text = f"Case No: {session['case_number']}"
        padding_case_no = PREVIEW_FIXED_WIDTH - len(case_no_text)

        padding_role = PREVIEW_FIXED_WIDTH - len("Applicant(s)")

        padding_vs = (PREVIEW_FIXED_WIDTH - len("Vs")) // 2

        main_title_preview = f"INDEX FOR {session['index_title'].upper()} ON {session['hearing_date'].upper()}"
        padding_main_title = (PREVIEW_FIXED_WIDTH - len(main_title_preview)) // 2

        preview_line_separator = "=" * PREVIEW_FIXED_WIDTH

        max_name_len = 0
        formatted_claimants = []
        for i, name in enumerate(session['claimants']):
            formatted_name = f"• {name.strip()} ({i+1})"
            formatted_claimants.append(formatted_name)
            if len(formatted_name) > max_name_len:
                max_name_len = len(formatted_name)

        formatted_defendants = []
        for i, name in enumerate(session['defendants']):
            formatted_name = f"• {name.strip()} ({i+1})"
            formatted_defendants.append(formatted_name)
            if len(formatted_name) > max_name_len:
                max_name_len = len(formatted_name)
        
        centered_claimants = "\n".join([
            ' ' * ((PREVIEW_FIXED_WIDTH - len(name)) // 2) + name for name in formatted_claimants
        ])
        centered_defendants = "\n".join([
            ' ' * ((PREVIEW_FIXED_WIDTH - len(name)) // 2) + name for name in formatted_defendants
        ])

        preview = (
            f"📋 *Excellent! Just one more step. Please carefully review the details below:*\n\n"
            f"  *Case Number:* `{session['case_number']}`\n"
            f"  *Court Name:* `{session['court_name']}`\n"
            f"  *Claimants:* `{', '.join(session['claimants'])}`\n"
            f"  *Defendants:* `{', '.join(session['defendants'])}`\n"
            f"  *Index Title:* `{session['index_title']}`\n"
            f"  *Hearing Date:* `{session['hearing_date']}`\n\n"
            f"--- *Your Index Title Page will be formatted like this:* ---\n\n"
            f"```\n"
            f"{' ' * padding_case_no}{case_no_text}\n"
            f"\n"
            f"{session['court_name']}\n"
            f"\n"
            f"BETWEEN:\n"
            f"{centered_claimants}\n"
            f"{' ' * padding_role}Applicant(s)\n"
            f"\n"
            f"{' ' * padding_vs}Vs\n"
            f"\n"
            f"{centered_defendants}\n"
            f"{' ' * padding_role}Respondent(s)\n"
            f"\n"
            f"{preview_line_separator}\n"
            f"{' ' * padding_main_title}{main_title_preview}\n"
            f"{preview_line_separator}\n"
            f"```\n\n"
        )
        await update.message.reply_text(f"{preview}\n*Does everything look absolutely correct and ready to go?* (Type 'yes' or 'no')", parse_mode="Markdown")

def main():
    """Starts the bot."""
    # --- MODIFIED FOR WEBHOOKS ---
    # The ApplicationBuilder is now configured for webhooks.
    # It will listen on the specified PORT and expose a URL path.
    # The URL for Telegram will be constructed using RENDER_EXTERNAL_HOSTNAME.

    # Ensure WEBHOOK_URL is available for the bot to set itself up with Telegram
    if not WEBHOOK_URL:
        logger.error("RENDER_EXTERNAL_HOSTNAME environment variable is not set. Cannot run in webhook mode.")
        logger.info("Falling back to polling mode for local development. This is not recommended for Render deployment.")
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        logger.info("🤖 Court Index Bot running in polling mode...")
        app.run_polling()
        return

    # Build the Application object first
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Set the webhook URL after building the application
    # The webhook_url should be the full URL including the path
    full_webhook_url = f"https://{WEBHOOK_URL}/telegram"

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the webhook server
    logger.info(f"🤖 Court Index Bot running in webhook mode on port {PORT} at path /telegram...")
    # The run_webhook method takes the URL, listen address, and port
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="telegram",
        webhook_url=full_webhook_url # Pass the full URL here
    )

if __name__ == "__main__":
    main()

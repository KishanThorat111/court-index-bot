🏛️ Court Index Pro - Your Automated Legal Index Generator 🚀Effortlessly create professional Court Index Title Pages with a simple Telegram bot!✨ OverviewWelcome to Court Index Pro! This powerful Python-based Telegram bot is designed to revolutionize how legal professionals generate their court index title pages. Say goodbye to tedious manual formatting and hello to instant, perfectly structured PDFs. 📄✨Whether you're dealing with complex multi-party cases or need quick, accurate documentation, this bot streamlines the entire process, ensuring your legal filings always look impeccable.🌟 Key FeaturesAutomated PDF Generation: Instantly creates a polished PDF index title page.Intelligent Input Handling: Accepts details one-by-one or as a complete block of text. 🧠Smart Date Parsing: Understands various date formats and normalizes them. 🗓️Dynamic Party Numbering: Automatically adds (1), (2) etc., to claimant and defendant names.Real-time Preview: Shows you exactly how your index page will look before generating the PDF! 👀User-Friendly Interface: Interact seamlessly via Telegram. 💬Secure Token Management: Keeps your bot's secret token safe. 🔒🛠️ How It WorksThe Court Index Pro bot leverages the python-telegram-bot library to communicate with users. It collects essential case details, processes them using reportlab to generate a meticulously formatted PDF, and then sends the document directly back to the user. python-dotenv ensures secure handling of sensitive API keys.🚀 Getting Started (Local Setup for Development)Want to run this bot on your own machine or contribute to its development? Follow these steps!1. 🎣 Clone the RepositoryFirst, get a copy of the code onto your computer.git clone https://github.com/KishanThorat111/court-index-bot.git
cd court-index-bot
2. 🐍 Set Up Your Python EnvironmentIt's highly recommended to use a virtual environment to manage dependencies.python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
3. 📦 Install DependenciesAll required libraries are listed in requirements.txt.pip install -r requirements.txt
4. 🤖 Get Your Telegram Bot TokenYou need to create your own Telegram bot via @BotFather to get a unique API token.Open Telegram and search for @BotFather.Send /newbot and follow the prompts to choose a name and username.@BotFather will give you an HTTP API Token. Copy this token! 🔑5. 🔑 Configure Environment VariablesCreate a .env file in the root of your project directory (where telegram_bot.py is located) and add your bot token.Create a file named .envAdd the following line, replacing YOUR_TELEGRAM_BOT_TOKEN_HERE with your actual token:BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
Remember to keep this file out of version control (it's in .gitignore!) for security. 🛡️6. ▶️ Run the Bot!With everything set up, you can now start your bot locally.python telegram_bot.py
You should see 🤖 Court Index Bot running... in your terminal. Keep this window open for the bot to remain active!🌐 Deployment (Running 24/7 in the Cloud)To keep your bot running continuously without needing your local machine, you can deploy it to a cloud hosting platform like Render.com, Heroku, or a Virtual Private Server (VPS).Key Deployment Files:Procfile: This file tells the hosting service how to start your bot.web: python telegram_bot.py
Ensure this file is in the root of your repository.requirements.txt: Specifies all Python dependencies for the server to install.Environment Variables: Instead of a .env file, you'll configure BOT_TOKEN as an environment variable directly on your chosen hosting platform (e.g., in Render's dashboard under "Environment Variables"). This is the secure way to handle secrets in production.General Deployment Steps:Push to GitHub: Ensure all your code (except .env) is pushed to your GitHub repository.Choose a Platform: Select a hosting service (e.g., Render).Connect Repository: Link your GitHub repository to the hosting service.Configure Build/Start Commands: Set the Build Command to pip install -r requirements.txt and the Start Command to python telegram_bot.py.Add BOT_TOKEN: Set BOT_TOKEN as a secure environment variable on the platform.Deploy! Initiate the deployment process and monitor the build logs.💬 How to Use the Bot (in Telegram)Once your bot is running (either locally or deployed), interact with it on Telegram!Find Your Bot: Search for your bot's username (e.g., @YourCourtIndexBot).Start a Chat: Send the /start command.Provide Details: The bot will guide you through providing the necessary information. You can either:Respond to prompts one-by-one: The bot will ask for each detail individually.Paste a block of text: Use the suggested format for quick input:Case Number: 1664-7423-0110-8918
Court Name: IN THE FAMILY COURT sitting at The Royal Courts of Justice
Claimants: Mr. ABCD, Ms. ABCD
Defendants: Ms. XYZ, Mr. XYZ
Index Title: FDR HEARING
Hearing Date: 4th July 2024
Review the Preview: The bot will present a beautiful, formatted preview of your index page:                                    Case No: 1664-7423-0110-8918

IN THE FAMILY COURT sitting at The Royal Courts of Justice

BETWEEN:
                            • Mr. Prem Pal Sharma (1)
                            • Ms. Sarah Jane (2)
                                                            Applicant(s)

                                    Vs

                            • Ms. Charan Bala Sharma (1)
                            • Mr. Robert Smith (2)
                                                            Respondent(s)

============================================================
        INDEX FOR FDR HEARING ON 4TH JULY 2024
============================================================
Confirm & Receive PDF: If the preview looks good, confirm, and your professional PDF will be delivered! ✅📁 Project Structure.
├── data/
│   └── processed/
│       └── Index.pdf  # Generated PDF output (ignored by Git)
├── generate_index.py  # Core logic for PDF generation using ReportLab
├── telegram_bot.py    # Main Telegram bot logic and user interaction
├── requirements.txt   # Python dependencies
├── Procfile           # For cloud deployment (e.g., Render, Heroku)
└── .gitignore         # Specifies files/folders to ignore in Git
└── .env               # Your bot token (ignored by Git for security)
└── README.md          # This file!
🤝 ContributingWe welcome contributions! If you have ideas for improvements, bug fixes, or new features, feel free to:Fork the repository.Create a new branch (git checkout -b feature/your-feature-name).Make your changes.Commit your changes (git commit -m 'feat: Add new feature X').Push to your branch (git push origin feature/your-feature-name).Open a Pull Request.📜 LicenseThis project is open-source and available under the MIT License.❓ Support & QuestionsIf you have any questions, encounter issues, or just want to say hello, feel free to open an issue on this GitHub repository! We're here to help you make your legal document preparation seamless. 📧Happy Indexing! 🥳
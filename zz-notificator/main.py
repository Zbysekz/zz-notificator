import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from parameters import Parameters
from databaseMySQL import cMySQL
from logger import Logger

logger = Logger("main")
while True:
    try:
        mysql = cMySQL()
        queue = mysql.getQueue()
        if queue and len(queue) > 0:
            # Create SMTP session
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Secure the connection
                server.login(Parameters.SENDER_MAIL, Parameters.APP_PASSWORD)

                results = []
                for notification in queue:
                    try:
                        # Create the email message
                        message = MIMEMultipart()
                        message["From"] = Parameters.SENDER_MAIL
                        message["To"] = notification["receiver"]
                        message["Subject"] = notification["subject"]
                        body = notification["message"]
                        message.attach(MIMEText(body, "plain"))

                        text = message.as_string()
                        server.sendmail(Parameters.SENDER_MAIL, notification["receiver"], text)
                        results.append({"result": "ok", "id": notification["id"]})
                    except Exception as e:
                        results.append([{"result":"error", "error_type": type(e), "error_message":repr(e),"id": notification["id"]}])
                mysql.reportSentResult(results)

            logger.log(f"Sent {len(queue)} notification emails.")
    except Exception as e:
        logger.log(f"Exception in main thread: {repr(e)}")
    time.sleep(30)
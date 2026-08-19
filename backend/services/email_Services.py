import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🚨 SENDER DETAILS: Yahan apni details daliye
SENDER_EMAIL = "ypriyanshi94@gmail.com"  
SENDER_PASSWORD = "slbu jrlg arwp hxuv"  # 👈 Google se mila hua 16-digit code (bina spaces ke)

def send_interview_email(candidate_email, candidate_name, interview_link):
    try:
        # Email Content Configuration
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = candidate_email
        message["Subject"] = f"🎯 Congratulations {candidate_name}! You've been Shortlisted"

        # Professional HTML Email Design
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">Hello {candidate_name},</h2>
                    <p>Great news! Your resume matches our technical requirements perfectly.</p>
                    <p>Your personalized dynamic live interview room is ready:</p>
                    <div style="margin: 20px 0;">
                        <a href="{interview_link}" target="_blank" style="background-color: #10B981; color: white; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 5px; display: inline-block;">
                            🎙️ Start Your Live Interview
                        </a>
                    </div>
                    <p style="font-size: 12px; color: #64748B;">Please ensure you are in a quiet environment before starting.</p>
                </div>
            </body>
        </html>
        """
        message.attach(MIMEText(html_body, "html"))

        # Connection with Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Security Encryption
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, candidate_email, message.as_string())
            
        print(f"[EMAIL] Email successfully sent to {candidate_email}!")
        return True
    except Exception as e:
        print(f"[ERROR] Email delivery failed: {e}")
        return False
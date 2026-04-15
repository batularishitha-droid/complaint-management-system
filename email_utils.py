"""
Enhanced Email Notification System for VoiceHer
Supports HTML emails with beautiful formatting and proper error handling
"""

import os
import smtplib
import ssl
import threading
import time
from email.message import EmailMessage
from datetime import datetime

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER") or "your_email@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") or ""
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def send_email_sync(receiver, subject, html_body):
    """
    Send email synchronously with retry logic and proper error handling
    Returns: (success: bool, message: str)
    """
    if not EMAIL_PASSWORD or EMAIL_SENDER == "your_email@gmail.com":
        return False, "⚠️ Email not configured. Please set EMAIL_SENDER and EMAIL_PASSWORD environment variables."
    
    if not receiver or not isinstance(receiver, str) or "@" not in receiver:
        return False, "❌ Invalid recipient email address."
    
    for attempt in range(MAX_RETRIES):
        try:
            # Create email message with HTML support
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = EMAIL_SENDER
            msg["To"] = receiver
            msg.set_content(html_body, subtype="html")
            
            # Create SSL context for secure connection
            context = ssl.create_default_context()
            
            # Connect to Gmail SMTP server
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                server.starttls(context=context)
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            
            return True, "✅ Email sent successfully"
        
        except smtplib.SMTPAuthenticationError:
            return False, "❌ Email authentication failed. Check your email/password or use an app password for Gmail."
        except smtplib.SMTPException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return False, f"❌ SMTP Error: {str(e)}"
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return False, f"❌ Error: {str(e)}"
    
    return False, "❌ Failed to send email after multiple attempts."


def send_email_async(receiver, subject, html_body):
    """Send email in background thread (non-blocking)"""
    thread = threading.Thread(target=send_email_sync, args=(receiver, subject, html_body), daemon=True)
    thread.start()


# ==================== EMAIL TEMPLATES ====================

def email_complaint_submitted(name, student_id, ticket, category, issue, description):
    """Beautiful HTML email for new complaint submission"""
    html_body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 2px solid #0EA5E9; border-radius: 12px; padding: 30px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);">
                
                <h2 style="color: #0EA5E9; text-align: center; margin-bottom: 20px;">✅ Complaint Submitted Successfully</h2>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0 0 15px 0;"><strong>Dear {name},</strong></p>
                    <p>Your complaint has been successfully registered in our system. Here are your details:</p>
                    
                    <table style="width: 100%; margin: 20px 0;">
                        <tr>
                            <td style="padding: 10px; background: #f0f9ff; font-weight: bold;">Ticket ID</td>
                            <td style="padding: 10px; background: white; color: #0EA5E9; font-weight: bold;">{ticket}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #f0f9ff; font-weight: bold;">Student ID</td>
                            <td style="padding: 10px; background: white;">{student_id}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #f0f9ff; font-weight: bold;">Category</td>
                            <td style="padding: 10px; background: white; color: #06B6D4; font-weight: bold;">{category}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #f0f9ff; font-weight: bold;">Issue</td>
                            <td style="padding: 10px; background: white;">{issue}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #f0f9ff; font-weight: bold; vertical-align: top;">Description</td>
                            <td style="padding: 10px; background: white;">{description[:200]}...</td>
                        </tr>
                    </table>
                    
                    <p style="margin-top: 20px; color: #666;"><strong>📋 Next Steps:</strong></p>
                    <ul style="color: #666;">
                        <li>Save your Ticket ID: <strong>{ticket}</strong></li>
                        <li>You will receive updates via email as your complaint is processed</li>
                        <li>Track your complaint status in "My Complaints" section</li>
                        <li>Expected resolution: 48-72 hours</li>
                    </ul>
                </div>
                
                <div style="background: #ecf6ff; padding: 15px; border-radius: 8px; text-align: center;">
                    <p style="margin: 0; color: #0EA5E9;"><strong>📞 Need Help?</strong></p>
                    <p style="margin: 5px 0 0 0; color: #666;">Contact Admin: admin@mrecw.edu.in | Security: 040-XXXXXXX</p>
                </div>
                
                <p style="margin-top: 20px; color: #999; font-size: 12px; text-align: center;">
                    VoiceHer - Smart Campus Care System | MRECW Engineering College for Women
                </p>
            </div>
        </body>
    </html>
    """
    return html_body


def email_complaint_status_updated(name, ticket, status, category):
    """Beautiful HTML email for status update"""
    status_color = {
        "Pending": "#FFA500",
        "In Progress": "#0EA5E9",
        "Resolved": "#10B981",
        "Escalated": "#EF4444"
    }.get(status, "#666")
    
    html_body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 2px solid {status_color}; border-radius: 12px; padding: 30px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);">
                
                <h2 style="color: {status_color}; text-align: center; margin-bottom: 20px;">🔄 Your Complaint Status Updated</h2>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0 0 15px 0;"><strong>Hi {name},</strong></p>
                    <p>Your complaint status has been updated. Here's the latest information:</p>
                    
                    <div style="background: linear-gradient(135deg, #f0f9ff 0%, #ecf6ff 100%); padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {status_color};">
                        <p style="margin: 0 0 10px 0; color: #666;">Ticket ID</p>
                        <p style="margin: 0 0 20px 0; color: {status_color}; font-size: 18px; font-weight: bold;">{ticket}</p>
                        
                        <p style="margin: 0 0 10px 0; color: #666;">Current Status</p>
                        <p style="margin: 0; color: {status_color}; font-size: 18px; font-weight: bold;">● {status}</p>
                    </div>
                    
                    <p style="margin: 0; color: #666;"><strong>Category:</strong> {category}</p>
                    <p style="margin: 10px 0 0 0; color: #999; font-size: 14px;">Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="background: #10B98130; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0; color: #10B981;"><strong>✅ What's Next?</strong></p>
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">Your complaint is being actively handled by our team. We'll send you another update once it reaches the next stage.</p>
                </div>
                
                <div style="background: #ecf6ff; padding: 15px; border-radius: 8px; text-align: center;">
                    <p style="margin: 0; color: #0EA5E9;"><strong>📞 Questions?</strong></p>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 14px;">Contact us: admin@mrecw.edu.in</p>
                </div>
                
                <p style="margin-top: 20px; color: #999; font-size: 12px; text-align: center;">
                    VoiceHer - Smart Campus Care System | MRECW Engineering College for Women
                </p>
            </div>
        </body>
    </html>
    """
    return html_body


def email_admin_alert(student_name, ticket, category, issue, description):
    """Beautiful HTML email for admin alert"""
    html_body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; border: 2px solid #EF4444; border-radius: 12px; padding: 30px; background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);">
                
                <h2 style="color: #DC2626; text-align: center; margin-bottom: 20px;">🔔 NEW COMPLAINT ALERT</h2>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0 0 15px 0;"><strong>A new complaint has been submitted and requires attention:</strong></p>
                    
                    <table style="width: 100%; margin: 20px 0; border-collapse: collapse;">
                        <tr style="background: #f9fafb;">
                            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold; width: 30%;">Ticket ID</td>
                            <td style="padding: 12px; border: 1px solid #e5e7eb; color: #DC2626; font-weight: bold;">{ticket}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold;">Student Name</td>
                            <td style="padding: 12px; border: 1px solid #e5e7eb;">{student_name}</td>
                        </tr>
                        <tr style="background: #f9fafb;">
                            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold;">Category</td>
                            <td style="padding: 12px; border: 1px solid #e5e7eb; color: #0EA5E9; font-weight: bold;">{category}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold;">Issue</td>
                            <td style="padding: 12px; border: 1px solid #e5e7eb;">{issue}</td>
                        </tr>
                        <tr style="background: #f9fafb;">
                            <td style="padding: 12px; border: 1px solid #e5e7eb; font-weight: bold; vertical-align: top;">Description</td>
                            <td style="padding: 12px; border: 1px solid #e5e7eb;">{description[:300]}</td>
                        </tr>
                    </table>
                    
                    <p style="margin: 20px 0 0 0; padding: 15px; background: #FEF3C7; border-radius: 6px; color: #92400E;">
                        <strong>⚠️ Action Required:</strong> Please review and assign this complaint to the appropriate team member.
                    </p>
                </div>
                
                <p style="margin-top: 20px; color: #999; font-size: 12px; text-align: center;">
                    VoiceHer Admin Alert | MRECW Engineering College for Women
                </p>
            </div>
        </body>
    </html>
    """
    return html_body


def email_emergency_sos(student_name, ticket, timestamp):
    """URGENT: Emergency SOS Alert email"""
    html_body = f"""
    <html>
        <body style="font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #fff;">
            <div style="max-width: 600px; margin: 0 auto; border: 3px solid #EF4444; border-radius: 12px; padding: 30px; background: linear-gradient(135deg, #7F1D1D 0%, #DC2626 100%);">
                
                <h2 style="color: #FCA5A5; text-align: center; margin-bottom: 20px; font-size: 28px;">🚨 EMERGENCY SOS ALERT 🚨</h2>
                
                <div style="background: rgba(255, 255, 255, 0.95); padding: 20px; border-radius: 8px; margin-bottom: 20px; color: #333;">
                    <p style="margin: 0 0 15px 0; font-size: 16px;"><strong>⚠️ URGENT - Emergency assistance required immediately!</strong></p>
                    
                    <table style="width: 100%; margin: 20px 0;">
                        <tr>
                            <td style="padding: 10px; background: #FEE2E2; font-weight: bold;">Student Name</td>
                            <td style="padding: 10px; background: white;">{student_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #FEE2E2; font-weight: bold;">Ticket ID</td>
                            <td style="padding: 10px; background: white; color: #DC2626; font-weight: bold;">{ticket}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #FEE2E2; font-weight: bold;">Time</td>
                            <td style="padding: 10px; background: white;">{timestamp}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; background: #FEE2E2; font-weight: bold;">Status</td>
                            <td style="padding: 10px; background: white; color: #EF4444; font-weight: bold;">🔴 CRITICAL - IMMEDIATE ACTION REQUIRED</td>
                        </tr>
                    </table>
                    
                    <p style="margin: 15px 0; color: #DC2626; font-weight: bold;">📍 LOCATION: GPS data captured and stored</p>
                    <p style="margin: 0; color: #666;">🔔 Alarm siren activated on student's portal</p>
                </div>
                
                <div style="background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 8px; color: #FCA5A5; border: 2px solid #FCA5A5;">
                    <p style="margin: 0 0 10px 0; font-weight: bold;">REQUIRED ACTIONS:</p>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Dispatch security team immediately</li>
                        <li>Contact Warden on duty</li>
                        <li>Alert Campus Security</li>
                        <li>Prepare emergency response protocol</li>
                    </ul>
                </div>
                
                <p style="margin-top: 20px; color: #FCA5A5; font-size: 12px; text-align: center;">
                    VoiceHer Emergency Response System | MRECW Security
                </p>
            </div>
        </body>
    </html>
    """
    return html_body
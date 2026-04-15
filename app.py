import os
import socket
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from ai_model import categorize, get_priority, chatbot_response
from auth import *
from database import *  # includes get_complaint_by_id now

st.set_page_config(page_title="MRECW Complaint Portal", layout="wide")

create_users()
create_table()

ADMIN_EMAILS = [email.strip() for email in os.environ.get("ADMIN_EMAILS", "batularishitha@gmail.com").split(",") if email.strip()]
DEFAULT_SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
DEFAULT_SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
DEFAULT_EMAIL_SENDER = os.environ.get("EMAIL_SENDER", os.environ.get("SMTP_EMAIL", "your.email@example.com"))
DEFAULT_EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", os.environ.get("SMTP_PASSWORD", ""))
SIREN_PATH = os.path.join(os.path.dirname(__file__), "siren.wav")


def get_email_config():
    sender = st.session_state.get("EMAIL_SENDER") or DEFAULT_EMAIL_SENDER
    password = st.session_state.get("EMAIL_PASSWORD") or DEFAULT_EMAIL_PASSWORD
    server = st.session_state.get("SMTP_SERVER") or DEFAULT_SMTP_SERVER
    port = st.session_state.get("SMTP_PORT") or DEFAULT_SMTP_PORT
    return sender, password, server, port


def get_admin_emails():
    raw_list = st.session_state.get("ADMIN_EMAILS_INPUT") or ", ".join(ADMIN_EMAILS)
    return [email.strip() for email in raw_list.split(",") if email.strip()]


def send_email_alert(subject, body, recipients):
    email_sender, email_password, smtp_server, smtp_port = get_email_config()
    if not email_password or email_sender == "your.email@example.com":
        return False, "Please configure EMAIL_SENDER (or SMTP_EMAIL) and EMAIL_PASSWORD (or SMTP_PASSWORD) environment variables to send emails, or enter them in the app settings."

    if not smtp_server or not smtp_server.strip():
        return False, "SMTP_SERVER is not configured. Please set a valid SMTP host such as smtp.gmail.com."

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_sender
    message["To"] = ", ".join(recipients)
    message.set_content(body)

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls(context=context)
            server.login(email_sender, email_password)
            server.send_message(message)
        return True, "Email sent successfully."
    except socket.gaierror:
        return False, f"Email sending failed: SMTP host '{smtp_server}' could not be resolved. Check your SMTP_SERVER setting and DNS/network connectivity."
    except smtplib.SMTPAuthenticationError:
        return False, "Email sending failed: authentication error. Verify your email/password or app password."
    except Exception as error:
        return False, f"Email sending failed: {error}"


def test_smtp_settings():
    email_sender, email_password, smtp_server, smtp_port = get_email_config()
    if not email_password or email_sender == "your.email@example.com":
        return False, "Please enter a valid sender email and password first."
    if not smtp_server or not smtp_server.strip():
        return False, "Please enter a valid SMTP server, e.g. smtp.gmail.com."

    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(email_sender, email_password)
        return True, "SMTP settings are correct. Connection successful."
    except socket.gaierror:
        return False, f"SMTP host '{smtp_server}' could not be resolved. Check SMTP_SERVER and your network."
    except smtplib.SMTPAuthenticationError:
        return False, "SMTP login failed. Check your email and password, or use an app password for Gmail."
    except Exception as error:
        return False, f"SMTP test failed: {error}"


def get_notification_summary():
    counts = get_complaint_counts()
    total = sum(counts.values())
    return {
        "total": total,
        "pending": counts.get("Pending", 0),
        "in_progress": counts.get("In Progress", 0),
        "resolved": counts.get("Resolved", 0),
    }


def generate_ticket(name, sid):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_name = name.strip().upper().replace(" ", "")[:4] if name else "USER"
    sanitized_sid = sid.strip().upper().replace(" ", "")[-4:] if sid else "0000"
    return f"MRECW-{sanitized_name}-{sanitized_sid}-{timestamp}"


st.markdown(
    """
    <style>
        body {
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 25%, #A78BFA 50%, #F472B6 75%, #EC4899 100%);
            color: #1f2937;
        }
        .stApp, .reportview-container, .main, .block-container {
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 25%, #A78BFA 50%, #F472B6 75%, #EC4899 100%) !important;
            backdrop-filter: blur(18px);
            border-radius: 30px;
            box-shadow: 0 22px 65px rgba(15, 23, 42, 0.08);
        }
        .block-container {
            padding: 2rem 2rem 3rem !important;
            background: rgba(255, 255, 255, 0.92) !important;
            border-radius: 20px !important;
        }
        .stButton>button {
            border-radius: 16px;
            background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 50%, #A78BFA 100%);
            color: white;
            font-weight: 700;
            border: 1px solid rgba(14, 165, 233, 0.35);
            padding: 0.9rem 1.3rem;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #0284C7 0%, #0891B2 50%, #9333EA 100%);
            transform: translateY(-2px);
            box-shadow: 0 12px 28px rgba(14, 165, 233, 0.4);
        }
        .stTextInput>div>div>input, .stTextInput>div>div>textarea, .stSelectbox>div>div>div>div,
        .stNumberInput>div>div>input, .stFileUploader>div>div {
            border-radius: 16px;
            border: 2px solid rgba(14, 165, 233, 0.25);
            background: rgba(255,255,255,0.98);
            color: #1f2937;
        }
        .stTextInput>div>div>input::placeholder, .stTextInput>div>div>textarea::placeholder {
            color: rgba(15, 23, 42, 0.45);
        }
        .login-card {
            padding: 2rem 2rem 2.4rem;
            border-radius: 30px;
            background: #ffffff;
            box-shadow: 0 24px 60px rgba(14, 165, 233, 0.2);
            border: 2px solid rgba(14, 165, 233, 0.2);
            backdrop-filter: blur(10px);
        }
        .login-card h2 {
            background: linear-gradient(135deg, #0EA5E9, #A78BFA, #F472B6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            font-size: 2.2rem;
        }
        .login-card p {
            color: #64748b;
            margin-top: 0.25rem;
            margin-bottom: 1.5rem;
            line-height: 1.7;
        }
        .stRadio > div { margin-bottom: 1rem; }
        .stRadio label, section[data-testid="stSidebar"] label {
            color: #0EA5E9 !important;
            font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] label { font-size: 1rem !important; }
        section[data-testid="stSidebar"] [role="radio"] { accent-color: #06B6D4 !important; }
        [role="radio"] { accent-color: #06B6D4 !important; }
        .sos-button button {
            background: linear-gradient(135deg, #F472B6 0%, #EC4899 50%, #0EA5E9 100%);
            border-radius: 18px;
            color: white;
            font-weight: 700;
            border: 2px solid #EC4899;
        }
        .sos-button button:hover { 
            background: linear-gradient(135deg, #EC4899 0%, #F472B6 50%, #06B6D4 100%);
            box-shadow: 0 12px 32px rgba(236, 72, 153, 0.4);
        }
        .logo-container {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #E0F2FE 0%, #F3E8FF 50%, #FCE7F3 100%);
            border-radius: 28px;
            margin-bottom: 1.5rem;
            box-shadow: 0 20px 40px rgba(14, 165, 233, 0.1);
            border: 2px solid rgba(14, 165, 233, 0.1);
        }
        .logo-container img { display: block; margin: 0 auto; }
        .college-header {
            text-align: center;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 3px solid #DC2626;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
        }
        .college-header-logo img {
            height: 70px;
            width: auto;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
        }
        .college-header h1 {
            color: #DC2626;
            font-size: 2.3rem;
            font-weight: 900;
            margin: 0;
            letter-spacing: 1.5px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
            display: inline-block;
        }
        .dashboard-title { 
            background: linear-gradient(135deg, #0EA5E9, #A78BFA, #F472B6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.8rem; 
            font-weight: 800; 
            text-align: center; 
            margin-bottom: 1.8rem; 
        }
        .dashboard-card {
            padding: 1.75rem;
            border-radius: 26px;
            background: rgba(255, 255, 255, 0.95);
            border: 2px solid rgba(14, 165, 233, 0.12);
            box-shadow: 0 18px 45px rgba(14, 165, 233, 0.1);
            margin-bottom: 1.25rem;
        }
        .dashboard-card h3 { 
            margin-top: 0; 
            background: linear-gradient(135deg, #0EA5E9, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        [data-testid="stDataFrame"] {
            background: rgba(240, 249, 255, 0.98) !important;
            border-radius: 20px !important;
            color: #0f172a !important;
            border: 2px solid rgba(14, 165, 233, 0.15) !important;
        }
        .css-1cpxqw2 { color: #0EA5E9 !important; font-weight: 700 !important; }
        .css-1v0mbdj { background-color: rgba(14, 165, 233, 0.06) !important; }
        .css-1lcbmhc, .css-1v4u2gq, .css-1q8f2ux { background-color: rgba(14, 165, 233, 0.05) !important; }
        h1, h2, h3, h4, h5, h6, p, div { color: #111827; }
        .stMarkdown, .stText { color: #111827; }
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.98) !important;
            border-right: 2px solid rgba(14, 165, 233, 0.1);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "role" not in st.session_state:
    st.session_state.role=None

# ---------------- LOGIN PAGE ----------------
if st.session_state.role is None:

    # College Name Header
    st.markdown(
        """
        <div class='college-header'>
            <h1>MALLA REDDY ENGINEERING COLLEGE FOR WOMEN
            <img src="logo.png" width="60" class="college-header-logo" /></h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        st.image("logo.png", width=120)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<h2>Welcome to MRECW Complaint Portal</h2>", unsafe_allow_html=True)
        st.markdown("<p>Please login or register with your college role to raise and manage campus issues effectively.</p>", unsafe_allow_html=True)

        with st.expander("Email Settings (optional)"):
            st.info("If you want SOS alert emails to reach admins, enter your SMTP email values here and then test the connection.")
            st.markdown(
                "- **Sender Email**: email address that sends the alerts.\n"
                "- **Email Password**: the SMTP password or app password.\n"
                "- **SMTP Server**: outgoing mail server host (example: smtp.gmail.com).\n"
                "- **SMTP Port**: outgoing mail port, usually 587 for TLS."
            )
            st.text_input(
                "Sender Email",
                key="EMAIL_SENDER",
                value=st.session_state.get("EMAIL_SENDER") or DEFAULT_EMAIL_SENDER,
                placeholder="your.email@gmail.com",
                help="The email address that will appear as sender for alert emails.",
            )
            st.text_input(
                "Email Password",
                type="password",
                key="EMAIL_PASSWORD",
                value=st.session_state.get("EMAIL_PASSWORD") or DEFAULT_EMAIL_PASSWORD,
                placeholder="App password or SMTP password",
                help="For Gmail, use an app password instead of your normal Google password.",
            )
            st.text_input(
                "SMTP Server",
                key="SMTP_SERVER",
                value=st.session_state.get("SMTP_SERVER") or DEFAULT_SMTP_SERVER,
                placeholder="smtp.gmail.com",
                help="The SMTP host for your email provider.",
            )
            st.number_input(
                "SMTP Port",
                min_value=1,
                max_value=65535,
                value=st.session_state.get("SMTP_PORT") or DEFAULT_SMTP_PORT,
                key="SMTP_PORT",
                help="The SMTP port, usually 587 for TLS.",
            )
            admin_emails_input = st.text_input(
                "Admin Receiver Emails",
                key="ADMIN_EMAILS_INPUT",
                value=st.session_state.get("ADMIN_EMAILS_INPUT") or ", ".join(ADMIN_EMAILS),
                placeholder="admin1@example.com, admin2@example.com",
                help="Comma-separated admin addresses to notify on new complaints and emergency SOS alerts.",
            )
            st.caption("If you entered these values, click Save Email Settings and then Test SMTP Connection to verify them.")
            st.caption("For Gmail, use an app password: Google account > Security > App passwords.")
            with st.expander("Current Email Settings (for verification)"):
                sender, password, server, port = get_email_config()
                st.write(f"**Sender Email:** {sender}")
                st.write(f"**SMTP Server:** {server}")
                st.write(f"**SMTP Port:** {port}")
                st.write(f"**Password Set:** {'Yes' if password else 'No'}")
                if sender == "your.email@example.com" or not password:
                    st.warning("Email settings are not configured. Please enter valid values above.")
                else:
                    st.info("Email settings appear configured. Test the connection below.")
            if st.button("Save Email Settings"):
                st.success("Email settings saved for this session.")
            if st.button("Test SMTP Connection"):
                test_ok, test_msg = test_smtp_settings()
                if test_ok:
                    st.success(test_msg)
                else:
                    st.error(test_msg)

        option = st.radio("Login/Register", ["Login", "Register"], horizontal=True)

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        role = st.selectbox("Role", [
            "Student",
            "Hostel Admin",
            "College Admin",
            "Canteen Admin",
            "Security Admin",
            "Women Safety Admin",
            "Other Admin"
        ])

        st.write("")
        if option == "Register":

            if st.button("Register"):
                if not username.strip() or not password.strip():
                    st.error("Username and password are required to register.")
                else:
                    ok, msg = register(username, password, role)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
        else:
            if st.button("Login"):
                if not username.strip() or not password.strip():
                    st.error("Please enter both username and password.")
                else:
                    user = login(username, password)
                    if user:
                        st.session_state.username = user[0]
                        st.session_state.role = user[1]
                        st.rerun()
                    else:
                        st.error("Invalid Login")

        st.markdown("</div>", unsafe_allow_html=True)
    with col1:
        st.write("")
    with col3:
        st.write("")

# ---------------- AFTER LOGIN ----------------
else:

    role = st.session_state.role

    st.sidebar.title(role)

    if role != "Student":
        summary = get_notification_summary()
        st.sidebar.markdown("### Admin Notifications")
        st.sidebar.markdown(f"- **Total complaints:** {summary['total']}")
        st.sidebar.markdown(f"- **Pending:** {summary['pending']}")
        st.sidebar.markdown(f"- **In Progress:** {summary['in_progress']}")
        st.sidebar.markdown(f"- **Resolved:** {summary['resolved']}")
        if st.sidebar.button("Refresh Notifications"):
            st.experimental_rerun()
        st.sidebar.markdown("---")

    menu = st.sidebar.radio("Menu",[
        "Dashboard",
        "Submit Complaint",
        "AI Chatbot",
        "Hostel Admin",
        "College Admin",
        "Canteen Admin",
        "Security Admin",
        "Women Safety Admin",
        "Other Admin",
        "Logout"
    ])

    # College Name Header
    st.markdown(
        """
        <div class='college-header'>
            <h1>MALLA REDDY ENGINEERING COLLEGE FOR WOMEN
            <img src="logo.png" width="60" class="college-header-logo" /></h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<h1 class='dashboard-title'>🎓 Smart Campus Care</h1>", unsafe_allow_html=True)

# ---------------- STUDENT ----------------

    if role=="Student":

        if menu=="Dashboard":

            st.markdown("<div class='sos-button'>", unsafe_allow_html=True)
            if st.button("Emergency SOS"):
                student_name = st.session_state.username or "Unknown Student"
                ticket = generate_ticket(student_name, st.session_state.username or "0000")
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sos_description = "Emergency SOS triggered by student. Immediate attention required."

                add_complaint((
                    ticket,
                    student_name,
                    st.session_state.username or "Unknown",
                    None,  # student_email
                    "Unknown",
                    "N/A",
                    "Emergency SOS",
                    "Security",
                    "Emergency SOS",
                    sos_description,
                    None,
                    "High",
                    "Pending",
                    "",
                    "",
                    now,
                ))

                subject = f"Emergency SOS Alert from {student_name}"
                body = (
                    f"An emergency SOS alert was triggered by {student_name} at {now}.\n"
                    f"Immediate security support is required.\n"
                    f"Ticket: {ticket}\n"
                    "A siren sound was triggered in the portal UI.\n"
                )
                admin_recipients = get_admin_emails()
                email_ok, email_msg = send_email_alert(subject, body, admin_recipients)
                
                # Play siren immediately with autoplay
                if os.path.exists(SIREN_PATH):
                    with open(SIREN_PATH, 'rb') as audio_file:
                        audio_bytes = audio_file.read()
                    st.markdown(
                        f"""
                        <audio autoplay>
                            <source src="data:audio/wav;base64,{__import__('base64').b64encode(audio_bytes).decode()}" type="audio/wav">
                        </audio>
                        """,
                        unsafe_allow_html=True
                    )
                    st.info("🔊 Siren sound activated immediately.")
                else:
                    st.warning("Siren sound file not found. Please add siren.wav to the app folder.")
                
                if email_ok:
                    st.error("Emergency alert sent to admins. Help is on the way.")
                else:
                    st.warning(f"SOS submitted, but alert email failed: {email_msg}")
            st.markdown("</div>", unsafe_allow_html=True)

            # Display All Admins in Blue
            st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>👥 Available Admins</h3></div>", unsafe_allow_html=True)
            admins = get_all_admins()
            if admins:
                admin_html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>"
                for admin_username, admin_role in admins:
                    role_emoji = "🏛️" if "College" in admin_role else "🏨" if "Hostel" in admin_role else "🍽️" if "Canteen" in admin_role else "🔒" if "Security" in admin_role else "👩" if "Women" in admin_role else "⚙️"
                    admin_html += f"""
                    <div style='background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 100%); 
                                padding: 20px; border-radius: 12px; border: 2px solid #ff6b35;
                                box-shadow: 0 8px 16px rgba(255, 107, 53, 0.4); cursor: pointer;
                                transition: transform 0.2s;'>
                        <div style='font-weight: 700; color: #ffffff; margin-bottom: 8px; font-size: 1.1rem;'>{role_emoji} {admin_role}</div>
                        <div style='color: #ffe0b2; font-size: 0.9rem;'>👤 {admin_username}</div>
                    </div>
                    """
                admin_html += "</div>"
                st.markdown(admin_html, unsafe_allow_html=True)
            else:
                st.info("No admins available yet.")

            data=get_student_complaints(st.session_state.username)

            df=pd.DataFrame(data,columns=[
                "id","ticket","student_name","student_id","student_email","department","section",
                "complaint_for","category","issue","description","image","priority","status","feedback","rating","date_created"
            ])

            df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                          "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]

            st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📋 Your Complaints</h3></div>", unsafe_allow_html=True)
            st.dataframe(df)

            if not df.empty:
                # Complaint Status Analytics
                st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📊 Complaint Status Overview</h3></div>", unsafe_allow_html=True)
                status_counts = df["Status"].value_counts()
                if not status_counts.empty:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                    st.pyplot(fig)
                else:
                    st.info("No complaints to display status overview.")

                # Category Distribution
                st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📈 Complaint Category Distribution</h3></div>", unsafe_allow_html=True)
                category_counts = df["Category"].value_counts()
                if not category_counts.empty:
                    fig2, ax2 = plt.subplots(figsize=(6, 4))
                    category_counts.plot(kind='bar', ax=ax2, color='#ff6b35')
                    ax2.set_xlabel("Category")
                    ax2.set_ylabel("Number of Complaints")
                    st.pyplot(fig2)
                else:
                    st.info("No complaints to display category distribution.")

                # Additional analytics charts at the bottom
                priority_counts = df["Priority"].value_counts()
                if not priority_counts.empty:
                    st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📊 Priority Analytics</h3></div>", unsafe_allow_html=True)
                    fig3, ax3 = plt.subplots(figsize=(6, 4))
                    priority_counts.plot(kind='bar', ax=ax3, color=['#ff6b35', '#ffa75c', '#ffd27a', '#7dd3fc'])
                    ax3.set_xlabel("Priority")
                    ax3.set_ylabel("Number of Complaints")
                    ax3.set_title("Complaint Priority Distribution")
                    st.pyplot(fig3)

                department_counts = df["Department"].value_counts()
                if not department_counts.empty:
                    st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📊 Department Analysis</h3></div>", unsafe_allow_html=True)
                    fig4, ax4 = plt.subplots(figsize=(6, 4))
                    department_counts.plot(kind='bar', ax=ax4, color='#63b3ed')
                    ax4.set_xlabel("Department")
                    ax4.set_ylabel("Number of Complaints")
                    ax4.set_title("Complaints by Department")
                    st.pyplot(fig4)
            else:
                st.info("No complaints found. Submit a complaint to see analytics.")
        elif menu=="Submit Complaint":

            st.markdown("**Please fill in the complaint form below. Required fields are marked with an asterisk.**")
            st.write("")

            name = st.text_input("Name *")
            sid = st.text_input("Student ID *")
            email = st.text_input("Email *")
            dept = st.text_input("Department *")
            section = st.text_input("Section")
            complaint_for = st.text_input("Complaint For", "Student Services")

            issue = st.text_input("Issue *")
            desc = st.text_area("Description *")

            suggested_category = categorize(f"{issue} {desc}")
            suggested_priority = get_priority(f"{issue} {desc}")

            category = st.selectbox("Category", [
                "Auto Categorize",
                "Hostel",
                "College",
                "Canteen",
                "Security",
                "Women Safety",
                "Other"
            ])
            if category == "Auto Categorize":
                category = suggested_category
                st.info(f"Suggested category: {category}")
                st.markdown(f"**Detected category:** {category}")

            priority = st.selectbox("Priority", ["Auto Estimate", "Low", "Medium", "High"])
            if priority == "Auto Estimate":
                priority = suggested_priority
                st.info(f"Suggested priority: {priority}")

            image = st.file_uploader("Upload Image")

            if st.button("Submit"):
                required_fields = {
                    "Name": name,
                    "Student ID": sid,
                    "Email": email,
                    "Department": dept,
                    "Issue": issue,
                    "Description": desc,
                }
                missing = [label for label, value in required_fields.items() if not str(value).strip()]

                if missing:
                    st.error("Please fill in the following required fields: " + ", ".join(missing))
                else:
                    img = image.read() if image else None
                    ticket = generate_ticket(name, sid)
                    date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    add_complaint((
                        ticket,
                        name,
                        sid,
                        email,
                        dept,
                        section,
                        complaint_for,
                        category,
                        issue,
                        desc,
                        img,
                        priority,
                        "Pending",
                        "",
                        "",
                        date_created,
                    ))

                    counts = get_complaint_counts()
                    pending_count = counts.get("Pending", 0)
                    subject = f"New Complaint Submitted: {ticket}"
                    body = (
                        f"A new complaint has been submitted by {name} ({sid}).\n"
                        f"Category: {category}\n"
                        f"Priority: {priority}\n"
                        f"Issue: {issue}\n"
                        f"Description: {desc}\n"
                        f"Ticket: {ticket}\n\n"
                        f"Current complaint counts:\n"
                        f"- Pending: {pending_count}\n"
                        f"- In Progress: {counts.get('In Progress', 0)}\n"
                        f"- Resolved: {counts.get('Resolved', 0)}\n"
                    )
                    admin_recipients = get_admin_emails()
                    email_ok, email_msg = send_email_alert(subject, body, admin_recipients)
                    if email_ok:
                        st.success("Complaint submitted and admin notified by email.")
                    else:
                        st.warning(f"Complaint submitted, but admin email alert failed: {email_msg}")

                    if email and "@" in email:
                        student_subject = f"Complaint Received: {ticket}"
                        student_body = (
                            f"Hello {name},\n\nYour complaint has been received successfully and assigned ticket number {ticket}.\n\n"
                            f"Category: {category}\nPriority: {priority}\nIssue: {issue}\n\n"
                            "An admin will review your issue shortly.\n\nThank you for using the MRECW Complaint Portal."
                        )
                        student_ok, student_msg = send_email_alert(student_subject, student_body, [email])
                        if student_ok:
                            st.info("Confirmation email sent to your email address.")
                        else:
                            st.warning(f"Complaint submitted, but student email failed: {student_msg}")

                    st.markdown(f"<div class='dashboard-card'><strong>Detected Category:</strong> {category}</div>", unsafe_allow_html=True)

        elif menu == "AI Chatbot":
            st.header("🤖 AI Chatbot Assistant")
            st.markdown(
                "💬 Ask me anything about the Smart Campus Care system, complaints, or campus services. I'll respond instantly!"
            )

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            if "chatbot_input" not in st.session_state:
                st.session_state.chatbot_input = ""

            st.markdown(
                """
                <style>
                    .chat-window {
                        border-radius: 18px;
                        padding: 20px;
                        background: rgba(240, 249, 255, 0.6);
                        border: 2px solid rgba(14, 165, 233, 0.2);
                        margin-bottom: 20px;
                    }
                    .chat-row {
                        margin-bottom: 16px;
                        display: flex;
                        animation: fadeIn 0.3s ease-in;
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateY(10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .chat-bubble-user {
                        background: linear-gradient(135deg, #0EA5E9 0%, #06B6D4 100%);
                        color: white;
                        padding: 14px 18px;
                        border-radius: 18px;
                        margin-left: auto;
                        max-width: 70%;
                        word-wrap: break-word;
                        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
                        font-size: 14px;
                        line-height: 1.5;
                    }
                    .chat-bubble-assistant {
                        background: white;
                        color: #111827;
                        padding: 14px 18px;
                        border-radius: 18px;
                        margin-right: auto;
                        max-width: 70%;
                        word-wrap: break-word;
                        border: 2px solid rgba(14, 165, 233, 0.15);
                        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.1);
                        font-size: 14px;
                        line-height: 1.5;
                    }
                    .chat-empty {
                        text-align: center;
                        color: #94a3b8;
                        padding: 40px 20px;
                        font-style: italic;
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<div class='chat-window'>", unsafe_allow_html=True)
            if not st.session_state.chat_history:
                st.markdown(
                    "<div class='chat-empty'>👋 No messages yet. Start by asking me about the portal, complaints, emergency support, or anything about the system!</div>",
                    unsafe_allow_html=True,
                )
            else:
                for message in st.session_state.chat_history:
                    if message["role"] == "user":
                        st.markdown(
                            f"<div class='chat-row'>"
                            f"<div class='chat-bubble-user'>{message['content']}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<div class='chat-row'>"
                            f"<div class='chat-bubble-assistant'>{message['content']}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
            st.markdown("</div>", unsafe_allow_html=True)

            if "chatbot_warning" not in st.session_state:
                st.session_state.chatbot_warning = ""

            def send_chat_message():
                user_message = st.session_state.chatbot_input.strip()
                if not user_message:
                    st.session_state.chatbot_warning = "Please enter a message before sending."
                    return

                st.session_state.chat_history.append({"role": "user", "content": user_message})
                st.session_state.chatbot_input = ""

                try:
                    response = chatbot_response(user_message)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I'm here to help! Please try again with your question."})

            col1, col2 = st.columns([5, 1], gap="small")
            with col1:
                st.text_area(
                    "Your message",
                    placeholder="Ask anything about the system...",
                    key="chatbot_input",
                    height=80,
                )
            with col2:
                st.button("Send", use_container_width=True, type="primary", on_click=send_chat_message)

            if st.session_state.chatbot_warning:
                st.warning(st.session_state.chatbot_warning)
                st.session_state.chatbot_warning = ""

            if st.session_state.chat_history:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()

    if role != "Student" and menu == "Dashboard":
        summary = get_notification_summary()
        st.markdown("<div class='dashboard-card'><h3 style='color: #ff6b35;'>📣 Admin Dashboard</h3></div>", unsafe_allow_html=True)
        st.markdown(f"**Total complaints:** {summary['total']}  \n**Pending:** {summary['pending']}  \n**In Progress:** {summary['in_progress']}  \n**Resolved:** {summary['resolved']}")

        all_data = get_all_complaints()
        if all_data:
            admin_df = pd.DataFrame(all_data, columns=[
                "id","ticket","student_name","student_id","student_email","department","section",
                "complaint_for","category","issue","description","image","priority","status","feedback","rating","date_created"
            ])
            admin_df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                              "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]
            st.dataframe(admin_df)
        else:
            st.info("No complaints have been submitted yet.")


# ---------------- ADMIN PANELS ----------------

    admin_map={
        "Hostel Admin":"Hostel",
        "College Admin":"College",
        "Canteen Admin":"Canteen",
        "Security Admin":"Security",
        "Women Safety Admin":"Women Safety",
        "Other Admin":"Other"
    }

    if menu in admin_map:

        category=admin_map[menu]

        data=get_category_complaints(category)

        df=pd.DataFrame(data,columns=[
            "id","ticket","student_name","student_id","student_email","department","section",
            "complaint_for","category","issue","description","image","priority","status","feedback","rating","date_created"
        ])

        df.columns = ["ID", "Ticket", "Student Name", "Student ID", "Student Email", "Department", "Section",
                      "Complaint For", "Category", "Issue", "Description", "Image", "Priority", "Status", "Feedback", "Rating", "Date Created"]

        st.header(f"{category} Complaints Dashboard")

        st.dataframe(df)

        cid=st.number_input("Complaint ID",step=1)

        status=st.selectbox("Status",[
            "Pending","In Progress","Resolved"
        ])

        if st.button("Update Status"):

            update_status(cid,status)

            complaint = get_complaint_by_id(cid)
            if complaint and complaint[4]:  # student_email is index 4
                student_email = complaint[4]
                subject = f"Complaint Status Update: {complaint[1]}"  # ticket
                if status == "Resolved":
                    body = (
                        f"Dear {complaint[2]},\n\n"  # student_name
                        f"Your complaint (Ticket: {complaint[1]}) has been resolved.\n"
                        f"Issue: {complaint[8]}\n"  # issue
                        f"Description: {complaint[9]}\n\n"  # description
                        f"Thank you for using MRECW Complaint Portal.\n"
                        f"If you have feedback, please reply to this email.\n\n"
                        f"Best regards,\nMRECW Admin Team"
                    )
                elif status == "In Progress":
                    body = (
                        f"Dear {complaint[2]},\n\n"  # student_name
                        f"Your complaint (Ticket: {complaint[1]}) is now in progress.\n"
                        f"We are working on resolving your issue.\n"
                        f"Issue: {complaint[8]}\n"  # issue
                        f"Description: {complaint[9]}\n\n"  # description
                        f"You will be notified when it's resolved.\n\n"
                        f"Best regards,\nMRECW Admin Team"
                    )
                else:  # Pending or other
                    body = (
                        f"Dear {complaint[2]},\n\n"  # student_name
                        f"Your complaint (Ticket: {complaint[1]}) status has been updated to: {status}.\n"
                        f"Issue: {complaint[8]}\n"  # issue
                        f"Description: {complaint[9]}\n\n"  # description
                        f"Best regards,\nMRECW Admin Team"
                    )
                email_ok, email_msg = send_email_alert(subject, body, [student_email])
                if email_ok:
                    st.success(f"Status updated to '{status}' and student notified by email.")
                else:
                    st.warning(f"Status updated to '{status}', but student email failed: {email_msg}")
            else:
                st.success(f"Status updated to '{status}'.")

# ---------------- LOGOUT ----------------

    if menu=="Logout":

        st.session_state.role=None

        st.rerun()

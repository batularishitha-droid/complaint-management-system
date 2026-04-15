
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Try to import Google GenerativeAI (Free option with good results)
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False


class SmartChatbot:
    def __init__(self):
        self.initialization_status = self._initialize_model()
        
        # Build comprehensive knowledge base
        self.knowledge_base = self._build_knowledge_base()
    
    def _initialize_model(self):
        """Initialize AI model"""
        global GOOGLE_AI_AVAILABLE
        
        if GOOGLE_AI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    print("✓ Google Generative AI initialized")
                    return "google_ai"
                except Exception as e:
                    print(f"Google AI initialization failed: {e}")
        
        print("✓ Using intelligent fallback chatbot")
        return "intelligent_fallback"
    
    def _build_knowledge_base(self):
        """Build comprehensive knowledge base for campus portal"""
        return {
            "complaint_process": {
                "keywords": ["submit", "complaint", "how to", "process", "fill", "form", "submit complaint"],
                "answer": """📝 **How to Submit a Complaint:**

1. **Go to Dashboard** → Click 'Submit Complaint'
2. **Fill Required Fields:**
   - Name, Student ID, Email (mandatory)
   - Department, Section, Complaint For
3. **Describe Issue:**
   - Issue title (short summary)
   - Detailed description
4. **Select Category:** Hostel, College, Canteen, Security, Women Safety, or Other
5. **Set Priority:** Auto-estimate or manually select Low/Medium/High
6. **Upload Image** (optional): Add evidence if needed
7. **Submit:** Click Submit button
8. **Confirmation:** You'll get a ticket number for tracking

📌 Tip: Set accurate priority for faster resolution. Emergency issues = High priority!"""
            },
            
            "track_complaint": {
                "keywords": ["track", "status", "my complaint", "check", "where", "progress", "update"],
                "answer": """🔍 **How to Track Your Complaint:**

1. **Login** to your account
2. **Go to Dashboard** (Student menu)
3. **View 'Your Complaints' Section:** Shows all submitted complaints with details
4. **Check Status:**
   - **Pending:** Waiting for admin review
   - **In Progress:** Admin is working on it
   - **Resolved:** Issue has been resolved
5. **See Details:** Ticket number, date created, priority, feedback
6. **Get Updates:** Admins will email you status changes

⏱️ Average Resolution Time: 3-7 days depending on category"""
            },
            
            "hostel_issues": {
                "keywords": ["hostel", "room", "accommodation", "dorm", "bed", "furniture", "cleaning", "water", "light"],
                "answer": """🏨 **Hostel Complaint Guidelines:**

**Common Issues:**
- Room maintenance/cleanliness
- Water/electricity problems
- Bed/furniture issues
- Noise complaints
- Guest policy violations

**How to Submit:**
1. Select **'Hostel'** as category
2. Describe the issue clearly
3. Provide room number and hostel name
4. Upload photos if possible
5. Set priority (usually Medium unless urgent)

**Escalation:** For urgent hostel issues affecting safety, use **Emergency SOS**"""
            },
            
            "security": {
                "keywords": ["security", "safety", "guard", "alarm", "incident", "theft", "emergency"],
                "answer": """🔒 **Security Issues - Immediate Action:**

**For EMERGENCIES:**
- Click **Emergency SOS Button** ⚠️
- Your location will notify security immediately

**Security Complaints Include:**
- Theft/missing items
- Suspicious activity
- Boundary breaches
- Guard neglect
- Safety concerns

**Submit Complaint:**
1. Category: **'Security'**
2. Describe incident with timestamp
3. Set **High Priority** for urgent issues
4. Include witness names if available
5. Attach videos/photos if you have them

**Response:** Security team responds within 1-2 hours for urgent cases"""
            },
            
            "women_safety": {
                "keywords": ["women safety", "women's", "harassment", "eve teasing", "discrimination", "assault"],
                "answer": """👩 **Women Safety - Confidential Support:**

**Issues Covered:**
- Harassment (verbal/physical)
- Discrimination
- Eve-teasing
- Safety concerns
- Discrimination-based incidents

**Submit Confidentially:**
1. Category: **'Women Safety'**
2. Your complaint is **CONFIDENTIAL**
3. Describe incident without fear
4. Can request **Anonymous Processing**
5. Set **High Priority** - expedited review

**Support Available:**
- Dean of Students Office
- Counseling Services
- Campus Security
- Legal Support (if needed)

⚠️ For immediate danger: Use **Emergency SOS** or call Security"""
            },
            
            "canteen_issues": {
                "keywords": ["canteen", "food", "meal", "quality", "hygiene", "pricing", "cafeteria", "kitchen"],
                "answer": """🍽️ **Canteen Complaints:**

**Issues You Can Report:**
- Food quality problems
- Hygiene concerns
- Inappropriate pricing
- Service quality
- Menu/variety complaints
- Billing errors

**Submit Complaint:**
1. Category: **'Canteen'**
2. Describe issue (food quality, hygiene, etc.)
3. Mention date/time of incident
4. Describe what was ordered
5. Upload photos if applicable
6. Set priority accordingly

**Resolution:** Canteen admin responds within 24-48 hours with corrective actions"""
            },
            
            "college_issues": {
                "keywords": ["college", "class", "exam", "faculty", "staff", "academic", "academics", "classroom", "attendance", "semester", "department", "professor"],
                "answer": """🎓 **College/Academic Issues:**

Academic issues should be submitted using the **College** category when they relate to:
- Classroom facilities
- Exam scheduling or grading
- Faculty or staff behavior
- Attendance or course registration
- Academic policy or syllabus concerns
- Classroom equipment or teaching issues

When you file the complaint, include the course name, section, teacher name, date, and a clear description. Attach evidence if available.

The College admin team will review academic complaints and typically responds within 2-3 days. If you are unsure, choose **Other** and the admins will redirect your complaint to the correct team."""
            },
            
            "admin_visibility": {
                "keywords": ["admin", "seen", "view", "review", "access", "manager", "admin can", "admin sees", "admins"],
                "answer": """👨‍💼 **How Admins See Complaints:**

All complaints submitted through this portal are stored in the shared database. Admin users can view complaints in their dedicated dashboard section and handle them according to category.

- Student complaints appear in the student's own 'Your Complaints' view.
- Admins see complaints for their assigned category (Hostel, College, Canteen, Security, Women Safety, Other).
- Every complaint has a ticket number, status, priority, and description.
- When an admin updates a complaint, the status changes and the student can see that update in real time.

If your complaint is not visible to an admin, confirm that it was submitted correctly and that you selected the right category."""
            },
            
            "emergency_sos": {
                "keywords": ["emergency", "sos", "urgent", "help", "danger", "accident", "injury"],
                "answer": """🚨 **Emergency SOS Button - Use Immediately:**

**Click SOS When:**
- ⚠️ Personal safety threatened
- 🏥 Medical emergency
- 🔥 Fire/natural disaster
- 🚗 Accident/injury
- 🎯 Active threat/violence

**What Happens:**
1. Security team alerted IMMEDIATELY
2. Your location transmitted to guards
3. Ticket generated for reference
4. Response time: < 5 minutes

**After SOS:**
- Call Campus Security: [Contact Number]
- Call Medical: [Contact Number]
- Don't hang up if police called

⚡ SOS = FASTEST emergency response method"""
            },
            
            "tips_and_tricks": {
                "keywords": ["tip", "trick", "how to use", "feature", "help", "advice", "best practice"],
                "answer": """💡 **Portal Tips & Best Practices:**

1. **Clear Descriptions:** More detail = faster resolution
2. **Photos/Evidence:** Attach images when relevant
3. **Accurate Priority:** Choose correctly for faster response
4. **Follow Up:** Check dashboard regularly
5. **Be Professional:** Polite tone gets better responses
6. **Proper Category:** Select most relevant category
7. **Complete Info:** Fill all required fields fully
8. **Email Notifications:** Watch for status update emails
9. **Feedback:** Rate resolution after completion
10. **Escalation:** If unsatisfied, request supervisor review

📊 Complaints with photos: 40% faster resolution"""
            },
            
            "faq": {
                "keywords": ["question", "faq", "frequently asked", "can i", "will", "does", "how do i", "is it possible", "what if"],
                "answer": """❓ **Frequently Asked Questions:**

**Q: How long until my complaint is reviewed?**
A: 24-48 hours for initial review.

**Q: Can I modify a submitted complaint?**
A: No, after submission the complaint is recorded. You can follow up by posting feedback or contacting an admin.

**Q: Is my information confidential?**
A: Yes, your details are protected by the portal policy.

**Q: Can I submit anonymously?**
A: The portal is not fully anonymous, but you can request confidential handling.

**Q: What if I'm not satisfied with the response?**
A: Request a supervisor review or escalate the issue to the Dean.

**Q: Who can submit complaints?**
A: All registered users including students and staff can file complaints.

**Q: Is SOS only for life-threatening issues?**
A: It is intended for urgent safety or security events, but use it if you need immediate help.

**Q: Can I track someone else's complaint?**
A: No, you can only see your own complaints."""
            },

            "portal_notifications": {
                "keywords": ["notify", "notification", "email", "sms", "alert", "alerted", "admin notified", "receiver", "sender"],
                "answer": """📩 **Notifications and Alerts:**

When you submit a complaint, the portal sends an email notification to the admin addresses configured in the portal settings. If you entered your personal email while submitting a complaint, the portal also sends a confirmation email to you.

For Emergency SOS, the portal records the alert, stores it as a high-priority security complaint, and sends an email to the configured admin addresses. The siren sound also plays in your browser when the SOS button is pressed.

If email settings are not configured or fail, the complaint still saves in the database and the portal will show a warning message."""
            },
            
            "categories": {
                "keywords": ["category", "categories", "difference", "which category", "choose category"],
                "answer": """📂 **Complaint Categories Explained:**

🏨 **Hostel:** Room issues, cleanliness, facilities
🎓 **College:** Academic, classroom, faculty issues
🍽️ **Canteen:** Food quality, hygiene, service
🔒 **Security:** Safety, theft, suspicious activity
👩 **Women Safety:** Harassment, discrimination (confidential)
⚙️ **Other:** Miscellaneous issues

**How to Choose:**
- Select MOST RELEVANT category
- Each has dedicated admin team
- Faster response with correct category
- Can't change after submission

**Unsure?** Select 'Other' - admins will redirect"""
            },
        }
    
    def _find_best_match(self, user_input):
        """Find best matching knowledge base entry"""
        user_input_lower = user_input.lower()
        best_match = None
        best_score = 0
        
        for key, data in self.knowledge_base.items():
            score = 0
            for keyword in data["keywords"]:
                keyword_lower = keyword.lower()
                if keyword_lower in user_input_lower:
                    score += len(keyword_lower.split()) * 2
                else:
                    for token in keyword_lower.split():
                        if token and token in user_input_lower:
                            score += 1
            
            if score > best_score:
                best_score = score
                best_match = key
        
        return best_match if best_score >= 1 else None
    
    def _generate_contextual_response(self, user_input):
        """Generate intelligent contextual response"""
        user_input_lower = user_input.lower()
        # Check for greeting
        greetings = ["hello", "hi", "hey", "greetings", "how are"]
        if any(greeting in user_input_lower for greeting in greetings):
            return "👋 Hello! I'm your Campus Complaint Assistant. I'm here to help you navigate the MRECW Complaint Portal. You can ask me about:\n\n✅ How to submit complaints\n✅ Tracking complaint status\n✅ Understanding categories\n✅ Using emergency features\n✅ Portal tips & guidelines\n\nWhat can I help you with?"
        
        # Check for gratitude
        thanks = ["thank", "thanks", "appreciate", "grateful", "great help"]
        if any(thank in user_input_lower for thank in thanks):
            return "😊 You're welcome! I'm glad I could help. Feel free to ask any other questions about the complaint portal. Remember, we're here to ensure your campus issues are resolved quickly!"
        
        # Check knowledge base
        match = self._find_best_match(user_input)
        if match:
            return self.knowledge_base[match]["answer"]
        
        # Smart fallback based on keywords
        if any(word in user_input_lower for word in ["what", "how", "why", "which", "where", "can", "should"]):
            if any(term in user_input_lower for term in ["admin", "seen", "view", "visible", "review"]):
                return self.knowledge_base["admin_visibility"]["answer"]
            if any(term in user_input_lower for term in ["category", "categories", "difference", "which category", "choose category"]):
                return self.knowledge_base["categories"]["answer"]
            if any(term in user_input_lower for term in ["academic", "academics", "college issue", "exam", "faculty", "classroom"]):
                return self.knowledge_base["college_issues"]["answer"]
            if any(term in user_input_lower for term in ["how to submit", "submit complaint", "form", "ticket"]):
                return self.knowledge_base["complaint_process"]["answer"]
            if any(term in user_input_lower for term in ["track", "status", "progress", "update"]):
                return self.knowledge_base["track_complaint"]["answer"]
            if any(term in user_input_lower for term in ["emergency", "sos", "urgent", "danger"]):
                return self.knowledge_base["emergency_sos"]["answer"]
            if any(term in user_input_lower for term in ["hostel", "room", "cleaning", "water", "light"]):
                return self.knowledge_base["hostel_issues"]["answer"]
            if any(term in user_input_lower for term in ["canteen", "food", "hygiene", "pricing"]):
                return self.knowledge_base["canteen_issues"]["answer"]
            if any(term in user_input_lower for term in ["women safety", "harassment", "eve teasing", "discrimination"]):
                return self.knowledge_base["women_safety"]["answer"]

        # Better default helpful response
        return """I understand you're asking about the portal. I can answer any question about submitting complaints, tracking status, categories, SOS alerts, email notifications, and admin review.

Here are examples of what you can ask:
- How to submit a new complaint
- Which category I should select for academics
- How admins see my complaint
- Why my complaint is not showing up
- How Emergency SOS works
- How email alerts are sent

Please ask your question in a normal sentence, and I will give you a full answer."""
    
    def get_response_google_ai(self, user_input):
        """Get response from Google Generative AI"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            system_instruction = """You are a helpful campus complaint assistant for MRECW College. 
Your role is to:
- Help students submit and track complaints
- Explain different complaint categories (Hostel, College, Canteen, Security, Women Safety, Other)
- Guide on using the portal features
- Provide emergency SOS information
- Be friendly, professional, and informative
- Give complete answers with helpful detail, not just a short list of points
- If the user asks a question, answer it fully and clearly
- Use bullet points only when it improves readability
- Mention portal-specific features like complaint submission, tracking, and admin roles
"""
            
            response = model.generate_content(
                f"System: {system_instruction}\n\nUser: {user_input}"
            )
            
            return response.text
        except Exception as e:
            print(f"Google AI error: {e}")
            return self._generate_contextual_response(user_input)
    
    def get_response(self, user_input):
        """Main method to get chatbot response"""
        if self.initialization_status == "google_ai":
            return self.get_response_google_ai(user_input)
        else:
            return self._generate_contextual_response(user_input)


# Initialize chatbot
chatbot = SmartChatbot()


def categorize(text):
    """Categorize complaint - rule based"""
    text_lower = text.lower()
    
    categories = {
        "Hostel": ["hostel", "room", "accommodation", "dorm", "bed", "furniture", "cleaning", "water", "light"],
        "Security": ["security", "safety", "guard", "alarm", "incident", "theft", "suspicious"],
        "Canteen": ["canteen", "food", "meal", "cafeteria", "kitchen", "hygiene", "meal"],
        "College": ["college", "class", "exam", "faculty", "staff", "academic", "classroom"],
        "Women Safety": ["women", "harassment", "safety", "discrimination", "eve teasing"],
        "Other": []
    }
    
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return "Other"


def get_priority(text):
    """Get priority level - rule based"""
    text_lower = text.lower()
    
    high_priority = ["emergency", "urgent", "critical", "danger", "injury", "attack", "threat", "fire", "accident", "sos"]
    medium_priority = ["problem", "issue", "broken", "damaged", "not working", "fail", "complaint", "harassment"]
    
    if any(word in text_lower for word in high_priority):
        return "High"
    elif any(word in text_lower for word in medium_priority):
        return "Medium"
    else:
        return "Low"


def chatbot_response(user_message):
    """Get intelligent chatbot response"""
    return chatbot.get_response(user_message)

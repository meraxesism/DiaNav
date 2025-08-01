from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
from dianav_data import parse_dtc_txt, extract_image_from_pdf
from local_vector_search import LocalVectorSearch
import re
import os
import base64
import requests

app = FastAPI()

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],  # React development server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Include OPTIONS
    allow_headers=["*"],
)

# PDF and data file paths
PDF_PATH = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.pdf"
TXT_PATH = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.txt"
JSON_PATH = "SZM_ DTC_Troubleshooting_Guide_V1.4_main_v2.json"
SAMPLE_PATH = "sample_dtc_data.txt"

# Load DTC index at startup with PDF for image extraction
try:
    if os.path.exists(PDF_PATH) and os.path.exists(TXT_PATH):
        DTC_INDEX = parse_dtc_txt(TXT_PATH, PDF_PATH, JSON_PATH)
        print(f"Loaded DTC data with PDF image extraction support using JSON bounding boxes")
    else:
        DTC_INDEX = parse_dtc_txt(SAMPLE_PATH)
        print(f"Loaded sample DTC data (PDF not available)")
except Exception as e:
    print(f"Error loading DTC data: {e}")
    DTC_INDEX = parse_dtc_txt(SAMPLE_PATH)

# Initialize local vector search
try:
    vector_search = LocalVectorSearch()
    # Try to load existing embeddings, create new ones if not available
    if not vector_search.load_embeddings():
        print("Creating new local embeddings for vector search...")
        vector_search.create_dtc_embeddings(DTC_INDEX)
        vector_search.save_embeddings()
    print("Local vector search initialized successfully")
except Exception as e:
    print(f"Warning: Local vector search not available: {e}")
    vector_search = None

class QueryRequest(BaseModel):
    query: str

class ImageResponse(BaseModel):
    image_data: str
    description: str
    page_num: int

def find_dtc_code_in_query(query: str):
    """Enhanced DTC search that uses vector search as primary method"""
    import re
    
    # First, try exact DTC code patterns (e.g., B1087, B155A-01, etc.)
    match = re.search(r"([A-Z][0-9A-Z]{3,}-?\d{0,2})", query)
    if match:
        return match.group(1)
    
    # Use vector search as primary method for semantic understanding
    if vector_search:
        try:
            vector_results = vector_search.semantic_search(query, top_k=1)
            if vector_results and vector_results[0]['similarity'] > 0.2:  # Lower threshold for better matching
                best_match = vector_results[0]
                print(f"Vector search found: {best_match['dtc_code']} with {best_match['similarity']:.1%} confidence")
                return best_match['dtc_code']
        except Exception as e:
            print(f"Vector search error: {e}")
    
    # Fallback to fuzzy matching if vector search fails
    query_lower = query.lower()
    
    # Try partial DTC code matching (e.g., "B108" matches "B1087")
    for dtc_code in DTC_INDEX.keys():
        if dtc_code.lower().startswith(query_lower) or query_lower.startswith(dtc_code.lower()):
            return dtc_code
    
    return None

def call_ollama_llm(prompt: str, model: str = "llama3.2:3b") -> str:
    """Call Ollama LLM running locally and return the response text."""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response from LLM]")
    except Exception as e:
        print(f"Error calling Ollama LLM: {e}")
        return "[AI Error: Could not generate a human-like response. Please check Ollama is running.]"

@app.get("/health")
def health_check():
    return {"status": "ok", "dtc_count": len(DTC_INDEX)}

def handle_quick_action_request(query: str) -> dict:
    """Handle quick action requests with intelligent responses based on the action type."""
    query_lower = query.lower()
    
    # Determine which quick action was requested
    if "need help finding diagnostic" in query_lower or "finding diagnostic codes" in query_lower:
        return handle_search_dtc_request()
    elif "want to check my vehicle" in query_lower or "check vehicle systems" in query_lower:
        return handle_system_check_request()
    elif "need step-by-step troubleshooting" in query_lower or "troubleshooting guidance" in query_lower:
        return handle_troubleshoot_request()
    elif "want to generate a diagnostic report" in query_lower or "generate diagnostic report" in query_lower:
        return handle_generate_report_request()
    elif "need help with a specific vehicle component" in query_lower or "vehicle component" in query_lower:
        return handle_component_search_request()
    elif "need to analyze symptoms" in query_lower or "analyze symptoms" in query_lower:
        return handle_symptom_analysis_request()
    else:
        # Fallback for unrecognized quick actions
        return {
            "conversational": "I'm here to help with your vehicle diagnostics! What specific issue are you experiencing?",
            "structured": "Quick action request received. Please provide more details about your vehicle issue.",
            "images": [],
            "has_images": False
        }

def handle_search_dtc_request() -> dict:
    """Handle DTC search quick action."""
    conversational = """🔍 **DTC Code Search Assistant**

I can help you find and understand diagnostic trouble codes! Here's how I can assist you:

**What I can do:**
• Search for specific DTC codes (like B1087, P0300, etc.)
• Explain what each code means in simple terms
• Show you the diagnostic procedures
• Provide troubleshooting steps
• Display relevant diagrams and images

**How to use me:**
1. **Enter a DTC code** - Just type the code (e.g., "B1087")
2. **Describe the problem** - Tell me what's happening with your car
3. **Ask about symptoms** - Describe what you're experiencing

**Example queries:**
• "What does DTC B1087 mean?"
• "My car is making a clicking noise, what could it be?"
• "Check engine light is on, help me diagnose"

What DTC code or problem would you like me to help you with?"""
    
    return {
        "conversational": conversational,
        "structured": "DTC Search Assistant - Ready to help find and explain diagnostic codes",
        "images": [],
        "has_images": False
    }

def handle_system_check_request() -> dict:
    """Handle system check quick action."""
    conversational = """📊 **Vehicle System Check Assistant**

I can help you check various vehicle systems! Here are the main systems I can diagnose:

**🔧 Engine Systems:**
• Engine control module (ECM)
• Fuel system
• Ignition system
• Emission control systems

**⚡ Electrical Systems:**
• Battery and charging system
• Starting system
• Lighting systems
• Body control modules

**🛡️ Safety Systems:**
• Airbag systems
• ABS/brake systems
• Traction control
• Stability control

**🎛️ Comfort Systems:**
• HVAC (heating/cooling)
• Seat systems
• Door systems
• Entertainment systems

**Which system would you like me to check?** You can:
• Tell me a specific system (e.g., "Check my engine system")
• Describe symptoms (e.g., "My car won't start")
• Ask about a specific component (e.g., "Check my battery")"""
    
    return {
        "conversational": conversational,
        "structured": "Vehicle System Check Assistant - Ready to diagnose various vehicle systems",
        "images": [],
        "has_images": False
    }

def handle_troubleshoot_request() -> dict:
    """Handle troubleshooting quick action."""
    conversational = """🔧 **Step-by-Step Troubleshooting Assistant**

I'm here to guide you through troubleshooting your vehicle issues step by step!

**How I can help:**
• Break down complex problems into simple steps
• Guide you through diagnostic procedures
• Help you identify the root cause
• Provide safety tips and warnings
• Show you what tools you might need

**What I need from you:**
1. **Describe the problem** - What's happening?
2. **List the symptoms** - What do you notice?
3. **Tell me when it happens** - Under what conditions?
4. **Share any recent changes** - Did you modify anything?

**Example troubleshooting scenarios:**
• "My car won't start - help me troubleshoot"
• "Engine is making a strange noise"
• "Check engine light is flashing"
• "Car is overheating"

**What symptoms are you experiencing?** Let me guide you through the diagnostic process!"""
    
    return {
        "conversational": conversational,
        "structured": "Troubleshooting Assistant - Ready to provide step-by-step diagnostic guidance",
        "images": [],
        "has_images": False
    }

def handle_generate_report_request() -> dict:
    """Handle diagnostic report generation quick action."""
    conversational = """📋 **Diagnostic Report Generator**

I can help you generate comprehensive diagnostic reports! Here's what I can include:

**📊 Report Sections:**
• Vehicle information and VIN
• DTC codes found and their meanings
• Diagnostic procedures performed
• Test results and measurements
• Recommended repairs
• Parts needed
• Estimated costs
• Safety warnings

**🔍 What I need to generate a report:**
1. **Vehicle details** - Make, model, year, VIN
2. **DTC codes** - Any trouble codes you've found
3. **Symptoms** - What problems you're experiencing
4. **Tests performed** - What diagnostics you've done
5. **Findings** - What you've discovered

**📝 Report Formats:**
• Summary report (quick overview)
• Detailed report (comprehensive analysis)
• Service report (for mechanics)
• Customer report (easy to understand)

**What information should I include in your diagnostic report?** Tell me about your vehicle and the issues you're dealing with!"""
    
    return {
        "conversational": conversational,
        "structured": "Diagnostic Report Generator - Ready to create comprehensive diagnostic reports",
        "images": [],
        "has_images": False
    }

def handle_component_search_request() -> dict:
    """Handle component search quick action."""
    conversational = """🔧 **Vehicle Component Search Assistant**

I can help you find information about specific vehicle components! Here are the main component categories:

**🚗 Engine Components:**
• Sensors (O2, MAF, MAP, etc.)
• Actuators (fuel injectors, coils, etc.)
• Mechanical parts (pistons, valves, etc.)

**⚡ Electrical Components:**
• Relays and fuses
• Wiring harnesses
• Control modules
• Switches and buttons

**🛡️ Safety Components:**
• Airbag sensors and modules
• ABS components
• Brake system parts
• Seat belt systems

**🎛️ Comfort Components:**
• HVAC components
• Seat motors and switches
• Door locks and windows
• Audio system parts

**Which component are you having issues with?** You can:
• Name a specific component (e.g., "O2 sensor")
• Describe the problem (e.g., "My seat won't move")
• Ask about a system (e.g., "Brake system components")"""
    
    return {
        "conversational": conversational,
        "structured": "Component Search Assistant - Ready to help with specific vehicle components",
        "images": [],
        "has_images": False
    }

def handle_symptom_analysis_request() -> dict:
    """Handle symptom analysis quick action."""
    conversational = """🚨 **Symptom Analysis Assistant**

I can help you analyze symptoms and identify potential causes! Here's how I can assist:

**🔍 What I can analyze:**
• Engine performance issues
• Electrical problems
• Safety system warnings
• Comfort system malfunctions
• Noise and vibration issues
• Warning lights and messages

**📋 Analysis Process:**
1. **Symptom identification** - What exactly are you experiencing?
2. **Condition analysis** - When does it happen?
3. **Severity assessment** - How serious is the problem?
4. **Cause investigation** - What could be causing it?
5. **Solution recommendations** - What should you do?

**💡 Common symptom categories:**
• **Performance issues** - Power loss, poor acceleration
• **Starting problems** - Won't start, hard to start
• **Running issues** - Rough idle, stalling
• **Warning lights** - Check engine, ABS, airbag lights
• **Noises** - Squealing, knocking, rattling
• **Leaks** - Oil, coolant, transmission fluid

**Describe the symptoms you're experiencing in detail.** Include when they happen, how long they've been occurring, and any other relevant details!"""
    
    return {
        "conversational": conversational,
        "structured": "Symptom Analysis Assistant - Ready to analyze symptoms and identify causes",
        "images": [],
        "has_images": False
    }

@app.post("/query")
def query_dianav(request: QueryRequest):
    query_lower = request.query.lower()
    
    # Handle Quick Action requests first
    if any(phrase in query_lower for phrase in ["need help finding diagnostic", "want to check my vehicle", "need step-by-step troubleshooting", "want to generate a diagnostic report", "need help with a specific vehicle component", "need to analyze symptoms"]):
        return handle_quick_action_request(request.query)
    
    # Handle DTC code queries
    dtc_code = find_dtc_code_in_query(request.query)
    
    if dtc_code and dtc_code in DTC_INDEX:
        dtc = DTC_INDEX[dtc_code]
        structured = dtc['content']
        
        # Use Ollama LLM for conversational responses
        prompt = (
            f"User query: {request.query}\n\n"
            f"Technical information for DTC {dtc['full_code']}:\n{structured}\n\n"
            "You are a friendly, knowledgeable automotive diagnostic expert. Be conversational and helpful, like talking to a friend who needs car advice. Use a warm, approachable tone.\n\n"
            "Respond in this conversational format:\n\n"
            "## 🚗 DTC Code\n"
            "[DTC code and name]\n\n"
            "## 📝 What This Means\n"
            "[Explain in simple terms what this DTC means, like you're explaining to a friend]\n\n"
            "## 🔍 What Could Be Wrong\n"
            "• [Cause 1 - explain simply]\n"
            "• [Cause 2 - explain simply]\n"
            "• [Cause 3 - explain simply]\n\n"
            "## ⚠️ What You Might Notice\n"
            "• [Symptom 1 - in everyday terms]\n"
            "• [Symptom 2 - in everyday terms]\n"
            "• [Symptom 3 - in everyday terms]\n\n"
            "## 🛠️ How to Check\n"
            "1. [Step 1 - simple language]\n"
            "2. [Step 2 - simple language]\n"
            "3. [Step 3 - simple language]\n\n"
            "## 💡 Pro Tips\n"
            "[Give some helpful advice or common mistakes to avoid]\n\n"
            "Keep it friendly and easy to understand. Use emojis and conversational language!"
        )
        conversational = call_ollama_llm(prompt)
        
        # Extract images from the DTC data (already extracted during parsing)
        images = []
        if dtc.get('images'):
            for img in dtc['images']:
                if 'image_data' in img:
                    images.append({
                        'image_data': img['image_data'],
                        'description': img.get('description', 'Diagnostic diagram'),
                        'page_num': img.get('page_num', 0)
                    })
        
        return {
            "conversational": conversational,
            "structured": structured,
            "images": images,
            "has_images": len(images) > 0
        }
    else:
        # Check for conversational responses like "no, that's not right"
        query_lower = request.query.lower()
        conversational_responses = {
            # Technical corrections
            "no": "😅 Oh, my bad! Let me try a different approach. Can you tell me more specifically what's happening with your car?",
            "not right": "🤔 Hmm, I might have misunderstood. What exactly are you experiencing?",
            "wrong": "😕 Sorry about that! Let me get this right - what's the actual issue you're dealing with?",
            "not what i meant": "🙈 Got it! I was way off. Can you describe your car problem in a different way?",
            "that's not it": "😅 Alright, let me start over. What's really going on with your vehicle?",
            "incorrect": "🤷‍♂️ My mistake! Help me understand your car issue better.",
            "nope": "😊 Fair enough! Let's try again - what's the problem you're trying to solve?",
            "nah": "😄 Got it! What's the real issue here?",
            "that's wrong": "🤦‍♂️ You're right, I messed up. What's actually happening?",
            "not correct": "😅 My bad! Can you explain your car problem differently?",
            
            # Casual greetings and chat
            "hey": "👋 Hey there! What's up?",
            "hi": "😊 Hi! How's it going?",
            "hello": "👋 Hello! Nice to chat with you!",
            "sup": "🤙 What's up! How are you doing?",
            "yo": "😎 Yo! What's good?",
            "bro": "🤜🤛 Bro! What's happening?",
            "dude": "🤙 Dude! How's it going?",
            "man": "👨‍🔧 Hey man! What's up?",
            "buddy": "🤝 Hey buddy! How are you?",
            "mate": "🇬🇧 G'day mate! How's your day going?",
            
            # Random casual responses
            "what": "🤔 What what? What are you thinking about?",
            "huh": "😕 Huh? What's on your mind?",
            "ok": "👍 Ok! What's up?",
            "cool": "😎 Cool! What's going on?",
            "nice": "👌 Nice! What's happening?",
            "lol": "😄 Haha! That's funny!",
            "haha": "😂 Funny! What's so funny?",
            "omg": "😱 Oh my! What's the big news?",
            "wow": "😲 Wow! What's so amazing?",
            "seriously": "😐 Seriously though, what's up?",
            
            # Questions about the AI
            "who are you": "🤖 I'm your AI assistant! I can help with car diagnostics, but I'm also just here to chat. What's up?",
            "what are you": "🚗 I'm an AI! I'm pretty good with car stuff, but I can also just hang out and chat. What's on your mind?",
            "how are you": "😊 I'm doing great, thanks for asking! How about you?",
            "are you real": "🤖 I'm an AI assistant, but I'm real good at chatting! What's happening?",
            "are you human": "👨‍🔧 Nope, I'm an AI, but I'm pretty friendly! What's going on?",
            
            # Random words/phrases
            "test": "🧪 Testing what? What are you testing?",
            "hello world": "🌍 Hello world! Nice to meet you!",
            "random": "🎲 Random indeed! What's on your mind?",
            "stuff": "📦 Stuff? What kind of stuff?",
            "things": "🔧 Things? What things are you thinking about?",
            "whatever": "🤷‍♂️ Whatever you say! What's going on?",
            "idk": "🤔 You don't know? What are you trying to figure out?",
            "maybe": "🤷‍♂️ Maybe? What are you thinking about?",
            "probably": "🤔 Probably what? What's on your mind?",
            "sure": "👍 Sure! What's up?",
            
            # Emojis and reactions
            "😊": "😊 Smiling back! What's up?",
            "😂": "😂 Haha! What's so funny?",
            "😎": "😎 Cool! What's going on?",
            "🤔": "🤔 Thinking about what?",
            "😅": "😅 Sweating? What's stressing you out?",
            "😱": "😱 Scared? What's the big deal?",
            "👍": "👍 Thumbs up! What's good?",
            "👎": "👎 Thumbs down? What's not working?",
            "❤️": "❤️ Love you too! What's happening?",
            "🔥": "🔥 Fire! What's hot?",
        }
        
        # Check if user is saying something is wrong
        for phrase, response in conversational_responses.items():
            if phrase in query_lower:
                return {
                    "conversational": response,
                    "structured": "",
                    "images": [],
                    "has_images": False
                }
        
        # Check for longer conversational patterns
        if any(word in query_lower for word in ["how's it going", "how are you doing", "what's up", "what's new"]):
            return {
                "conversational": "😊 I'm doing great! How about you? What's new in your world?",
                "structured": "",
                "images": [],
                "has_images": False
            }
        
        if any(word in query_lower for word in ["thanks", "thank you", "thx", "ty"]):
            return {
                "conversational": "😊 You're welcome! Happy to help with whatever you need!",
                "structured": "",
                "images": [],
                "has_images": False
            }
        
        if any(word in query_lower for word in ["bye", "goodbye", "see you", "later"]):
            return {
                "conversational": "👋 See you later! Have a great day! Come back anytime!",
                "structured": "",
                "images": [],
                "has_images": False
            }
        
        if any(word in query_lower for word in ["good", "great", "awesome", "amazing"]):
            return {
                "conversational": "😎 That's awesome! What's making it so great?",
                "structured": "",
                "images": [],
                "has_images": False
            }
        
        if any(word in query_lower for word in ["bad", "terrible", "awful", "horrible"]):
            return {
                "conversational": "😕 That sounds rough! What's going wrong?",
                "structured": "",
                "images": [],
                "has_images": False
            }
        
        # Try vector search as fallback
        if vector_search:
            try:
                vector_results = vector_search.semantic_search(request.query, top_k=3)
                if vector_results and vector_results[0]['similarity'] > 0.7:  # Good match threshold
                    best_match = vector_results[0]
                    dtc_code = best_match['dtc_code']
                    
                    if dtc_code in DTC_INDEX:
                        dtc = DTC_INDEX[dtc_code]
                        structured = dtc['content']
        
                        # Use Ollama LLM for conversational responses
                        prompt = (
                            f"User query: {request.query}\n\n"
                            f"Technical information for DTC {dtc['full_code']}:\n{structured}\n\n"
                            "You are a friendly, knowledgeable automotive diagnostic expert. Be conversational and helpful, like talking to a friend who needs car advice. Use a warm, approachable tone.\n\n"
                            "Respond in this conversational format:\n\n"
                            "## 🚗 DTC Code\n"
                            "[DTC code and name]\n\n"
                            "## 📝 What This Means\n"
                            "[Explain in simple terms what this DTC means, like you're explaining to a friend]\n\n"
                            "## 🔍 What Could Be Wrong\n"
                            "• [Cause 1 - explain simply]\n"
                            "• [Cause 2 - explain simply]\n"
                            "• [Cause 3 - explain simply]\n\n"
                            "## ⚠️ What You Might Notice\n"
                            "• [Symptom 1 - in everyday terms]\n"
                            "• [Symptom 2 - in everyday terms]\n"
                            "• [Symptom 3 - in everyday terms]\n\n"
                            "## 🛠️ How to Check\n"
                            "1. [Step 1 - simple language]\n"
                            "2. [Step 2 - simple language]\n"
                            "3. [Step 3 - simple language]\n\n"
                            "## 💡 Pro Tips\n"
                            "[Give some helpful advice or common mistakes to avoid]\n\n"
                            f"**🤖 Smart Match:** I found this DTC using AI search with {best_match['similarity']:.1%} confidence - it seemed like the best match for your issue!\n\n"
                            "Keep it friendly and easy to understand. Use emojis and conversational language!"
                        )
                        conversational = call_ollama_llm(prompt)
                        
                        # Extract images from the DTC data (already extracted during parsing)
                        images = []
                        if dtc.get('images'):
                            for img in dtc['images']:
                                if 'image_data' in img:
                                    images.append({
                                        'image_data': img['image_data'],
                                        'description': img.get('description', 'Diagnostic diagram'),
                                        'page_num': img.get('page_num', 0)
                                    })
                        
                        return {
                            "conversational": conversational,
                            "structured": structured,
                            "images": images,
                            "has_images": len(images) > 0,
                            "search_method": "semantic_vector",
                            "confidence": f"{best_match['similarity']:.1%}"
                        }
            except Exception as e:
                print(f"Vector search error: {e}")
        
        # Use Llama 3 for general questions and conversation
        general_prompt = (
            f"User query: {request.query}\n\n"
            "You are a friendly, knowledgeable AI assistant. You're particularly good at automotive diagnostics and car-related topics, but you can also chat about general topics, answer questions, and have casual conversations.\n\n"
            "Guidelines:\n"
            "- Be conversational and friendly, like talking to a friend\n"
            "- If it's about cars, diagnostics, or automotive topics, use your expertise\n"
            "- If it's a general question, answer it helpfully\n"
            "- If it's casual conversation, be engaging and friendly\n"
            "- Use emojis and conversational language\n"
            "- Keep responses helpful and informative\n\n"
            "Respond naturally to the user's query:"
        )
        
        conversational = call_ollama_llm(general_prompt)
        
        # If Llama 3 fails, fall back to keyword suggestions
        if "[AI Error:" in conversational or "[No response from LLM]" in conversational:
            available_dtcs = list(DTC_INDEX.keys())[:5]
            dtc_list = ", ".join(available_dtcs)
            
            conversational = f"""🤔 Hmm, I'm not sure I found the right DTC for your issue. Let me help you better!

**💡 Try asking like this:**
• **Exact codes:** "B1087", "What causes B1087?"
• **Partial codes:** "B108", "B10" 
• **Symptoms:** "seat movement problem", "LIN bus error", "communication fault"
• **General terms:** "seat issue", "bus trouble", "movement error"

**🔍 Available DTC codes in our database:**
{dtc_list}

**💬 You can also ask:**
• "What DTCs are related to seats?"
• "Show me LIN bus problems"
• "What causes communication errors?"

Just describe what's happening with your car, and I'll help you find the right diagnostic info! 😊"""
        
        structured = "General conversation - no structured automotive data."
        return {
            "conversational": conversational,
            "structured": structured,
            "images": [],
            "has_images": False
        }

@app.get("/dtc/{dtc_code}")
def get_dtc_info(dtc_code: str):
    """Get detailed information for a specific DTC code"""
    if dtc_code in DTC_INDEX:
        dtc = DTC_INDEX[dtc_code]
        
        # Extract images if available
        images = []
        if dtc.get('images') and os.path.exists(PDF_PATH):
            for img_ref in dtc['images']:
                try:
                    image_data = extract_image_from_pdf(PDF_PATH, img_ref['page_num'])
                    if image_data:
                        images.append({
                            'image_data': image_data,
                            'description': img_ref['description'],
                            'page_num': img_ref['page_num']
                        })
                except Exception as e:
                    print(f"Error extracting image for DTC {dtc_code}: {e}")
        
        return {
            "dtc_code": dtc_code,
            "code": dtc['code'],
            "full_code": dtc['full_code'],
            "content": dtc['content'],
            "images": images,
            "image_references": dtc.get('image_references', [])
        }
    else:
        raise HTTPException(status_code=404, detail=f"DTC code {dtc_code} not found")

@app.get("/dtc-list")
def get_dtc_list():
    """Get list of all available DTC codes"""
    return {
        "dtc_codes": list(DTC_INDEX.keys()),
        "total_count": len(DTC_INDEX)
    }

@app.get("/search-dtc")
def search_dtc(query: str = ""):
    """Search for DTCs by symptoms, partial codes, or keywords"""
    if not query:
        return {"results": [], "message": "Please provide a search query"}
    
    results = []
    query_lower = query.lower()
    
    # Search through all DTCs
    for dtc_code, dtc_data in DTC_INDEX.items():
        score = 0
        reasons = []
        
        # Check if DTC code matches
        if query_lower in dtc_code.lower():
            score += 10
            reasons.append(f"Code matches: {dtc_code}")
        
        # Check if query is a partial match
        if dtc_code.lower().startswith(query_lower) or query_lower.startswith(dtc_code.lower()):
            score += 8
            reasons.append(f"Partial code match: {dtc_code}")
        
        # Check content for keywords
        content_lower = dtc_data['full_block'].lower()
        if query_lower in content_lower:
            score += 5
            reasons.append("Content contains query")
        
        # Check for specific symptom keywords
        symptom_keywords = ['seat', 'lin', 'bus', 'communication', 'movement', 'error', 'fault', 'problem']
        for keyword in symptom_keywords:
            if keyword in query_lower and keyword in content_lower:
                score += 3
                reasons.append(f"Matches symptom: {keyword}")
        
        if score > 0:
            results.append({
                "dtc_code": dtc_code,
                "dtc_code_line": dtc_data['dtc_code_line'],
                "score": score,
                "reasons": reasons,
                "snippet": dtc_data['full_block'][:200] + "..." if len(dtc_data['full_block']) > 200 else dtc_data['full_block']
            })
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        "query": query,
        "results": results[:10],  # Return top 10 results
        "total_found": len(results)
    }

@app.get("/vector-search")
def vector_search_dtc(query: str = "", top_k: int = 5):
    """Semantic vector search for DTCs using OpenAI embeddings"""
    if not query:
        return {"results": [], "message": "Please provide a search query"}
    
    if not vector_search:
        return {"results": [], "message": "Vector search not available"}
    
    try:
        results = vector_search.semantic_search(query, top_k=top_k)
        
        # Format results for frontend
        formatted_results = []
        for result in results:
            formatted_results.append({
                "dtc_code": result['dtc_code'],
                "dtc_code_line": result['dtc_code_line'],
                "similarity": result['similarity'],
                "confidence": f"{result['similarity']:.1%}",
                "snippet": result['full_block'][:200] + "..." if len(result['full_block']) > 200 else result['full_block']
            })
        
        return {
            "query": query,
            "results": formatted_results,
            "total_found": len(formatted_results),
            "search_type": "semantic_vector"
        }
    except Exception as e:
        return {"results": [], "message": f"Vector search error: {str(e)}"}

@app.get("/extract-image/{page_num}")
def extract_image_from_page(page_num: int):
    """Extract image from a specific page of the PDF"""
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    try:
        image_data = extract_image_from_pdf(PDF_PATH, page_num)
        if image_data:
            return {
                "image_data": image_data,
                "page_num": page_num,
                "description": f"Diagnostic diagram from page {page_num + 1}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"No image found on page {page_num}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting image: {str(e)}")

@app.get("/search-filters")
def get_search_filters():
    """Get available search filters and categories"""
    return {
        "categories": [
            {"id": "all", "name": "All Categories", "count": len(DTC_INDEX)},
            {"id": "common", "name": "Common DTCs", "count": len([k for k in DTC_INDEX.keys() if k.startswith('B')])},
            {"id": "electrical", "name": "Electrical Systems", "count": len([k for k in DTC_INDEX.keys() if 'electrical' in DTC_INDEX[k]['content'].lower()])},
            {"id": "communication", "name": "Communication", "count": len([k for k in DTC_INDEX.keys() if 'communication' in DTC_INDEX[k]['content'].lower()])},
            {"id": "seats", "name": "Seat Systems", "count": len([k for k in DTC_INDEX.keys() if 'seat' in DTC_INDEX[k]['content'].lower()])}
        ],
        "severity_levels": [
            {"id": "critical", "name": "Critical", "color": "#ff4757"},
            {"id": "high", "name": "High", "color": "#ffa502"},
            {"id": "medium", "name": "Medium", "color": "#ffb142"},
            {"id": "low", "name": "Low", "color": "#2ed573"}
        ]
    }

@app.get("/quick-actions")
def get_quick_actions():
    """Get available quick actions"""
    return {
        "actions": [
            {
                "id": "search_dtc",
                "label": "🔍 Search DTC",
                "description": "Find diagnostic codes",
                "prompt": "Please enter a DTC code or describe the problem you're experiencing."
            },
            {
                "id": "system_check",
                "label": "📊 System Check",
                "description": "Check vehicle systems",
                "prompt": "I can help you check various vehicle systems. Which system would you like to diagnose?"
            },
            {
                "id": "troubleshoot",
                "label": "🔧 Troubleshoot",
                "description": "Step-by-step guidance",
                "prompt": "Let's troubleshoot step by step. What symptoms are you experiencing?"
            },
            {
                "id": "generate_report",
                "label": "📋 Generate Report",
                "description": "Create diagnostic report",
                "prompt": "I'll help you generate a diagnostic report. What information should I include?"
            },
            {
                "id": "component_search",
                "label": "🔧 Component Search",
                "description": "Search by vehicle component",
                "prompt": "Which vehicle component are you having issues with?"
            },
            {
                "id": "symptom_analysis",
                "label": "🚨 Symptom Analysis",
                "description": "Analyze symptoms",
                "prompt": "Describe the symptoms you're experiencing in detail."
            }
        ]
    }

@app.post("/export-chat")
def export_chat_session(chat_data: dict):
    """Export chat session data"""
    try:
        # Generate a comprehensive diagnostic report
        report = {
            "export_date": chat_data.get("exportDate"),
            "chat_session": chat_data.get("chat"),
            "summary": {
                "total_messages": len(chat_data.get("chat", {}).get("messages", [])),
                "dtc_codes_found": [],
                "diagnostic_notes": [],
                "recommendations": []
            },
            "metadata": {
                "version": "1.0",
                "exported_by": "DiaNav AI Assistant",
                "format": "diagnostic_report"
            }
        }
        
        # Extract DTC codes from the conversation
        messages = chat_data.get("chat", {}).get("messages", [])
        for msg in messages:
            if msg.get("sender") == "ai":
                # Look for DTC codes in AI responses
                import re
                dtc_matches = re.findall(r'[A-Z][0-9A-Z]{3,}-?\d{0,2}', msg.get("text", ""))
                report["summary"]["dtc_codes_found"].extend(dtc_matches)
        
        # Remove duplicates
        report["summary"]["dtc_codes_found"] = list(set(report["summary"]["dtc_codes_found"]))
        
        return {
            "success": True,
            "report": report,
            "filename": f"dianav-report-{chat_data.get('chat', {}).get('id', 'unknown')}-{chat_data.get('exportDate', '').split('T')[0]}.json"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/diagnostic-stats")
def get_diagnostic_stats():
    """Get diagnostic statistics"""
    total_dtcs = len(DTC_INDEX)
    categories = {}
    
    for dtc_code, dtc_data in DTC_INDEX.items():
        content = dtc_data['content'].lower()
        
        if 'seat' in content:
            categories['seat_systems'] = categories.get('seat_systems', 0) + 1
        if 'communication' in content or 'lin' in content or 'bus' in content:
            categories['communication'] = categories.get('communication', 0) + 1
        if 'electrical' in content or 'wiring' in content:
            categories['electrical'] = categories.get('electrical', 0) + 1
        if 'motor' in content:
            categories['motor_systems'] = categories.get('motor_systems', 0) + 1
    
    return {
        "total_dtcs": total_dtcs,
        "categories": categories,
        "recent_searches": [],  # Could be implemented with session tracking
        "popular_dtcs": list(DTC_INDEX.keys())[:5]  # Top 5 DTCs
    }

@app.get("/component-search")
def search_by_component(component: str = ""):
    """Search DTCs by vehicle component"""
    if not component:
        return {"results": [], "message": "Please specify a component"}
    
    results = []
    component_lower = component.lower()
    
    for dtc_code, dtc_data in DTC_INDEX.items():
        content = dtc_data['content'].lower()
        score = 0
        
        # Component-specific scoring
        if component_lower in ['seat', 'seats'] and 'seat' in content:
            score += 10
        elif component_lower in ['motor', 'motors'] and 'motor' in content:
            score += 10
        elif component_lower in ['lin', 'bus', 'communication'] and ('lin' in content or 'bus' in content or 'communication' in content):
            score += 10
        elif component_lower in ['electrical', 'wiring'] and ('electrical' in content or 'wiring' in content):
            score += 10
        
        if score > 0:
            results.append({
                "dtc_code": dtc_code,
                "dtc_code_line": dtc_data['dtc_code_line'],
                "score": score,
                "component_match": component,
                "snippet": dtc_data['content'][:200] + "..." if len(dtc_data['content']) > 200 else dtc_data['content']
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return {
        "component": component,
        "results": results[:10],
        "total_found": len(results)
    }

@app.get("/symptom-analysis")
def analyze_symptoms(symptoms: str = ""):
    """Analyze symptoms and suggest possible DTCs"""
    if not symptoms:
        return {"results": [], "message": "Please describe the symptoms"}
    
    # Use vector search for symptom analysis
    if vector_search:
        try:
            results = vector_search.semantic_search(symptoms, top_k=5)
            return {
                "symptoms": symptoms,
                "analysis": "AI-powered symptom analysis",
                "results": results,
                "confidence": "High" if results and results[0]['similarity'] > 0.7 else "Medium"
            }
        except Exception as e:
            print(f"Symptom analysis error: {e}")
    
    # Fallback to keyword search
    results = []
    symptoms_lower = symptoms.lower()
    
    for dtc_code, dtc_data in DTC_INDEX.items():
        content = dtc_data['content'].lower()
        score = 0
        
        # Symptom keyword matching
        symptom_keywords = ['stop', 'movement', 'error', 'fault', 'problem', 'issue']
        for keyword in symptom_keywords:
            if keyword in symptoms_lower and keyword in content:
                score += 3
        
        if score > 0:
            results.append({
                "dtc_code": dtc_code,
                "dtc_code_line": dtc_data['dtc_code_line'],
                "score": score,
                "symptoms": symptoms,
                "snippet": dtc_data['content'][:200] + "..." if len(dtc_data['content']) > 200 else dtc_data['content']
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return {
        "symptoms": symptoms,
        "analysis": "Keyword-based symptom analysis",
        "results": results[:5],
        "confidence": "Medium"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




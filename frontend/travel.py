import streamlit as st
from PIL import Image
import io
import base64
import time
import datetime
import requests
import pyttsx3
import cv2
import time


# Set page configuration
st.set_page_config(
    page_title="Travel Buddy",
    page_icon="🧭",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4338ca;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .emergency-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #dc2626;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d1fae5;
        color: #047857;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .contact-card {
        background-color: #f9fafb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .emergency-card {
        background-color: #fee2e2;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #dc2626;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .empty-state {
        text-align: center;
        background-color: #f9fafb;
        padding: 2rem;
        border-radius: 0.5rem;
        color: #6b7280;
    }
    .emergency-empty-state {
        text-align: center;
        background-color: #fee2e2;
        padding: 2rem;
        border-radius: 0.5rem;
        color: #6b7280;
    }
    .stTabs [role="tablist"] {
        justify-content: center
    }
</style>
""", unsafe_allow_html=True)

def handle_start():
    st.write("Start button clicked!")  # Placeholder for your actual code

def handle_start2():
    st.write("Start button clicked!")  # Placeholder for your actual code

if st.button("🚀 Start Weapon Detection!", key="start2_button"):
    try:
        API_URL = "http://192.168.160.40:5000/detect"

        def text_to_speech():
            engine = pyttsx3.init()
            engine.say("Gun detected")
            engine.runAndWait()

        def detect_objects_in_realtime():
            video_capture = cv2.VideoCapture(0)
            gun_detected = False

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                
                _, img_encoded = cv2.imencode('.jpg', frame)
                response = requests.post(API_URL, files={'frame': img_encoded.tobytes()})

                if response.status_code == 200:
                    data = response.json()
                    if data.get("gun_detected"):
                        if not gun_detected:
                            gun_detected = True
                            print("Gun detected!")
                        text_to_speech()
                    else:
                        gun_detected = False
                else:
                    print("Error:", response.text)
                
                cv2.imshow("Client Camera", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            video_capture.release()
            cv2.destroyAllWindows()

        if __name__ == "__main__":
            detect_objects_in_realtime()
        

    except Exception as e:
        st.error(f"Error while calling API: {str(e)}")

        # Save inputs to session state
        st.session_state.source = source
        st.session_state.destination = destination
        st.session_state.route_planned = True
        st.session_state.show_route_success = True
        st.session_state.route_planned_time = time.time()


# Create a large "Start" button
if st.button("🚀 Start", key="start_button"):
    try:
        # Flask server URL (replace with your Flask API IP if remote)
        server_url = "http://192.168.160.85:8000/detect"

        # Initialize TTS (Text-to-Speech) engine
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)  # Set speaking speed

        # Initialize webcam
        cap = cv2.VideoCapture(0)

        # Keep track of last announced name to avoid repeating
        last_name = None

        

        def speak(text):
            engine.say(text)
            engine.runAndWait()

        def send_frame_to_server(frame):
            # Encode frame to JPEG
            _, img_encoded = cv2.imencode(".jpg", frame)
            files = {"file": ("frame.jpg", img_encoded.tobytes(), "image/jpeg")}
            
            try:
                # Send the frame to the server
                response = requests.post(server_url, files=files)

                if response.status_code == 200:
                    return response.json().get("detected_name", "Unknown")
                else:
                    print(f"❌ Server Error: {response.status_code}, {response.text}")
                    return "Unknown"
            except Exception as e:
                print(f"❌ Error sending frame: {e}")
                return "Unknown"

        while True:
            # Capture frame from webcam
            ret, frame = cap.read()
            if not ret:
                print("❌ Error capturing frame")
                break

            # Send frame to the server and get the detected name
            detected_name = send_frame_to_server(frame)

            # Announce the detected person only if they are known and not repeated
            if detected_name != "Unknown" and detected_name != last_name:
                print(f"✅ Known Person Detected: {detected_name}")
                speak(f"{detected_name} is detected.")
                last_name = detected_name

            # Display the video feed
            cv2.imshow("Client - Face Recognition", frame)

            # Exit loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        

    except Exception as e:
        st.error(f"Error while calling API: {str(e)}")

        # Save inputs to session state
        st.session_state.source = source
        st.session_state.destination = destination
        st.session_state.route_planned = True
        st.session_state.show_route_success = True
        st.session_state.route_planned_time = time.time()

# Initialize session state variables if they don't exist
if 'contacts' not in st.session_state:
    st.session_state.contacts = []
if 'emergency_contacts' not in st.session_state:
    st.session_state.emergency_contacts = []
if 'route_planned' not in st.session_state:
    st.session_state.route_planned = False
if 'source' not in st.session_state:
    st.session_state.source = ""
if 'destination' not in st.session_state:
    st.session_state.destination = ""
if 'show_route_success' not in st.session_state:
    st.session_state.show_route_success = False

# App header
st.markdown('<div class="main-header">Dristikon Dashboard</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["🗺️ Route Planning", "👪 Family & Friends", "🚨 Emergency Contacts"])

# Route Planning Tab
with tab1:
    st.markdown('<div class="section-header">Plan Your Route</div>', unsafe_allow_html=True)
    
    # Form for route planning
    col1, col2 = st.columns(2)
    
    with col1:
        source = st.text_input("Source Address", value=st.session_state.source, 
                              placeholder="Enter starting location")
    
    with col2:
        destination = st.text_input("Destination Address", value=st.session_state.destination, 
                                   placeholder="Enter destination location")
    
    if st.button("🗺️ Plan Route", type="primary", use_container_width=True):
        if source and destination:
            try:
                # Initialize text-to-speech engine
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)  # Adjust speaking speed

                # Define API endpoints
                API_URL = "http://192.168.160.40:5000"

                # Get GPS location from API
                location_response = requests.get(f"{API_URL}/get_location")
                if location_response.status_code == 200:
                    location_data = location_response.json()
                    location_text = f"Current GPS Location: {location_data}"
                    print("📍", location_text)
                # engine.say(location_text)
                else:
                    error_text = "Failed to fetch GPS location."
                    print("❌", error_text)
                    engine.say(error_text)

                # Get navigation route
                data = {"end": "77.2643,28.5444"}  # Destination coordinates
                route_response = requests.post(f"{API_URL}/get_route", json=data)

                # Store all step instructions in an array
                step_instructions = []

                if route_response.status_code == 200:
                    route_data = route_response.json()
                    print("\n🛣 Navigation Route:")

                    for step in route_data.get("route", []):
                        step_text = f"Take {step['instruction']} after {step['distance']} meters"
                        step_instructions.append(step_text)  # Store in array

                else:
                    error_text = "Failed to get route."
                    print("❌", error_text)
                    engine.say(error_text)

                # Speak and print all instructions with a delay
                for instruction in step_instructions:
                    print(instruction)
                    engine.say(instruction)
                    engine.runAndWait()

            except Exception as e:
                st.error(f"Error while calling API: {str(e)}")

            # Save inputs to session state
            st.session_state.source = source
            st.session_state.destination = destination
            st.session_state.route_planned = True
            st.session_state.show_route_success = True
            st.session_state.route_planned_time = time.time()
    
    # Success message (will show and then disappear after a few seconds)
    if st.session_state.show_route_success:
        st.markdown(f"""
        <div class="success-message">
            ✅ Route planned successfully from {st.session_state.source} to {st.session_state.destination}!
        </div>
        """, unsafe_allow_html=True)
        
        # Set a timer to hide the success message after 3 seconds
        if time.time() - st.session_state.route_planned_time > 3:
            st.session_state.show_route_success = False
            st.experimental_rerun()
    
    # Map placeholder
    st.markdown("### Map")
    st.image("https://via.placeholder.com/800x400.png?text=Map+would+display+here+with+the+route", 
             caption="Route map visualization would appear here")

# Family & Friends Contacts Tab
with tab2:
    st.markdown('<div class="section-header">Family & Friends</div>', unsafe_allow_html=True)
    
    # Form for adding contacts
    with st.form(key="contact_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name", key="contact_name", placeholder="Enter name")
        
        with col2:
            phone = st.text_input("Phone Number", key="contact_phone", placeholder="Enter phone number")
        
        with col3:
            photo = st.file_uploader("Photo (optional)", type=["jpg", "jpeg", "png"], key="contact_photo")
        
        submit_button = st.form_submit_button(label="👪 Add Contact")
        
        if submit_button and name and phone:
            photo_data = None
            if photo is not None:
                # Process the uploaded image
                img = Image.open(photo)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                photo_data = base64.b64encode(buf.getvalue()).decode("utf-8")
            
            # Add the new contact to the contacts list
            st.session_state.contacts.append({
                "id": datetime.datetime.now().timestamp(),
                "name": name,
                "phone": phone,
                "photo": photo_data
            })
            st.success(f"Added {name} to your contacts!")
    
    # Display contacts
    if st.session_state.contacts:
        st.markdown("### Your Contacts")
        
        # Display contacts in a grid (2 columns)
        col1, col2 = st.columns(2)
        
        for i, contact in enumerate(st.session_state.contacts):
            # Alternate between columns
            with col1 if i % 2 == 0 else col2:
                with st.container():
                    st.markdown(f"""
                    <div class="contact-card">
                        <div style="display: flex; align-items: center;">
                            <div style="flex-shrink: 0; margin-right: 1rem;">
                                {f'<img src="data:image/png;base64,{contact["photo"]}" width="64" height="64" style="border-radius: 50%; object-fit: cover;">' if contact["photo"] else '<div style="width: 64px; height: 64px; border-radius: 50%; background-color: #e5e7eb; display: flex; align-items: center; justify-content: center;">👤</div>'}
                            </div>
                            <div style="flex-grow: 1;">
                                <h3 style="margin: 0; font-weight: 500;">{contact["name"]}</h3>
                                <p style="margin: 0; color: #6b7280;">{contact["phone"]}</p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("❌", key=f"delete_contact_{contact['id']}"):
                        st.session_state.contacts.remove(contact)
                        st.experimental_rerun()
    else:
        st.markdown("""
        <div class="empty-state">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👪</div>
            <p>No contacts added yet. Add your family and friends.</p>
        </div>
        """, unsafe_allow_html=True)

# Emergency Contacts Tab
with tab3:
    st.markdown('<div class="emergency-header">Emergency Contacts</div>', unsafe_allow_html=True)
    
    # Form for adding emergency contacts
    with st.form(key="emergency_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name", key="emergency_name", placeholder="Enter emergency contact name")
        
        with col2:
            phone = st.text_input("Phone Number", key="emergency_phone", placeholder="Enter emergency phone number")
        
        with col3:
            phone = st.text_input("Email", key="email", placeholder="Enter emergency contact E-mail")
        
        
        submit_button = st.form_submit_button(label="🚨 Add Emergency Contact")
        
        if submit_button and name and phone:
            photo_data = None
            if photo is not None:
                # Process the uploaded image
                img = Image.open(photo)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                photo_data = base64.b64encode(buf.getvalue()).decode("utf-8")
            
            # Add the new contact to the contacts list
            st.session_state.contacts.append({
                "id": datetime.datetime.now().timestamp(),
                "name": name,
                "phone": phone,
                "photo": photo_data
            })
            st.success(f"Added {name} to your contacts!")
    
    # Display emergency contacts
    if st.session_state.emergency_contacts:
        st.markdown("### Your Emergency Contacts")
        
        for contact in st.session_state.emergency_contacts:
            with st.container():
                st.markdown(f"""
                <div class="emergency-card">
                    <div style="display: flex; align-items: center;">
                        <div style="flex-shrink: 0; margin-right: 1rem;">
                            {f'<img src="data:image/png;base64,{contact["photo"]}" width="64" height="64" style="border-radius: 50%; object-fit: cover;">' if contact["photo"] else '<div style="width: 64px; height: 64px; border-radius: 50%; background-color: #e5e7eb; display: flex; align-items: center; justify-content: center;">🚨</div>'}
                        </div>
                        <div style="flex-grow: 1;">
                            <h3 style="margin: 0; font-weight: 500;">{contact["name"]}</h3>
                            <p style="margin: 0; color: #6b7280;">{contact["phone"]}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("❌", key=f"delete_emergency_{contact['id']}"):
                    st.session_state.emergency_contacts.remove(contact)
                    st.experimental_rerun()
    else:
        st.markdown("""
        <div class="emergency-empty-state">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚨</div>
            <p>No emergency contacts added yet. Add important contacts for emergencies.</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("**Travel Buddy** - Stay safe while traveling!")
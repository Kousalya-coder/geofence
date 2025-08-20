import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from streamlit_javascript import st_javascript
import json
import time

# Initialize session state
if 'reminders' not in st.session_state:
    st.session_state.reminders = []  # List of {'name': str, 'location': (lat, lng), 'alerted': bool}
if 'current_location' not in st.session_state:
    st.session_state.current_location = None
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'start_location' not in st.session_state:
    st.session_state.start_location = None
if 'dest_location' not in st.session_state:
    st.session_state.dest_location = None

# Initialize geolocator
geolocator = Nominatim(user_agent="geo_fence_alert")
alert_distance = 1.0  # km before alert

# JavaScript for geolocation with enhanced error handling
def get_browser_location():
    try:
        js_code = """
        var coords = {};
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    coords.latitude = position.coords.latitude;
                    coords.longitude = position.coords.longitude;
                },
                function(error) {
                    coords.error = `Geolocation error: ${error.code} - ${error.message}`;
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            coords.error = "Geolocation not supported by this browser";
        }
        coords;
        """
        result = st_javascript(js_code)
        if result and 'latitude' in result:
            return (result['latitude'], result['longitude'])
        elif result and 'error' in result:
            st.error(result['error'])
            return None
        else:
            st.error("Geolocation failed. Please ensure permissions are granted.")
            return None
    except Exception as e:
        st.error(f"Geolocation execution error: {str(e)}")
        return None

# Streamlit UI
st.title("Geofence Alert System")

# Use columns for a compact layout
col1, col2 = st.columns(2)
with col1:
    start_input = st.text_input("Starting point (e.g., Theni)", key="start")
with col2:
    dest_input = st.text_input("Destination (e.g., Madurai)", key="dest")
reminder_input = st.text_input("Reminder location (e.g., Andipatti)", key="reminder")

if st.button("Add Reminder"):
    address = reminder_input.strip() + ", Tamil Nadu"
    if address:
        try:
            loc = geolocator.geocode(address)
            if loc:
                st.session_state.reminders.append({
                    'name': address,
                    'location': (loc.latitude, loc.longitude),
                    'alerted': False
                })
                st.success(f"Added reminder for {address}")
            else:
                st.error("Could not geocode. Try a different spelling or add ', Tamil Nadu'.")
        except Exception as e:
            st.error(f"Geocoding failed: {str(e)}. Check your internet or try again.")
    else:
        st.error("Please enter a reminder location.")

# Display reminders
if st.session_state.reminders:
    st.subheader("Reminders")
    for rem in st.session_state.reminders:
        st.write(f"- {rem['name']}: Lat {rem['location'][0]}, Lng {rem['location'][1]}")

# Start monitoring button
if st.button("Set Locations & Start Monitoring"):
    start_addr = start_input.strip() + ", Tamil Nadu"
    dest_addr = dest_input.strip() + ", Tamil Nadu"
    if start_addr and dest_addr and st.session_state.reminders:
        try:
            start_loc = geolocator.geocode(start_addr)
            dest_loc = geolocator.geocode(dest_addr)
            if start_loc and dest_loc:
                st.session_state.start_location = (start_loc.latitude, start_loc.longitude)
                st.session_state.dest_location = (dest_loc.latitude, dest_loc.longitude)
                st.session_state.monitoring = True
                st.success("Monitoring started!")
            else:
                st.error("Could not geocode start or destination.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Please set start, destination, and at least one reminder.")

# Stop monitoring button
if st.button("Stop Monitoring"):
    st.session_state.monitoring = False
    for rem in st.session_state.reminders:
        rem['alerted'] = False
    st.success("Monitoring stopped.")

# Monitoring loop
if st.session_state.monitoring:
    st.write("Status: Monitoring...")
    location = get_browser_location()
    if location:
        st.session_state.current_location = location
        st.write(f"Current Location: Lat {location[0]}, Lng {location[1]}")
        
        # Check reminders
        for rem in st.session_state.reminders:
            if rem['alerted']:
                continue
            dist = geodesic(st.session_state.current_location, rem['location']).km
            if dist <= alert_distance:
                st.toast(f"Approaching {rem['name']}! Distance: {dist:.2f} km")
                rem['alerted'] = True
    else:
        st.error("Unable to get current location.")
    
    # Simulate periodic updates
    time.sleep(5)  # Poll every 5 seconds
    st.rerun()

else:
    st.write("Status: Idle")
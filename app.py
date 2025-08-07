import streamlit as st
import json
import requests
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# --- YOUR CUSTOM CHANNEL GROUP DEFINITION ---
CHANNEL_GROUP_DEFINITION = {
    "displayName": "My Custom Marketing Channels",
    "description": "Custom channel group for primary marketing activities.",
    "groupingRule": [
        # Esempio di regole - sostituisci con le tue
        {
            "displayName": "Direct",
            "channelGrouping": [
                {
                    "conditions": [
                        {
                            "filter": {
                                "fieldName": "sessionSource",
                                "stringFilter": {
                                    "matchType": "EXACT",
                                    "value": "(direct)"
                                }
                            }
                        }
                    ]
                }
            ]
        },
        {
            "displayName": "Organic Search",
            "channelGrouping": [
                {
                    "conditions": [
                        {
                            "filter": {
                                "fieldName": "sessionMedium",
                                "stringFilter": {
                                    "matchType": "EXACT",
                                    "value": "organic"
                                }
                            }
                        }
                    ]
                }
            ]
        }
        # Aggiungi qui le tue altre regole personalizzate
    ]
}

def get_access_token(credentials_info: dict):
    """
    Ottiene un access token usando le credenziali del service account.
    """
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/analytics.edit"],
    )
    
    # Refresh the credentials to get an access token
    request = Request()
    credentials.refresh(request)
    return credentials.token

def create_custom_channel_group_rest(property_id: str, credentials_info: dict):
    """
    Crea un Custom Channel Group usando le API REST di GA4.
    """
    try:
        # Ottieni il token di accesso
        access_token = get_access_token(credentials_info)
        
        # URL dell'API GA4 Admin
        url = f"https://analyticsadmin.googleapis.com/v1/properties/{property_id}/customChannelGroups"
        
        # Headers per la richiesta
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        # Payload con la definizione del channel group
        payload = CHANNEL_GROUP_DEFINITION
        
        # Effettua la richiesta POST
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ Success! Channel group created with name: {result.get('name', 'Unknown')}"
        else:
            error_details = response.json() if response.content else {}
            error_message = error_details.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"🔴 API Error (Status {response.status_code}): {error_message}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"🔴 Network error: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("🔴 Invalid JSON response from API")
    except Exception as e:
        if "Permission denied" in str(e):
            raise Exception(f"🔴 ERROR: Permission denied for property {property_id}. Ensure the service account has 'Editor' role.")
        else:
            raise Exception(f"🔴 An unexpected error occurred: {e}")

# --- Streamlit Web Interface ---
st.set_page_config(page_title="GA4 Channel Group Creator", layout="centered")
st.title("GA4 Custom Channel Group Creator 🚀")
st.info("This tool uses the GA4 Admin API to create a predefined Custom Channel Group on the property you specify.")

# Mostra le regole attuali configurate
with st.expander("📋 Current Channel Group Rules"):
    st.json(CHANNEL_GROUP_DEFINITION)
    st.caption("You can modify these rules in the app.py file")

# Create a form for user input
with st.form("ga4_form"):
    property_id_input = st.text_input(
        "Enter GA4 Property ID", 
        placeholder="e.g., 123456789",
        help="You can find this ID in your GA4 property settings."
    )
    submitted = st.form_submit_button("Create Channel Group")

# This block runs when the user clicks the button
if submitted:
    if not property_id_input:
        st.warning("Please enter a Property ID.")
    else:
        try:
            # Securely load credentials from Streamlit's secrets manager
            creds = st.secrets["gcp_service_account"]
            
            with st.spinner(f"Creating channel group on property {property_id_input}..."):
                # Call our main function with the user's input
                success_message = create_custom_channel_group_rest(property_id_input, creds)
                st.success(success_message)
                
        except KeyError:
            st.error("🔴 ERROR: GCP service account credentials not found in secrets. Please check your Streamlit secrets configuration.")
        except Exception as e:
            st.error(str(e))

# Debug info (rimuovi in produzione)
if st.checkbox("Show debug info"):
    st.write("Python version:", st.write("Environment is working correctly!"))

import streamlit as st
import json
import requests
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# --- YOUR CUSTOM CHANNEL GROUP DEFINITION ---
CHANNEL_GROUP_DEFINITION = {
    "display_name": "My Custom Marketing Channels",
    "description": "Custom channel group for primary marketing activities.",
    "grouping_rule": [
        {
            "display_name": "Direct",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {
                            "filter": {
                                "field_name": "sessionSource",
                                "string_filter": {
                                    "match_type": "EXACT",
                                    "value": "(direct)"
                                }
                            }
                        },
                        {
                            "filter": {
                                "field_name": "sessionMedium", 
                                "string_filter": {
                                    "match_type": "EXACT",
                                    "value": "(none)"
                                }
                            }
                        }
                    ]
                }
            }
        },
        {
            "display_name": "Organic Search",
            "expression": {
                "filter": {
                    "field_name": "sessionMedium",
                    "string_filter": {
                        "match_type": "EXACT",
                        "value": "organic"
                    }
                }
            }
        },
        {
            "display_name": "Social",
            "expression": {
                "or_group": {
                    "filter_expressions": [
                        {
                            "filter": {
                                "field_name": "sessionMedium",
                                "string_filter": {
                                    "match_type": "EXACT", 
                                    "value": "social"
                                }
                            }
                        },
                        {
                            "filter": {
                                "field_name": "sessionSource",
                                "string_filter": {
                                    "match_type": "CONTAINS",
                                    "value": "facebook"
                                }
                            }
                        }
                    ]
                }
            }
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
        
        # URL dell'API GA4 Admin - Prova con v1alpha e channelGroups
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/channelGroups"
        
        # Headers per la richiesta
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        # Payload con la definizione del channel group
        payload = CHANNEL_GROUP_DEFINITION
        
        # Debug info
        st.write(f"🔍 Debug: Making request to {url}")
        st.write(f"🔍 Debug: Headers (token masked): Authorization: Bearer {access_token[:20]}...")
        
        # Effettua la richiesta POST
        response = requests.post(url, headers=headers, json=payload)
        
        # Debug della risposta
        st.write(f"🔍 Debug: Response status code: {response.status_code}")
        st.write(f"🔍 Debug: Response headers: {dict(response.headers)}")
        st.write(f"🔍 Debug: Raw response content: {response.content}")
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ Success! Channel group created with name: {result.get('name', 'Unknown')}"
        else:
            # Prova a ottenere dettagli dell'errore
            try:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('message', 'Unknown error')
                error_code = error_details.get('error', {}).get('code', 'Unknown code')
                raise Exception(f"🔴 API Error (Status {response.status_code}, Code {error_code}): {error_message}")
            except json.JSONDecodeError:
                raise Exception(f"🔴 API Error (Status {response.status_code}): Response is not valid JSON. Raw content: {response.content}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"🔴 Network error: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"🔴 JSON decode error: {str(e)}. This usually means the API returned an empty or invalid response.")
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

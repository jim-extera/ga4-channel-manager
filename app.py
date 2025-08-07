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
                            "or_group": {
                                "filter_expressions": [{
                                    "filter": {
                                        "field_name": "sessionSource",
                                        "string_filter": {"match_type": "EXACT", "value": "(direct)"}
                                    }
                                }]
                            }
                        },
                        {
                            "or_group": {
                                "filter_expressions": [{
                                    "filter": {
                                        "field_name": "sessionMedium",
                                        "string_filter": {"match_type": "EXACT", "value": "(none)"}
                                    }
                                }]
                            }
                        }
                    ]
                }
            }
        },
        {
            "display_name": "Organic Search",
            "expression": {
                "and_group": {
                    "filter_expressions": [{
                        "or_group": {
                            "filter_expressions": [{
                                "filter": {
                                    "field_name": "sessionMedium",
                                    "string_filter": {"match_type": "EXACT", "value": "organic"}
                                }
                            }]
                        }
                    }]
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
                                "string_filter": {"match_type": "EXACT", "value": "social"}
                            }
                        },
                        {
                            "filter": {
                                "field_name": "sessionSource",
                                "string_filter": {"match_type": "CONTAINS", "value": "facebook"}
                            }
                        }
                    ]
                }
            }
        }
        # Add your other custom rules here
    ]
}

def get_access_token(credentials_info: dict):
    """
    Gets an access token using service account credentials.
    """
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/analytics.edit"],
    )
    
    request = Request()
    credentials.refresh(request)
    return credentials.token

def create_custom_channel_group_rest(property_id: str, credentials_info: dict):
    """
    Creates a Custom Channel Group using GA4 REST APIs.
    """
    try:
        access_token = get_access_token(credentials_info)
        
        # NOTE: Using 'customChannelGroups' which is the v1beta endpoint name.
        # The API documentation can sometimes be inconsistent between client library and REST.
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/customChannelGroups"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        payload = CHANNEL_GROUP_DEFINITION
        
        response = requests.post(url, headers=headers, json=payload)
        
        if 200 <= response.status_code < 300:
            result = response.json()
            return f"✅ Success! Channel group created with name: {result.get('name', 'Unknown')}"
        else:
            try:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('message', 'Unknown error')
                error_code = error_details.get('error', {}).get('code', 'Unknown code')
                raise Exception(f"🔴 API Error (Status {response.status_code}, Code {error_code}): {error_message}")
            except json.JSONDecodeError:
                raise Exception(f"🔴 API Error (Status {response.status_code}): Response is not valid JSON. Raw content: {response.text}")

    except Exception as e:
        raise Exception(f"🔴 An unexpected error occurred: {e}")

# --- Streamlit Web Interface ---
st.set_page_config(page_title="GA4 Channel Group Creator", layout="centered")
st.title("GA4 Custom Channel Group Creator 🚀")
st.info("This tool uses the GA4 Admin API to create a predefined Custom Channel Group on the property you specify.")

with st.expander("📋 Current Channel Group Rules"):
    st.json(CHANNEL_GROUP_DEFINITION)
    st.caption("You can modify these rules in the app.py file")

with st.form("ga4_form"):
    property_id_input = st.text_input(
        "Enter GA4 Property ID", 
        placeholder="e.g., 123456789",
        help="You can find this ID in your GA4 property settings."
    )
    submitted = st.form_submit_button("Create Channel Group")

if submitted:
    if not property_id_input:
        st.warning("Please enter a Property ID.")
    else:
        try:
            creds = st.secrets["gcp_service_account"]
            
            with st.spinner(f"Creating channel group on property {property_id_input}..."):
                success_message = create_custom_channel_group_rest(property_id_input, creds)
                st.success(success_message)
                
        except KeyError:
            st.error("🔴 ERROR: GCP service account credentials not found in secrets. Please check your Streamlit secrets configuration.")
        except Exception as e:
            st.error(str(e))

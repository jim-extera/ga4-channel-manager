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
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "source", "string_filter": {"match_type": "EXACT", "value": "(direct)"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "medium", "string_filter": {"match_type": "EXACT", "value": "(none)"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Organic Search",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "medium", "string_filter": {"match_type": "EXACT", "value": "organic"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Social",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "medium", "string_filter": {"match_type": "EXACT", "value": "social"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "source", "string_filter": {"match_type": "CONTAINS", "value": "facebook"}}}]}}
                    ]
                }
            }
        }
    ]
}

def get_access_token(credentials_info: dict):
    credentials = Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/analytics.edit"],
    )
    request = Request()
    credentials.refresh(request)
    return credentials.token

def create_custom_channel_group_rest(property_id: str, credentials_info: dict):
    try:
        access_token = get_access_token(credentials_info)
        
        # --- FIX: Correct v1beta URL ---
        url = f"https://analyticsadmin.googleapis.com/v1beta/properties/{property_id}/customChannelGroups"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        # --- FIX: Correct payload structure for REST API ---
        payload = {"custom_channel_group": CHANNEL_GROUP_DEFINITION}
        
        response = requests.post(url, headers=headers, json=payload)
        
        if 200 <= response.status_code < 300:
            result = response.json()
            return f"✅ Success! Channel group created with name: {result.get('name', 'Unknown')}"
        else:
            try:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('message', 'Unknown error')
                raise Exception(f"🔴 API Error (Status {response.status_code}): {error_message}")
            except json.JSONDecodeError:
                raise Exception(f"🔴 API Error (Status {response.status_code}): Raw content: {response.text}")

    except Exception as e:
        raise Exception(f"🔴 An unexpected error occurred: {e}")

# --- Streamlit Web Interface ---
st.set_page_config(page_title="GA4 Channel Group Creator", layout="centered")
st.title("GA4 Custom Channel Group Creator 🚀")
st.info("This tool uses the GA4 Admin API to create a predefined Custom Channel Group on the property you specify.")

with st.expander("📋 Current Channel Group Rules"):
    st.json(CHANNEL_GROUP_DEFINITION)

with st.form("ga4_form"):
    property_id_input = st.text_input("Enter GA4 Property ID", placeholder="e.g., 123456789")
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
            st.error("🔴 ERROR: GCP credentials not found in secrets.")
        except Exception as e:
            st.error(str(e))

import streamlit as st
import json
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your/service-account-key.json'
from google.analytics.admin_v1.types import CustomChannelGroup
from google.analytics.admin import AnalyticsAdminServiceClient
from google.api_core import exceptions
from google.oauth2.service_account import Credentials

# --- YOUR CUSTOM CHANNEL GROUP DEFINITION ---
# This part is the same as our original script.
CHANNEL_GROUP_DEFINITION = {
    "display_name": "My Custom Marketing Channels",
    "description": "Custom channel group for primary marketing activities.",
    "system_defined": False,
    "grouping_rule": [
        # ... (Your rules go here, same as before)
    ]
}

# This is our core function, slightly adapted for Streamlit.
# It now takes credentials as an argument instead of reading from a file path.
def create_custom_channel_group(property_id: str, credentials_info: dict):
    """
    Creates a Custom Channel Group on a specified GA4 property.
    """
    try:
        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/analytics.edit"],
        )
        
        client = AnalyticsAdminServiceClient(credentials=credentials)
        channel_group = CustomChannelGroup(
            display_name=CHANNEL_GROUP_DEFINITION["display_name"],
            description=CHANNEL_GROUP_DEFINITION["description"],
            system_defined=CHANNEL_GROUP_DEFINITION["system_defined"],
            grouping_rule=CHANNEL_GROUP_DEFINITION["grouping_rule"],
        )

        request = client.create_custom_channel_group(
            parent=f"properties/{property_id}",
            custom_channel_group=channel_group,
        )
        # Instead of printing, we return a success message.
        return f"✅ Success! Channel group created with name: {request.name}"

    except exceptions.PermissionDenied:
        raise Exception(f"🔴 ERROR: Permission denied for property {property_id}. Ensure the service account has 'Editor' role.")
    except exceptions.InvalidArgument as e:
        raise Exception(f"🔴 ERROR: Invalid argument. Check your rule syntax. API Message: {e.message}")
    except Exception as e:
        raise Exception(f"🔴 An unexpected error occurred: {e}")

# --- Streamlit Web Interface ---

st.set_page_config(page_title="GA4 Channel Group Creator", layout="centered")
st.title("GA4 Custom Channel Group Creator 🚀")

st.info("This tool uses the GA4 Admin API to create a predefined Custom Channel Group on the property you specify.")

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
                success_message = create_custom_channel_group(property_id_input, creds)
                st.success(success_message)
        except Exception as e:
            st.error(str(e))

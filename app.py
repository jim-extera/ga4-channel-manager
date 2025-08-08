import streamlit as st
from google.analytics.admin_v1.types import CustomChannelGroup
from google.analytics.admin import AnalyticsAdminServiceClient
from google.api_core import exceptions
from google.oauth2.service_account import Credentials

# --- YOUR CUSTOM CHANNEL GROUP DEFINITION ---
# This is a simpler dictionary structure that the client library understands.
CHANNEL_GROUP_DEFINITION = {
    "display_name": "My Custom Marketing Channels",
    "description": "Custom channel group for primary marketing activities.",
    "grouping_rule": [
        {
            "display_name": "Direct",
            "expression": {
                "and_group": {
                    "expressions": [
                        {"filter": {"field_name": "source", "string_filter": {"match_type": "EXACT", "value": "(direct)"}}},
                        {"filter": {"field_name": "medium", "string_filter": {"match_type": "EXACT", "value": "(none)"}}}
                    ]
                }
            }
        },
        {
            "display_name": "Organic Search",
            "expression": {"filter": {"field_name": "medium", "string_filter": {"match_type": "EXACT", "value": "organic"}}}
        },
        {
            "display_name": "Social",
            "expression": {
                "or_group": {
                    "expressions": [
                        {"filter": {"field_name": "medium", "string_filter": {"match_type": "EXACT", "value": "social"}}},
                        {"filter": {"field_name": "source", "string_filter": {"match_type": "CONTAINS", "value": "facebook"}}}
                    ]
                }
            }
        }
    ]
}

def create_custom_channel_group(property_id: str, credentials_info: dict):
    """
    Creates a Custom Channel Group using the official Google Admin Client Library.
    """
    try:
        credentials = Credentials.from_service_account_info(
            credentials_info, scopes=["https://www.googleapis.com/auth/analytics.edit"]
        )
        client = AnalyticsAdminServiceClient(credentials=credentials)
        
        # The client library automatically builds the complex objects.
        channel_group = CustomChannelGroup(
            display_name=CHANNEL_GROUP_DEFINITION["display_name"],
            description=CHANNEL_GROUP_DEFINITION["description"],
            grouping_rule=CHANNEL_GROUP_DEFINITION["grouping_rule"],
        )
        
        request = client.create_custom_channel_group(
            parent=f"properties/{property_id}",
            custom_channel_group=channel_group,
        )
        return f"✅ Success! Channel group created with name: {request.name}"

    except exceptions.NotFound:
        raise Exception(f"🔴 API Error 404: The Custom Channel Group feature may not be enabled for property {property_id}.")
    except exceptions.InvalidArgument as e:
        raise Exception(f"🔴 Invalid Argument: {e.message}")
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
                success_message = create_custom_channel_group(property_id_input, creds)
                st.success(success_message)
        except KeyError:
            st.error("🔴 ERROR: GCP credentials not found in secrets.")
        except Exception as e:
            st.error(str(e))

import streamlit as st
import json
import requests
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# --- YOUR CUSTOM CHANNEL GROUP DEFINITION ---
# Ora con i field_name corretti: eachScopeSource e eachScopeMedium
CHANNEL_GROUP_DEFINITION = {
    "display_name": "Extera Channel Group Custom",
    "description": "Custom channel group replicating Extera structure for all properties.",
    "grouping_rule": [
        {
            "display_name": "Direct",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "direct"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeMedium",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "none"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        },
        {
            "display_name": "Google Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "EXACT",
                                                "value": "google"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeMedium",
                                            "string_filter": {
                                                "match_type": "EXACT",
                                                "value": "cpc"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        },
        {
            "display_name": "Meta Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "facebook"
                                            }
                                        }
                                    },
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "instagram"
                                            }
                                        }
                                    },
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "social"
                                            }
                                        }
                                    },
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "stories"
                                            }
                                        }
                                    },
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "fb"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeMedium",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "cpc"
                                            }
                                        }
                                    },
                                    {
                                        "filter": {
                                            "field_name": "eachScopeMedium",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "paid"
                                            }
                                        }
                                    },
                                    {
                                        "filter": {
                                            "field_name": "eachScopeMedium",
                                            "string_filter": {
                                                "match_type": "CONTAINS",
                                                "value": "paidsocial"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        },
        {
            "display_name": "Google Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeSource",
                                            "string_filter": {
                                                "match_type": "EXACT",
                                                "value": "google"
                                            }
                                        }
                                    }
                                ]
                            }
                        },
                        {
                            "or_group": {
                                "filter_expressions": [
                                    {
                                        "filter": {
                                            "field_name": "eachScopeMedium",
                                            "string_filter": {
                                                "match_type": "EXACT",
                                                "value": "organic"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        # Puoi aggiungere qui le altre regole seguendo lo stesso pattern
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

def list_existing_channel_groups(property_id: str, credentials_info: dict):
    """
    Lista i channel groups esistenti per vedere la loro struttura.
    """
    try:
        # Ottieni il token di accesso
        access_token = get_access_token(credentials_info)
        
        # URL dell'API GA4 Admin per listare channel groups
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/channelGroups"
        
        # Headers per la richiesta
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        # Effettua la richiesta GET
        response = requests.get(url, headers=headers)
        
        st.write(f"🔍 List Debug: Response status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            st.write("📋 Existing Channel Groups:")
            st.json(result)
            return result
        else:
            error_details = response.json() if response.content else {}
            st.error(f"Error listing channel groups: {error_details}")
            return None
            
    except Exception as e:
        st.error(f"🔴 Error listing channel groups: {e}")
        return None

# <<< CORREZIONE INIZIA QUI
# Ho aggiunto la definizione della funzione qui
def create_custom_channel_group_rest(property_id: str, credentials_info: dict):
# Ho indentato tutto il blocco di codice sottostante
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
        payload = {
            "display_name": CHANNEL_GROUP_DEFINITION["display_name"],
            "description": CHANNEL_GROUP_DEFINITION["description"],
            "grouping_rule": CHANNEL_GROUP_DEFINITION["grouping_rule"]
        }
        
        # Effettua la richiesta POST
        response = requests.post(url, headers=headers, data=json.dumps({"channel_group": payload}))
        
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
# <<< CORREZIONE FINISCE QUI

# --- Streamlit Web Interface ---
st.set_page_config(page_title="GA4 Channel Group Creator", layout="centered")
st.title("GA4 Custom Channel Group Creator 🚀")
st.info("This tool uses the GA4 Admin API to create a predefined Custom Channel Group on the property you specify.")

# Mostra le regole attuali configurate
with st.expander("📋 Current Channel Group Rules"):
    st.json(CHANNEL_GROUP_DEFINITION["grouping_rule"])
    st.caption("You can modify these rules in the app.py file")

# Create a form for user input
with st.form("ga4_form"):
    property_id_input = st.text_input(
        "Enter GA4 Property ID", 
        placeholder="e.g., 123456789",
        help="You can find this ID in your GA4 property settings."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        submitted = st.form_submit_button("Create Channel Group")
    with col2:
        list_existing = st.form_submit_button("List Existing Channel Groups")

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

# Handle the "List Existing" button
if list_existing:
    if not property_id_input:
        st.warning("Please enter a Property ID.")
    else:
        try:
            creds = st.secrets["gcp_service_account"]
            
            with st.spinner(f"Fetching existing channel groups from property {property_id_input}..."):
                result = list_existing_channel_groups(property_id_input, creds)
                
        except KeyError:
            st.error("🔴 ERROR: GCP service account credentials not found in secrets.")
        except Exception as e:
            st.error(str(e))

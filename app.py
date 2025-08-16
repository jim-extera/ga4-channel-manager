import streamlit as st
import json
import requests
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# --- YOUR CUSTOM CHANNEL GROUP DEFINITION ---
# Versione aggiornata con le 24 regole complete
CHANNEL_GROUP_DEFINITION = {
    "display_name": "Extera Channel Group",
    "description": "Custom channel group replicating the full Extera structure.",
    "grouping_rule": [
        {
            "display_name": "Direct",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "direct"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "none"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Google Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "google"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Meta Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "facebook"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "instagram"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "social"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "stories"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "fb"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "cpc"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "paid"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "paidsocial"}}}
                        ]}}
                    ]
                }
            }
        },
        {
            "display_name": "Newsletter",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*newsletter.*|.*Newsletter.*|.*mail.*|.*outlook.*|.*nl.*|.*newsleeter.*|.*bird.*"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Google Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "google"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "organic"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Facebook Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "facebook"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "Facebook"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [
                            {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}},
                            {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paid"}}}},
                            {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paidsocial"}}}}
                        ]}}
                    ]
                }
            }
        },
        {
            "display_name": "Influencer Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "influencer"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "storie"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Influencer Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "influencer"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Klaviyo Flow",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*klaviyo.*|.*Klaviyo.*"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*flow.*|.*Flow.*|.*email.*"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "IG Shopping",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "IGShopping"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Bing organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "bing"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "yahoo"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "organic"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "referral"}}}
                        ]}}
                    ]
                }
            }
        },
        {
            "display_name": "Growave",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "growave"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Youtube Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "youtube"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Bing Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "bing"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "yahoo"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "cpc"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Google Shopping Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "google"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "product_sync"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Google Lens",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "lens.google.com"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "referral"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Other Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"not_expression": {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*google.*"}}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "organic"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Instagram Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "instagram"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "Instagram"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "IGShopping"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "linktr"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [
                            {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}},
                            {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paid"}}}},
                            {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paidsocial"}}}}
                        ]}}
                    ]
                }
            }
        },
        {
            "display_name": "TikTok Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "tiktok"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "TikTok"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "TIKTOK"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "paid"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "cpc"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "promo"}}}
                        ]}}
                    ]
                }
            }
        },
        {
            "display_name": "TikTok Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*tiktok.*|.*TikTok.*|.*TIKTOK.*"}}},
                            {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*social.*|.*Social.*|.*SOCIAL.*"}}}
                        ]}},
                        {"or_group": {"filter_expressions": [
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*social.*|.*Social.*|.*SOCIAL.*"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "referral"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "not set"}}},
                            {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*tiktok.*|.*TikTok.*|.*TIKTOK.*"}}}
                        ]}}
                    ]
                }
            }
        },
        {
            "display_name": "LinkedIn Ads",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "linkedin"}}}]}},
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "LinkedIn Organic",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "linkedin"}}}]}},
                        {"or_group": {"filter_expressions": [{"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*cpc.*"}}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Trovaprezzi",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "trovaprezzi"}}}]}}
                    ]
                }
            }
        },
        {
            "display_name": "Pinterest",
            "expression": {
                "and_group": {
                    "filter_expressions": [
                        {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "pinterest"}}}]}}
                    ]
                }
            }
        }
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
        access_token = get_access_token(credentials_info)
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/channelGroups"
        headers = {"Authorization": f"Bearer {access_token}"}
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

def create_custom_channel_group_rest(property_id: str, credentials_info: dict):
    """
    Crea un Custom Channel Group usando le API REST di GA4.
    """
    try:
        access_token = get_access_token(credentials_info)
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/channelGroups"
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
        
        # Usiamo il parametro 'json' che gestisce tutto in automatico
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return f"✅ Success! Channel group created with name: {result.get('name', 'Unknown')}"
        else:
            try:
                error_details = response.json()
                error_message = error_details.get('error', {}).get('message', 'Unknown error')
                error_code = error_details.get('error', {}).get('code', 'Unknown code')
                raise Exception(f"🔴 API Error (Status {response.status_code}, Code {error_code}): {error_message}")
            except json.JSONDecodeError:
                raise Exception(f"🔴 API Error (Status {response.status_code}): Response is not valid JSON. Raw content: {response.content}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"🔴 Network error: {str(e)}")
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
with st.expander("📋 Current Channel Group Rules (24 rules loaded)"):
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

# This block runs when the user clicks the "Create" button
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

# Handle the "List Existing" button
if list_existing:
    if not property_id_input:
        st.warning("Please enter a Property ID.")
    else:
        try:
            creds = st.secrets["gcp_service_account"]
            with st.spinner(f"Fetching existing channel groups from property {property_id_input}..."):
                list_existing_channel_groups(property_id_input, creds)
        except KeyError:
            st.error("🔴 ERROR: GCP service account credentials not found in secrets.")
        except Exception as e:
            st.error(str(e))

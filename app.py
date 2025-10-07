import streamlit as st
import json
import requests
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request

# --- DEFINIZIONE DEL TEMPLATE DI DEFAULT ---
# Abbiamo reintrodotto la definizione statica per usarla come opzione di default.
DEFAULT_CHANNEL_GROUP_DEFINITION = {
    "display_name": "Extera Channel Group (Default)",
    "description": "Custom channel group based on the default Extera structure.",
    "grouping_rule": [
        {"display_name": "Direct","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "direct"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "none"}}}]}}]}}},
        {"display_name": "Google Ads","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "google"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}]}}]}}},
        {"display_name": "Meta Ads","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "facebook"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "instagram"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "social"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "stories"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "fb"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "cpc"}}}, {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "paid"}}}, {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "paidsocial"}}}]}}]}}},
        {"display_name": "Newsletter","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*newsletter.*|.*Newsletter.*|.*mail.*|.*outlook.*|.*nl.*|.*newsleeter.*|.*bird.*"}}}]}}]}}},
        {"display_name": "Google Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "google"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "organic"}}}]}}]}}},
        {"display_name": "Facebook Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "facebook"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "Facebook"}}}]}}, {"or_group": {"filter_expressions": [{"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}}, {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paid"}}}}, {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paidsocial"}}}}]}}]}}},
        {"display_name": "Influencer Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "influencer"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "storie"}}}]}}]}}},
        {"display_name": "Influencer Ads","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "influencer"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}]}}]}}},
        {"display_name": "Klaviyo Flow","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*klaviyo.*|.*Klaviyo.*"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*flow.*|.*Flow.*|.*email.*"}}}]}}]}}},
        {"display_name": "IG Shopping","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "IGShopping"}}}]}}]}}},
        {"display_name": "Bing organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "bing"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "yahoo"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "organic"}}}, {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "referral"}}}]}}]}}},
        {"display_name": "Growave","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "growave"}}}]}}]}}},
        {"display_name": "Youtube Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "youtube"}}}]}}]}}},
        {"display_name": "Bing Ads","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "bing"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "yahoo"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "cpc"}}}]}}]}}},
        {"display_name": "Google Shopping Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "google"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "product_sync"}}}]}}]}}},
        {"display_name": "Google Lens","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "EXACT", "value": "lens.google.com"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "referral"}}}]}}]}}},
        {"display_name": "Other Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"not_expression": {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*google.*"}}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "organic"}}}]}}]}}},
        {"display_name": "Instagram Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "instagram"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "Instagram"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "IGShopping"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "linktr"}}}]}}, {"or_group": {"filter_expressions": [{"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}}, {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paid"}}}}, {"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "paidsocial"}}}}]}}]}}},
        {"display_name": "TikTok Ads","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "tiktok"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "TikTok"}}}, {"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "TIKTOK"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "paid"}}}, {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "cpc"}}}, {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "promo"}}}]}}]}}},
        {"display_name": "TikTok Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*tiktok.*|.*TikTok.*|.*TIKTOK.*"}}},{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*social.*|.*Social.*|.*SOCIAL.*"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*social.*|.*Social.*|.*SOCIAL.*"}}},{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "referral"}}},{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "CONTAINS", "value": "not set"}}},{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*tiktok.*|.*TikTok.*|.*TIKTOK.*"}}}]}}]}}},
        {"display_name": "LinkedIn Ads","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "linkedin"}}}]}}, {"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "EXACT", "value": "cpc"}}}]}}]}}},
        {"display_name": "LinkedIn Organic","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "linkedin"}}}]}}, {"or_group": {"filter_expressions": [{"not_expression": {"filter": {"field_name": "eachScopeMedium", "string_filter": {"match_type": "FULL_REGEXP", "value": ".*cpc.*"}}}}]}}]}}},
        {"display_name": "Trovaprezzi","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "trovaprezzi"}}}]}}]}}},
        {"display_name": "Pinterest","expression": {"and_group": {"filter_expressions": [{"or_group": {"filter_expressions": [{"filter": {"field_name": "eachScopeSource", "string_filter": {"match_type": "CONTAINS", "value": "pinterest"}}}]}}]}}}
    ]
}


## 1. FUNZIONI HELPER (INVARIATE)

def get_access_token(credentials_info: dict):
    credentials = Credentials.from_service_account_info(
        credentials_info, scopes=["https://www.googleapis.com/auth/analytics.edit"]
    )
    credentials.refresh(Request())
    return credentials.token

def list_channel_groups(property_id: str, credentials_info: dict):
    try:
        access_token = get_access_token(credentials_info)
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/channelGroups"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get("channelGroups", [])
    except requests.exceptions.HTTPError as err:
        error_details = err.response.json().get("error", {}).get("message", err.response.text)
        raise Exception(f"Errore API nel leggere i gruppi: {error_details}") from err
    except Exception as e:
        raise Exception(f"Errore imprevisto nel leggere i gruppi: {e}") from e

def create_channel_group(property_id: str, credentials_info: dict, channel_group_payload: dict):
    try:
        access_token = get_access_token(credentials_info)
        url = f"https://analyticsadmin.googleapis.com/v1alpha/properties/{property_id}/channelGroups"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=channel_group_payload)
        response.raise_for_status()
        result = response.json()
        return f"✅ Successo! Channel group '{result.get('displayName')}' creato con nome: {result.get('name', 'Sconosciuto')}"
    except requests.exceptions.HTTPError as err:
        error_details = err.response.json().get("error", {}).get("message", err.response.text)
        raise Exception(f"🔴 Errore API nella creazione del gruppo: {error_details}") from err
    except Exception as e:
        raise Exception(f"🔴 Errore imprevisto nella creazione: {e}") from e

## 2. INTERFACCIA STREAMLIT (MODIFICATA CON TABS)

st.set_page_config(page_title="GA4 Channel Group Copier", layout="centered")
st.title("GA4 Channel Group Copier 🚀")
st.info("Copia un Custom Channel Group da una proprietà GA4 sorgente a una di destinazione.")

# Inizializzazione Session State
if 'templates' not in st.session_state:
    st.session_state.templates = []
if 'template_to_apply' not in st.session_state:
    st.session_state.template_to_apply = None

st.header("1. Scegli il Metodo")
tab_copy, tab_default = st.tabs(["Copia da una Proprietà GA4", "Usa Template di Default"])

# --- Tab 1: Copia da Proprietà ---
with tab_copy:
    st.subheader("Copia un template da una proprietà esistente")
    source_property_id = st.text_input("ID Proprietà GA4 Sorgente", key="source_id")

    if st.button("Carica Template dalla Sorgente"):
        if not source_property_id:
            st.warning("Per favore, inserisci un ID proprietà sorgente.")
        else:
            with st.spinner(f"Caricamento dei channel group da {source_property_id}..."):
                try:
                    creds = st.secrets["gcp_service_account"]
                    templates = list_channel_groups(source_property_id, creds)
                    st.session_state.templates = [t for t in templates if not t.get("systemDefined", False)]
                    if not st.session_state.templates:
                        st.warning("Nessun channel group personalizzato trovato.")
                    else:
                        st.success(f"{len(st.session_state.templates)} channel group personalizzati trovati!")
                except Exception as e:
                    st.error(str(e))

    if st.session_state.templates:
        template_options = [t.get('displayName', 'Senza Nome') for t in st.session_state.templates]
        selected_template_name = st.selectbox("Scegli un template da copiare:", template_options)
        
        # Salva il template scelto nello stato della sessione
        selected_obj = next((t for t in st.session_state.templates if t.get('displayName') == selected_template_name), None)
        st.session_state.template_to_apply = selected_obj
        st.info(f"Hai selezionato: **{selected_template_name}**. Vai alla sezione 'Applica' in fondo alla pagina.")

# --- Tab 2: Usa Template di Default ---
with tab_default:
    st.subheader("Usa il template predefinito con 24 regole")
    with st.expander("🔬 Clicca per vedere l'anteprima delle regole"):
        st.json(DEFAULT_CHANNEL_GROUP_DEFINITION["grouping_rule"])
    
    if st.button("Seleziona il Template di Default"):
        st.session_state.template_to_apply = DEFAULT_CHANNEL_GROUP_DEFINITION
        st.info("Hai selezionato il **Template di Default**. Vai alla sezione 'Applica' in fondo alla pagina.")

# --- Sezione 3: DESTINAZIONE (unificata) ---
if st.session_state.get('template_to_apply'):
    st.header("2. Applica il Template Selezionato")
    
    # Mostra un riepilogo del template scelto
    st.success(f"Template Selezionato: **{st.session_state.template_to_apply.get('displayName')}**")

    dest_property_id = st.text_input("ID Proprietà GA4 Destinazione", help="L'ID della proprietà su cui vuoi incollare il channel group.")

    if st.button("Applica Template alla Destinazione"):
        if not dest_property_id:
            st.warning("Per favore, inserisci un ID proprietà di destinazione.")
        else:
            with st.spinner(f"Applicazione del template a {dest_property_id}..."):
                try:
                    template = st.session_state.template_to_apply
                    # Prepara il payload PULITO per la creazione
                    payload_to_create = {
                        "display_name": template.get("displayName"),
                        "description": template.get("description", ""),
                        "grouping_rule": template.get("grouping_rule") or template.get("groupingRule", []) # Gestisce sia camelCase che snake_case
                    }
                    
                    creds = st.secrets["gcp_service_account"]
                    result = create_channel_group(dest_property_id, creds, payload_to_create)
                    st.success(result)
                    
                except KeyError:
                    st.error("🔴 Credenziali GCP non trovate negli secrets di Streamlit.")
                except Exception as e:
                    st.error(str(e))

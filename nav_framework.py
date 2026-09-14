"""Reference-design comparison, enabled only on Resilience Framework."""
import streamlit as st
import i18n


def header(logo):
    title = ("Observatoire de la résilience des paysages et populations d’Haïti"
             if i18n.get_lang() == "fr" else
             "Observatory for the Resilience of Haiti’s Landscapes and Populations")
    st.markdown('''<style>
    .stApp div[data-testid="stColumn"]:has(.framework-nav-brand){
      background:white!important;border-right:0!important;
    }
    .stApp div[data-testid="stColumn"]:has(.framework-nav-brand)::after{display:none!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand){background:white!important;padding-right:12px!important;}
    .framework-nav-brand{display:flex;align-items:center;gap:12px;margin:20px 8px 25px 4px;}
    .framework-nav-brand img{width:58px;height:auto;flex:none;}
    .framework-nav-brand span{border-left:1px solid #075348;padding-left:12px;
      font:400 14px/1.3 Georgia,serif;color:#064d40;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) .nav-famille{
      color:#537c74!important;font:700 11px/1.4 Arial,sans-serif!important;
      letter-spacing:2px!important;margin:23px 0 8px!important;padding-left:12px!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) div[data-testid="stButton"]>button{
      color:#075348!important;min-height:43px!important;padding:11px 12px!important;
      border-radius:7px!important;background:transparent!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) div[data-testid="stButton"]>button p{
      color:#075348!important;font:400 14px/1.4 Arial,sans-serif!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) div[data-testid="stButton"]>button::before{
      width:20px!important;height:20px!important;flex:0 0 20px!important;background-color:#075348!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) div[data-testid="stButton"]>button:hover{
      background:#f0f8f2!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) div[data-testid="stButton"]>button[kind="primary"]{
      background:linear-gradient(100deg,#e5f5e9,#eef8f1)!important;
      border-left:3px solid #009849!important;border-radius:5px 9px 9px 5px!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) div[data-testid="stButton"]>button[kind="primary"] p{font-weight:600!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) .nav-pied{
      margin-top:24px!important;padding:0 12px!important;border:0!important;}
    .stApp .st-key-zone_nav:has(.framework-nav-brand) .nav-devise{
      font:italic 13px/1.7 Arial,sans-serif!important;color:#62877e!important;text-align:left!important;}
    .framework-nav-landscape{margin:16px -12px 0 -14px;pointer-events:none;}
    .framework-nav-landscape img{width:100%;display:block;mask-image:linear-gradient(transparent,black 24%);}
    </style><div class="framework-nav-brand"><img alt="APRI" src="data:image/png;base64,'''
                + logo + '"><span>' + title + '</span></div>', unsafe_allow_html=True)


def landscape(image):
    st.markdown('<div class="framework-nav-landscape"><img alt="" src="data:image/png;base64,'
                + image + '"></div>', unsafe_allow_html=True)

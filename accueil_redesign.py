"""
Page d'accueil redessinée — APRI Landscape Resilience Observatory
==================================================================

Design moderne et épuré avec :
- Hero image en haut pleine largeur
- 3 étapes (Où? Quoi? Comment?) sous forme de cartes cliquables
- Infos géographiques à droite (map + stats)
- Navigation fluide et narrative
"""

import streamlit as st
import pandas as pd
from i18n import T
import map_render

# =====================================================================
# CSS personnalisé pour le design
# =====================================================================
CUSTOM_CSS = """
<style>
    /* Hero section */
    .hero-container {
        width: 100%;
        height: 280px;
        background: linear-gradient(135deg, #1a6b52 0%, #0f7f6b 100%);
        border-radius: 0;
        overflow: hidden;
        margin: -2rem -2.6rem 0;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-align: center;
    }
    
    .hero-content {
        z-index: 2;
        position: relative;
    }
    
    .hero-title {
        font-size: 36px;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 14.5px;
        font-weight: 500;
        color: rgba(255,255,255,0.85);
        margin-top: 8px;
    }
    
    /* Navigation steps */
    .steps-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 18px;
        margin: 32px 0;
    }
    
    .step-card {
        background: white;
        border: 1.5px solid #e3eaf3;
        border-radius: 16px;
        padding: 24px;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px rgba(16,23,40,0.05);
    }
    
    .step-card:hover {
        border-color: #1a6b52;
        box-shadow: 0 3px 8px rgba(26,107,82,0.15);
        transform: translateY(-3px);
    }
    
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: #1a6b52;
        color: white;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    .step-title {
        font-size: 16px;
        font-weight: 700;
        color: #101728;
        margin-bottom: 8px;
        letter-spacing: -0.01em;
    }
    
    .step-subtitle {
        font-size: 12px;
        font-weight: 600;
        color: #8a93a5;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 12px;
    }
    
    .step-content {
        font-size: 13.5px;
        color: #3c4761;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    
    .step-list {
        font-size: 12.5px;
        color: #6b7590;
        line-height: 1.8;
    }
    
    .step-list li {
        margin-bottom: 6px;
    }
    
    /* Info box à droite */
    .info-box {
        background: #f4f8fc;
        border: 1px solid #e3eaf3;
        border-left: 5px solid #1a6b52;
        border-radius: 12px;
        padding: 20px;
        margin-top: 32px;
    }
    
    .info-box-title {
        font-size: 13px;
        font-weight: 700;
        color: #8a93a5;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 12px;
    }
    
    .info-box-content {
        font-size: 13.5px;
        color: #3c4761;
        line-height: 1.7;
    }
    
    .stat-line {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(227,234,243,0.5);
    }
    
    .stat-label {
        font-weight: 500;
    }
    
    .stat-value {
        font-weight: 700;
        color: #1a6b52;
    }
    
    /* Two-column layout */
    .main-content {
        display: grid;
        grid-template-columns: 1.8fr 1.2fr;
        gap: 24px;
        align-items: start;
    }
    
    @media (max-width: 1024px) {
        .main-content {
            grid-template-columns: 1fr;
        }
        .steps-container {
            grid-template-columns: 1fr;
        }
    }
    
    /* CTA Button */
    .cta-button {
        display: inline-block;
        padding: 11px 20px;
        background: #1a6b52;
        color: white;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
        margin-top: 12px;
    }
    
    .cta-button:hover {
        background: #0f7f6b;
        transform: translateY(-1px);
    }
</style>
"""

def render():
    """Page d'accueil complète ressemblant à la référence."""
    
    # Injecter le CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # =====================================================================
    # HERO SECTION
    # =====================================================================
    st.markdown("""
    <div class="hero-container">
        <div class="hero-content">
            <h1 class="hero-title">Household Resilience Survey 2024</h1>
            <p class="hero-subtitle">Landscape resilience observatory — Sud and Grand'Anse, Haiti</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("")  # Spacing
    
    # =====================================================================
    # MAIN CONTENT (2 colonnes)
    # =====================================================================
    col_left, col_right = st.columns([1.8, 1.2], gap="large")
    
    with col_left:
        # ===== STEP 1 : THE STUDY AREA =====
        st.markdown("""
        <div class="step-card" onclick="document.querySelector('[data-testid=\\"stButton\\"] button:nth-of-type(1)').click()">
            <div class="step-number">1</div>
            <div class="step-subtitle">Where?</div>
            <div class="step-title">The study area</div>
            <div class="step-content">
                Discover the geographical context of the survey in Haiti's South and Grand'Anse departments.
            </div>
            <ul class="step-list">
                <li>✓ Two pilot areas: Grand'Anse and Sud</li>
                <li>✓ 10 communal sections surveyed</li>
                <li>✓ 1,211 households interviewed</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== STEP 2 : METHODOLOGY =====
        st.markdown("""
        <div class="step-card" onclick="document.querySelector('[data-testid=\\"stButton\\"] button:nth-of-type(2)').click()">
            <div class="step-number">2</div>
            <div class="step-subtitle">What was measured?</div>
            <div class="step-title">Methodology</div>
            <div class="step-content">
                Learn about the resilience framework and how indicators were calculated across 6 dimensions.
            </div>
            <ul class="step-list">
                <li>✓ 6 dimensions of resilience</li>
                <li>✓ Survey + satellite + registries</li>
                <li>✓ Scores out of 10</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # ===== STEP 3 : RESULTS =====
        st.markdown("""
        <div class="step-card" onclick="document.querySelector('[data-testid=\\"stButton\\"] button:nth-of-type(3)').click()">
            <div class="step-number">3</div>
            <div class="step-subtitle">How resilient?</div>
            <div class="step-title">Results Analysis</div>
            <div class="step-content">
                Explore dimension by dimension, filtered by your chosen group or territory.
            </div>
            <ul class="step-list">
                <li>✓ Scores by section and group</li>
                <li>✓ Interactive filters</li>
                <li>✓ Detailed indicators</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        # ===== GEOGRAPHICAL INFO =====
        st.markdown("""
        <div class="info-box">
            <div class="info-box-title">The surveyed area</div>
            <div class="info-box-content">
                <p>The study covers <strong>two pilot areas in the far south-west</strong> of Haiti, 
                representing diverse agro-ecological zones and demographic profiles.</p>
                
                <div class="stat-line">
                    <span class="stat-label">Households</span>
                    <span class="stat-value">1,211</span>
                </div>
                <div class="stat-line">
                    <span class="stat-label">Communal sections</span>
                    <span class="stat-value">10</span>
                </div>
                <div class="stat-line">
                    <span class="stat-label">Departments</span>
                    <span class="stat-value">2</span>
                </div>
                <div class="stat-line">
                    <span class="stat-label">Landscapes</span>
                    <span class="stat-value">2</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Map intégrée
        try:
            # Créer une simple carte des sections
            valeurs = {
                "Anse à Drick": 5.5,
                "Barbois": 5.2,
                "Dumont": 5.8,
                "Débouchette": 5.1,
                "Mouline": 5.4,
                "Quentin": 5.3,
                "Beaulieu": 5.6,
                "Blactote": 5.2,
                "Dalmette": 5.7,
                "Trichet": 5.3
            }
            
            seuils = map_render.nice_thresholds([v for v in valeurs.values()])
            svg, _, _ = map_render.render_map_svg(
                valeurs,
                {s: 1 for s in valeurs.keys()},
                seuils,
                height=320,
                polarity="eleve_bon",
                unite="",
                infos={s: "Survey location" for s in valeurs.keys()}
            )
            
            st.markdown("""
            <div style="margin-top: 20px; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 2px rgba(16,23,40,.05);">
            """, unsafe_allow_html=True)
            
            st.components.v1.html(svg, height=340, scrolling=False)
            
            st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.info("📍 Map unavailable")
    
    # =====================================================================
    # HIDDEN BUTTONS (pour navigation)
    # =====================================================================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Go to The Territory", use_container_width=True, key="btn_territory"):
            st.session_state["app_mode"] = "accueil"
            st.rerun()
    
    with col2:
        if st.button("View Resilience Framework", use_container_width=True, key="btn_framework"):
            st.session_state["app_mode"] = "methodologie"
            st.rerun()
    
    with col3:
        if st.button("Start Analysis", use_container_width=True, key="btn_results"):
            st.session_state["app_mode"] = "dimensions"
            st.rerun()
    
    # =====================================================================
    # DIVIDER & CONTEXTE
    # =====================================================================
    st.divider()
    
    # Section additionnelle : Ce qu'on peut faire
    st.markdown("""
    ### 🎯 What you can explore
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 20px;">
        <div style="background: #f4f8fc; padding: 16px; border-radius: 10px; border-left: 4px solid #1a6b52;">
            <strong>📊 By Dimension</strong><br>
            <span style="font-size: 12px; color: #6b7590;">Physical, Economic, Social...</span>
        </div>
        <div style="background: #f4f8fc; padding: 16px; border-radius: 10px; border-left: 4px solid #1a6b52;">
            <strong>🗺️ By Territory</strong><br>
            <span style="font-size: 12px; color: #6b7590;">Compare 10 sections</span>
        </div>
        <div style="background: #f4f8fc; padding: 16px; border-radius: 10px; border-left: 4px solid #1a6b52;">
            <strong>👥 By Group</strong><br>
            <span style="font-size: 12px; color: #6b7590;">Gender, age, income...</span>
        </div>
        <div style="background: #f4f8fc; padding: 16px; border-radius: 10px; border-left: 4px solid #1a6b52;">
            <strong>📈 All Questions</strong><br>
            <span style="font-size: 12px; color: #6b7590;">1,000+ raw survey items</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Footer info
    st.markdown("""
    <div style="text-align: center; color: #8a93a5; font-size: 12px; margin-top: 30px;">
        <p>
            <strong>Data source:</strong> Household survey 2024 | 
            <strong>Built by:</strong> APRI & UNEP | 
            <strong>Updated:</strong> 2024-08-27
        </p>
    </div>
    """, unsafe_allow_html=True)

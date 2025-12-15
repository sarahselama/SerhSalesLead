"""
OOH Sales Leads Dashboard - Brand-Grouped View
AI-Enhanced Instagram Campaign Extrac

tion with feedback system
"""
import streamlit as st
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from brand_validator import normalize_brand_name

st.set_page_config(
    page_title="OOH Sales Leads - InsiteOOH",
    page_icon="🎯",
    layout="wide"
)

# Header
st.title("🎯 OOH Advertising Sales Leads")
st.markdown("*AI-extracted brand campaigns from @insiteooh_ae Instagram - **Brand-Grouped View***")

# Load extracted leads from CSV
csv_file = Path("ooh_leads_live.csv")

if not csv_file.exists():
    st.warning("⚠️ No leads extracted yet. Run the AI extraction first:")
    st.code("python extract_leads.py")
    st.info("This will analyze Instagram posts and extract brand information using AI.")
    st.stop()

# Load CSV
df = pd.read_csv(csv_file)

if len(df) == 0:
    st.warning("No leads found in ooh_leads_live.csv. AI extraction may have failed.")
    st.info("Check if Fisher AI API is configured correctly in .env file")
    st.stop()

# Convert DataFrame to list of dicts
leads = df.to_dict('records')

# Map CSV columns and normalize brands
for lead in leads:
    if 'Brand Name' in lead:
        lead['brand_name'] = normalize_brand_name(lead['Brand Name'])
    if 'Industry' in lead:
        lead['industry'] = lead['Industry']
    if 'Location' in lead:
        lead['location'] = lead['Location']
    if 'Post Date' in lead:
        lead['post_date'] = lead['Post Date']
    if 'Campaign Type' in lead:
        lead['campaign_type'] = lead['Campaign Type']
    if 'Campaign Message' in lead:
        lead['campaign_message'] = lead['Campaign Message']
    if 'Brand Handle' in lead:
        lead['brand_handle'] = lead['Brand Handle']
    if 'OOH Formats' in lead:
        lead['ooh_formats'] = lead['OOH Formats']
    
    # Check if UAE location
    loc = str(lead.get('location', '')).strip()
    lead['is_uae'] = any(city in loc.lower() for city in ['uae', 'dubai', 'sharjah', 'abu dhabi', 'ajman', 'ras al khaimah', 'fujairah', 'umm al quwain'])

# Group campaigns by brand
brands_dict = defaultdict(list)
for lead in leads:
    brand_name = lead.get('brand_name', 'Unknown')
    brands_dict[brand_name].append(lead)

# Sort brands by number of campaigns (descending)
sorted_brands = sorted(brands_dict.items(), key=lambda x: len(x[1]), reverse=True)

# Stats
total_brands = len(brands_dict)
total_campaigns = len(leads)
industries = list(set([l.get('industry', 'Unknown') for l in leads if l.get('industry')]))

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Brands", total_brands)
with col2:
    st.metric("Total Campaigns", total_campaigns)
with col3:
    avg_campaigns = total_campaigns / total_brands if total_brands > 0 else 0
    st.metric("Avg Campaigns/Brand", f"{avg_campaigns:.1f}")
with col4:
    st.metric("Industries", len(industries))

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["🏢 Brand Groups", "📊 Analysis", "💾 Export"])

with tab1:
    st.subheader("Brands & Their Campaigns")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_uae = st.checkbox("UAE Only", value=False)
    
    with col2:
        if len(industries) > 0:
            selected_industry = st.selectbox("Industry", ["All"] + sorted(industries))
        else:
            selected_industry = "All"
    
    with col3:
        search = st.text_input("Search brands")
    
    with col4:
        min_campaigns = st.slider("Min campaigns per brand", 1, 10, 1)
    
    # Filter brands
    filtered_brands = sorted_brands
    
    if filter_uae:
        filtered_brands = [
            (brand, campaigns) for brand, campaigns in filtered_brands
            if any(c.get('is_uae', False) for c in campaigns)
        ]
    
    if selected_industry != "All":
        filtered_brands = [
            (brand, campaigns) for brand, campaigns in filtered_brands
            if any(c.get('industry') == selected_industry for c in campaigns)
        ]
    
    if search:
        search_lower = search.lower()
        filtered_brands = [
            (brand, campaigns) for brand, campaigns in filtered_brands
            if search_lower in brand.lower()
        ]
    
    if min_campaigns > 1:
        filtered_brands = [
            (brand, campaigns) for brand, campaigns in filtered_brands
            if len(campaigns) >= min_campaigns
        ]
    
    total_filtered_campaigns = sum(len(campaigns) for _, campaigns in filtered_brands)
    
    st.markdown(f"**Showing {len(filtered_brands)} brands with {total_filtered_campaigns} campaigns**")
    
    if len(filtered_brands) == 0:
        st.info("No brands match your filters")
    else:
        # Display brand-grouped cards
        for brand_name, campaigns in filtered_brands:
            # Get brand metadata from first campaign
            first_campaign = campaigns[0]
            industry = first_campaign.get('industry', 'Unknown')
            brand_handle = first_campaign.get('brand_handle', '')
            
            # Create brand card
            with st.expander(
                f"🏢 **{brand_name}** ({len(campaigns)} campaign{'' if len(campaigns) == 1 else 's'}) - {industry}",
                expanded=False
            ):
                # Brand header
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**Handle:** {brand_handle}")
                    st.markdown(f"**Industry:** {industry}")
                with col2:
                    st.metric("Total Campaigns", len(campaigns))
                with col3:
                    # Get unique locations
                    locations = set(c.get('location', 'Unknown') for c in campaigns)
                    st.metric("Locations", len(locations))
                
                st.divider()
                
                # List all campaigns chronologically
                sorted_campaigns = sorted(campaigns, key=lambda x: x.get('post_date', ''), reverse=True)
                
                st.markdown("### Campaigns:")
                for i, campaign in enumerate(sorted_campaigns, 1):
                    campaign_date = campaign.get('post_date', 'Unknown')
                    campaign_type = campaign.get('campaign_type', 'Unknown')
                    campaign_location = campaign.get('location', 'Unknown')
                    campaign_message = campaign.get('campaign_message', 'No message')
                    ooh_formats = campaign.get('ooh_formats', 'Unknown')
                    
                    # Safely handle campaign message (could be NaN/float)
                    if campaign_message is None or (isinstance(campaign_message, float) and pd.isna(campaign_message)):
                        campaign_message = 'No description available'
                    else:
                        campaign_message = str(campaign_message)
                    
                    # Campaign row
                    cols = st.columns([1, 2, 2, 1, 1])
                    with cols[0]:
                        st.markdown(f"**{i}. {campaign_date}**")
                    with cols[1]:
                        st.markdown(f"*{campaign_type}*")
                    with cols[2]:
                        st.markdown(f"📍 {campaign_location}")
                    with cols[3]:
                        st.markdown(f"`{ooh_formats}`")
                    with cols[4]:
                        # Feedback button
                        if st.button("⚠️ Report", key=f"report_{brand_name}_{i}"):
                            st.session_state[f'feedback_{brand_name}_{i}'] = True
                    
                    # Show message below
                    st.markdown(f"> {campaign_message[:200]}{'...' if len(campaign_message) > 200 else ''}")
                    
                    # Feedback form (if triggered)
                    if st.session_state.get(f'feedback_{brand_name}_{i}', False):
                        with st.form(f"feedback_form_{brand_name}_{i}"):
                            st.markdown("**Report an Issue:**")
                            issue_type = st.selectbox(
                                "Issue Type",
                                ["Wrong Brand", "Wrong Industry", "Wrong Location", "Publisher (not a brand)", "Other"],
                                key=f"issue_type_{brand_name}_{i}"
                            )
                            correction = st.text_input("Correct Value", key=f"correction_{brand_name}_{i}")
                            notes = st.text_area("Notes (optional)", key=f"notes_{brand_name}_{i}")
                            
                            if st.form_submit_button("Submit Feedback"):
                                # Save feedback to JSON
                                feedback_file = Path("ai_feedback.json")
                                feedback_data = []
                                
                                if feedback_file.exists():
                                    with open(feedback_file, 'r') as f:
                                        feedback_data = json.load(f)
                                
                                feedback_data.append({
                                    "timestamp": pd.Timestamp.now().isoformat(),
                                    "brand_name": brand_name,
                                    "campaign_date": campaign_date,
                                    "issue_type": issue_type,
                                    "extracted_value": brand_name if "Brand" in issue_type else campaign.get('industry', ''),
                                    "correct_value": correction,
                                    "notes": notes
                                })
                                
                                with open(feedback_file, 'w') as f:
                                    json.dump(feedback_data, f, indent=2)
                                
                                st.success("✅ Feedback submitted! This will help improve AI extraction.")
                                st.session_state[f'feedback_{brand_name}_{i}'] = False
                                st.rerun()
                    
                    st.markdown("---")

with tab2:
    st.subheader("Campaign Analysis")
    
    # Top brands by campaign count
    st.markdown("### 🏆 Top Brands by Campaign Count")
    top_brands_df = pd.DataFrame(
        [(brand, len(campaigns)) for brand, campaigns in sorted_brands[:10]],
        columns=['Brand', 'Campaigns']
    )
    st.bar_chart(top_brands_df.set_index('Brand'))
    
    # Industry breakdown
    st.markdown("### 📊 Campaigns by Industry")
    industry_counts = defaultdict(int)
    for lead in leads:
        industry_counts[lead.get('industry', 'Unknown')] += 1
    
    industry_df = pd.DataFrame(
        sorted(industry_counts.items(), key=lambda x: x[1], reverse=True),
        columns=['Industry', 'Campaigns']
    )
    st.bar_chart(industry_df.set_index('Industry'))
    
    # Location breakdown
    st.markdown("### 📍 Campaigns by Location")
    location_counts = defaultdict(int)
    for lead in leads:
        location_counts[lead.get('location', 'Unknown')] += 1
    
    location_df = pd.DataFrame(
        sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:15],
        columns=['Location', 'Campaigns']
    )
    st.bar_chart(location_df.set_index('Location'))

with tab3:
    st.subheader("Export Data")
    
    st.markdown("### 📊 Sales-Ready Export")
    st.info("Export data optimized for sales team prospecting and CRM import")
    
    # Create sales-friendly DataFrame
    sales_df = df.copy()
    
    # Rename columns for sales clarity
    sales_df = sales_df.rename(columns={
        'Post Date': 'Campaign Date',
        'Brand Name': 'Company Name',
        'Brand Handle': 'Instagram Handle',
        'Industry': 'Industry Sector',
        'Campaign Type': 'Campaign Category',
        'Campaign Message': 'Campaign Description',
        'OOH Formats': 'Advertising Formats',
        'Location': 'Target Market',
        'Brand Confidence': 'Data Quality (Brand)',
        'Industry Confidence': 'Data Quality (Industry)'
    })
    
    # Reorder columns for sales priority
    column_order = [
        'Company Name',
        'Industry Sector',
        'Target Market',
        'Campaign Date',
        'Campaign Category',
        'Advertising Formats',
        'Campaign Description',
        'Instagram Handle',
        'Data Quality (Brand)',
        'Data Quality (Industry)'
    ]
    
    sales_df = sales_df[column_order]
    
    # Sort by date (newest first) and then by company name
    sales_df = sales_df.sort_values(['Campaign Date', 'Company Name'], ascending=[False, True])
    
    # Show preview
    st.markdown("**Preview (first 10 rows):**")
    st.dataframe(sales_df.head(10), use_container_width=True)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV export
        csv_data = sales_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Sales Report (CSV)",
            data=csv_data,
            file_name=f"ooh_sales_leads_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download as CSV for Excel/CRM import"
        )
    
    with col2:
        # Excel-formatted CSV (with UTF-8 BOM for Excel compatibility)
        csv_excel = '\ufeff' + sales_df.to_csv(index=False)
        st.download_button(
            label="📥 Download for Excel (CSV)",
            data=csv_excel.encode('utf-8'),
            file_name=f"ooh_sales_leads_excel_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Optimized for Microsoft Excel"
        )
    
    # Summary stats for sales team
    st.divider()
    st.markdown("### 📈 Lead Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Companies", sales_df['Company Name'].nunique())
    with col2:
        st.metric("Total Campaigns", len(sales_df))
    with col3:
        high_quality = len(sales_df[sales_df['Data Quality (Brand)'] == 'HIGH'])
        st.metric("High Quality Leads", high_quality)
    with col4:
        recent = len(sales_df[pd.to_datetime(sales_df['Campaign Date']) >= pd.Timestamp.now() - pd.Timedelta(days=30)])
        st.metric("Campaigns (Last 30d)", recent)
    
    # Show feedback stats if any
    feedback_file = Path("ai_feedback.json")
    if feedback_file.exists():
        with open(feedback_file, 'r') as f:
            feedback_data = json.load(f)
        
        if len(feedback_data) > 0:
            st.divider()
            st.markdown("### 📝 Quality Feedback Log")
            st.caption(f"{len(feedback_data)} corrections submitted to improve AI accuracy")
            
            feedback_df = pd.DataFrame(feedback_data)
            st.dataframe(feedback_df[['timestamp', 'brand_name', 'issue_type', 'correct_value']], use_container_width=True)
            
            # Download feedback
            feedback_csv = feedback_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Feedback Log",
                data=feedback_csv,
                file_name="ai_feedback_log.csv",
                mime="text/csv"
            )

# Footer
st.divider()
st.caption("🤖 Powered by Fisher AI | Data extracted from @insiteooh_ae Instagram posts")

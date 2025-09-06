#!/usr/bin/env python3
"""
Streamlit Cloud Deployment Helper
================================

This script helps deploy the marketing dashboard to Streamlit Cloud.
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

def create_streamlit_config():
    """Create Streamlit configuration for cloud deployment."""
    
    config_dir = Path(".streamlit")
    config_dir.mkdir(exist_ok=True)
    
    config = {
        "server": {
            "port": 8501,
            "address": "0.0.0.0",
            "enableCORS": False,
            "enableXsrfProtection": False,
            "maxUploadSize": 200
        },
        "browser": {
            "gatherUsageStats": False
        },
        "theme": {
            "primaryColor": "#1f77b4",
            "backgroundColor": "#ffffff",
            "secondaryBackgroundColor": "#f0f2f6",
            "textColor": "#262730"
        }
    }
    
    config_file = config_dir / "config.toml"
    with open(config_file, 'w') as f:
        f.write("# Streamlit Cloud Configuration\n\n")
        for section, settings in config.items():
            f.write(f"[{section}]\n")
            for key, value in settings.items():
                if isinstance(value, bool):
                    f.write(f"{key} = {str(value).lower()}\n")
                elif isinstance(value, int):
                    f.write(f"{key} = {value}\n")
                else:
                    f.write(f'{key} = "{value}"\n')
            f.write("\n")
    
    print(f"✅ Created Streamlit config: {config_file}")

def create_requirements_file():
    """Create requirements.txt for deployment."""
    
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "plotly>=5.15.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "google-ads>=22.0.0",
        "rich>=13.0.0"
    ]
    
    with open("requirements.txt", 'w') as f:
        f.write("# Dashboard Dependencies\n")
        f.write("# Generated for Streamlit Cloud deployment\n\n")
        for req in requirements:
            f.write(f"{req}\n")
    
    print("✅ Created requirements.txt")

def create_packages_file():
    """Create packages.txt for system dependencies."""
    
    packages = [
        "python3-dev",
        "build-essential"
    ]
    
    with open("packages.txt", 'w') as f:
        f.write("# System packages for Streamlit Cloud\n")
        for pkg in packages:
            f.write(f"{pkg}\n")
    
    print("✅ Created packages.txt")

def check_environment_variables():
    """Check if required environment variables are set."""
    
    required_vars = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID", 
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nThese will need to be set in Streamlit Cloud dashboard.")
    else:
        print("✅ All required environment variables are set")
    
    return len(missing_vars) == 0

def create_deployment_guide():
    """Create deployment guide."""
    
    guide = """# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy Steps

1. **Go to Streamlit Cloud**
   - Visit: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Repository: `ELevine-RE/google-ads-analysis`
   - Branch: `main`
   - Main file path: `dashboard.py`

3. **Configure Environment Variables**
   In the Streamlit Cloud dashboard, add these secrets:
   - `GOOGLE_ADS_DEVELOPER_TOKEN`
   - `GOOGLE_ADS_CLIENT_ID`
   - `GOOGLE_ADS_CLIENT_SECRET`
   - `GOOGLE_ADS_REFRESH_TOKEN`
   - `GOOGLE_ADS_LOGIN_CUSTOMER_ID`

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your dashboard will be live!

## Dashboard URL
Your dashboard will be available at:
`https://share.streamlit.io/ELevine-RE/google-ads-analysis/main/dashboard.py`

## Troubleshooting

### Build Fails
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility

### No Data Showing
- Verify environment variables are set correctly
- Check Google Ads API credentials
- Ensure campaigns are active

### Charts Not Loading
- Check internet connection
- Verify Plotly installation
- Clear browser cache

## Support
If you encounter issues:
1. Check the build logs in Streamlit Cloud
2. Verify all environment variables are set
3. Test locally first with `streamlit run dashboard.py`
"""
    
    with open("STREAMLIT_DEPLOYMENT_GUIDE.md", 'w') as f:
        f.write(guide)
    
    print("✅ Created deployment guide: STREAMLIT_DEPLOYMENT_GUIDE.md")

def main():
    """Main deployment setup function."""
    
    print("🚀 Setting up Streamlit Cloud deployment...")
    print("=" * 50)
    
    # Create necessary files
    create_streamlit_config()
    create_requirements_file()
    create_packages_file()
    create_deployment_guide()
    
    # Check environment
    print("\n🔍 Environment Check:")
    check_environment_variables()
    
    print("\n" + "=" * 50)
    print("✅ Deployment setup complete!")
    print("\n📋 Next Steps:")
    print("1. Go to https://share.streamlit.io/")
    print("2. Sign in with GitHub")
    print("3. Create new app")
    print("4. Select this repository")
    print("5. Set main file: dashboard.py")
    print("6. Add environment variables")
    print("7. Deploy!")
    print("\n📖 See STREAMLIT_DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == "__main__":
    main()

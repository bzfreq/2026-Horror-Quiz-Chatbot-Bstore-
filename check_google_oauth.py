#!/usr/bin/env python3
"""
Google OAuth Configuration Checker
This script helps diagnose Google Sign-In issues
"""

import requests
import sys

# Your current Client ID
CLIENT_ID = "383630092112-5vqj924hq2n44tjk1gpb3bisokfab50m.apps.googleusercontent.com"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_client_id_validity():
    """Check if the Client ID is valid by querying Google's tokeninfo endpoint"""
    print_header("Checking Client ID Validity")
    
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?client_id={CLIENT_ID}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print_success("Client ID is valid and active!")
            return True
        elif response.status_code == 400:
            print_error("Client ID is invalid or has been revoked")
            print_info("You need to create a new Client ID in Google Cloud Console")
            return False
        else:
            print_warning(f"Unexpected response: {response.status_code}")
            print_info("Response: " + response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Network error: {e}")
        print_info("Check your internet connection")
        return False

def check_requirements():
    """Check if required Python packages are installed"""
    print_header("Checking Python Requirements")
    
    try:
        import flask
        print_success(f"Flask is installed (version {flask.__version__})")
    except ImportError:
        print_error("Flask is not installed")
        print_info("Run: pip install flask")
    
    try:
        import flask_cors
        print_success("Flask-CORS is installed")
    except ImportError:
        print_error("Flask-CORS is not installed")
        print_info("Run: pip install flask-cors")
    
    print_success("requests is installed")

def check_server_running():
    """Check if the Flask server is running"""
    print_header("Checking Flask Server")
    
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        if response.status_code == 200:
            print_success("Flask server is running on http://localhost:5000")
            return True
        else:
            print_warning(f"Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Flask server is NOT running")
        print_info("Start the server with: python horror.py")
        return False
    except requests.exceptions.Timeout:
        print_error("Server connection timed out")
        return False

def print_configuration_guide():
    """Print step-by-step configuration instructions"""
    print_header("Google Cloud Console Configuration")
    
    print(f"{Colors.BOLD}Step 1: Go to Google Cloud Console{Colors.END}")
    print("   URL: https://console.cloud.google.com/")
    print()
    
    print(f"{Colors.BOLD}Step 2: Select or Create a Project{Colors.END}")
    print("   Click the project dropdown at the top")
    print()
    
    print(f"{Colors.BOLD}Step 3: Configure OAuth Consent Screen{Colors.END}")
    print("   Go to: APIs & Services → OAuth consent screen")
    print("   - Choose: External")
    print("   - App name: Horror Oracle")
    print("   - Add your email as test user")
    print()
    
    print(f"{Colors.BOLD}Step 4: Create OAuth Client ID{Colors.END}")
    print("   Go to: APIs & Services → Credentials")
    print("   - Click: + CREATE CREDENTIALS → OAuth client ID")
    print("   - Application type: Web application")
    print()
    
    print(f"{Colors.BOLD}Step 5: Add Authorized JavaScript Origins{Colors.END}")
    print(f"   {Colors.GREEN}Add these EXACT URLs:{Colors.END}")
    print("   • http://localhost:5000")
    print("   • http://127.0.0.1:5000")
    print("   • http://localhost")
    print()
    
    print(f"{Colors.BOLD}Step 6: Copy Your Client ID{Colors.END}")
    print("   Replace the Client ID in index.html (line 1742)")
    print()

def print_troubleshooting():
    """Print common troubleshooting tips"""
    print_header("Common Issues & Solutions")
    
    issues = [
        ("Button doesn't appear", "Check browser console for errors. Ensure Google script loads."),
        ("'invalid_client' error", "Your Client ID is wrong or revoked. Create a new one."),
        ("'redirect_uri_mismatch'", "Add http://localhost:5000 to authorized origins."),
        ("'access_denied' error", "Add your email as a test user in OAuth consent screen."),
        ("'popup_closed_by_user'", "User closed the popup - just try again."),
        ("Console: 'idpiframe...'", "Origin not authorized. Add localhost:5000 to origins."),
    ]
    
    for issue, solution in issues:
        print(f"\n{Colors.YELLOW}Problem: {issue}{Colors.END}")
        print(f"   {Colors.GREEN}Solution: {solution}{Colors.END}")

def main():
    print_header("🩸 Horror Oracle - Google Auth Diagnostic Tool 🩸")
    
    print_info(f"Current Client ID: {CLIENT_ID}")
    print()
    
    # Run checks
    checks_passed = 0
    total_checks = 3
    
    if check_client_id_validity():
        checks_passed += 1
    
    check_requirements()
    
    if check_server_running():
        checks_passed += 1
        print_success("You can test at: http://localhost:5000/test-google-signin.html")
    
    # Print summary
    print_header("Summary")
    print(f"Checks passed: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print_success("All checks passed! Your setup should be working.")
        print_info("If you still have issues, check the browser console.")
    else:
        print_warning("Some checks failed. Follow the guide below.")
        print_configuration_guide()
    
    print_troubleshooting()
    
    print_header("Next Steps")
    print("1. Read GOOGLE_AUTH_SETUP.md for detailed instructions")
    print("2. Test with: http://localhost:5000/test-google-signin.html")
    print("3. Check browser console (F12) for error messages")
    print("4. Verify your Google Cloud Console settings")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Script interrupted by user{Colors.END}")
        sys.exit(0)


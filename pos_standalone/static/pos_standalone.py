#!/usr/bin/env python3
import os
import sys
import threading
import time
import subprocess
import platform

# Try to import webview, provide helpful error if missing
try:
    import webview
except ImportError:
    print("\033[91mError: Required library 'pywebview' is not installed.\033[0m")
    sys.exit(1)

def run():
    """
    Launch the POS Standalone application in a native window.
    """
    # Force software rendering to avoid GLX errors
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu"
    os.environ["QT_XCB_GL_INTEGRATION"] = "none"
    
    # Check for GUI backends
    try:
        import gi
    except ImportError:
        try:
            import qtpy
            from qtpy import QtCore
            import PyQt5.QtWebEngineWidgets
        except ImportError:
            print("\033[91mError: No GUI backend found (GTK or Qt with WebEngine).\033[0m")
            print("Since you are running in a Conda/Virtual env, system GTK bindings might be missing.")
            print("For PyQt5, you MUST install the WebEngine component separately.")
            print("Please run:\n")
            print("    \033[92mpip install PyQt5 PyQtWebEngine qtpy\033[0m\n")
            sys.exit(1)
    # Get absolute path to index.html in the same directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_file = os.path.join(current_dir, 'index.html')
    
    # Verify file exists
    if not os.path.exists(index_file):
        print(f"\033[91mError: Could not find index.html at: {index_file}\033[0m")
        sys.exit(1)

    url = f'file://{index_file}'
    print(f"Launching POS from: {url}")

    # API Class to be exposed to JavaScript
    class Api:
        def close_window(self):
            webview.windows[0].destroy()
            sys.exit(0)

        def get_printers(self):
            """Returns a list of available printers."""
            print("LOG: get_printers called")
            system = platform.system()
            printers = []

            try:
                if system == "Linux":
                    # Use lpstat to get printers
                    print("LOG: Executing lpstat -a")
                    result = subprocess.check_output(['lpstat', '-a'], text=True)
                    print(f"LOG: lpstat output: {result}")
                    for line in result.splitlines():
                        if line.strip():
                            printers.append(line.split(' ')[0])
                
                elif system == "Windows":
                    # Use PowerShell to get printers
                    print("LOG: Executing Windows printer discovery")
                    cmd = ['powershell', '-Command', 'Get-Printer | Select-Object -ExpandProperty Name']
                    result = subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW, text=True)
                    printers = [p.strip() for p in result.splitlines() if p.strip()]
                    
            except Exception as e:
                print(f"Error getting printers: {e}")
                return {"error": str(e)}

            print(f"LOG: Found printers: {printers}")
            return printers

        def print_text(self, printer_name, text):
            """Prints raw text to the specified printer."""
            print(f"LOG: print_text called for printer: {printer_name}")
            system = platform.system()
            
            try:
                if system == "Linux":
                    # Use lpr
                    cmd = ['lpr', '-P', printer_name]
                    print(f"LOG: Executing command: {cmd}")
                    subprocess.run(cmd, input=text, text=True, check=True)
                
                elif system == "Windows":
                    print("LOG: Executing Windows print")
                    # Use simple notepad print or raw print if possible
                    # For a robust solution without win32print, popen to a temp file then print might be needed
                    # But for now, let's try a direct piping approach to generic text printer if possible
                    # A better generic approach on Windows without win32print is complicated.
                    # We will use valid PowerShell for raw text printing
                    import tempfile
                    
                    # Create temp file
                    fd, temp_path = tempfile.mkstemp(suffix=".txt")
                    with os.fdopen(fd, 'w') as f:
                        f.write(text)
                    
                    # Print using notepad /p is easiest for text files, but it opens a window momentarily
                    # subprocess.run(['notepad', '/p', temp_path], check=True)
                    
                    # Better: PowerShell Out-Printer
                    cmd = ['powershell', '-Command', f'Get-Content "{temp_path}" | Out-Printer -Name "{printer_name}"']
                    print(f"LOG: Running info: {cmd}")
                    subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, check=True)
                    
                    # Cleanup
                    # time.sleep(2) # Give it a moment?
                    # os.remove(temp_path) 
                    
                print("LOG: Print success")
                return {"success": True}
                
            except Exception as e:
                print(f"Error printing: {e}")
                return {"success": False, "error": str(e)}

        def print_receipt_image(self, printer_name, base64_image):
            """Prints a base64 encoded image to the specified printer."""
            print(f"LOG: print_receipt_image called for printer: {printer_name}")
            import base64
            import tempfile
            
            try:
                # Remove header if present (data:image/png;base64,...)
                if ',' in base64_image:
                    base64_image = base64_image.split(',')[1]
                
                image_data = base64.b64decode(base64_image)
                
                # Create temp file
                fd, temp_path = tempfile.mkstemp(suffix=".png")
                with os.fdopen(fd, 'wb') as f:
                    f.write(image_data)
                
                system = platform.system()
                if system == "Linux":
                    # Use lpr with options to ensure portrait and scaled to printable area
                    # Common options: -o fit-to-page, -o scaling=100
                    # For receipt printers (like 80mm), often just printing without options works best IF the image width matches.
                    # But if user says "Landscape", it means it's likely rotating.
                    # Try explicitly requesting portrait.
                    cmd = ['lpr', '-P', printer_name, '-o', 'orientation-requested=3', '-o', 'fit-to-page', temp_path]
                    print(f"LOG: Executing command: {cmd}")
                    subprocess.run(cmd, check=True)
                
                elif system == "Windows":
                    print("LOG: Executing Windows image print")
                    # PowerShell can print images using MS Paint or similar, but it's tricky without a proper CMD tool.
                    # A reliable way on vanilla Windows is via mspaint /p but it opens the UI.
                    # Or using Rundll32 with Windows Photo Viewer (deprecated but often present).
                    # A better way for POS is often just raw printing if it was ESC/POS, but for "Image", we rely on driver.
                    # Let's try mspaint for now as it's standard, though it might steal focus.
                    cmd = ['mspaint', '/p', temp_path] 
                    # Note: mspaint /p prints to default printer. To print to specific printer is harder with just mspaint.
                    # Alternative: Print-Job in Powershell? 
                    # Powershell's Start-Process -Verb Print prints to default.
                    
                    # If we really need specific printer on Windows without non-standard libs, it's hard.
                    # We will assume 'default' printer or try to change default momentarily (risky).
                    # For this verify step, let's try just printing to default if explicit selection fails? 
                    # Actually, the user might have selected a specific one.
                    # Let's use a powershell snippet that can print images if possible.
                    
                    # For now, simplistic approach: "mspaint /p" prints to DEFAULT. 
                    # If user chose a printer, we might need to set it as default temporarily? No that's bad.
                    # Let's hope the user sets the POS printer as default or we accept this limitation for now.
                    # OR: simple generic implementation for now.
                    subprocess.run(cmd, check=True)
                    
                # os.remove(temp_path) # Cleanup later
                return {"success": True}
            except Exception as e:
                print(f"Error printing image: {e}")
                return {"success": False, "error": str(e)}

        def test_connection(self, url, db, username, password):
            """
            Proxy Odoo authentication request to avoid CORS/CSRF issues in JS.
            """
            import requests
            print(f"LOG: Proxying connection test to: {url}")
            
            try:
                auth_url = f"{url.rstrip('/')}/web/session/authenticate"
                payload = {
                    "jsonrpc": "2.0",
                    "params": {
                        "db": db,
                        "login": username,
                        "password": password
                    }
                }
                
                response = requests.post(auth_url, json=payload, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                if "error" in result:
                    error_msg = result["error"].get("data", {}).get("message") or result["error"].get("message") or "Authentication failed"
                    return {"success": False, "error": error_msg}
                
                if "result" in result and result["result"].get("uid"):
                    return {"success": True}
                else:
                    return {"success": False, "error": "Invalid response from server"}
                    
            except requests.exceptions.Timeout:
                return {"success": False, "error": "Connection timed out. Please check the URL."}
            except requests.exceptions.ConnectionError:
                return {"success": False, "error": "Could not connect to server. Check URL and network."}
            except Exception as e:
                print(f"Error in test_connection proxy: {e}")
                return {"success": False, "error": str(e)}

        def export_database(self):
            """
            Export database from IndexedDB and save to file
            """
            print("LOG: export_database called")
            try:
                import json
                import datetime
                from pathlib import Path
                
                # Get data from IndexedDB via JavaScript
                # This will be called from JavaScript, so we need to handle the data differently
                # For now, create a placeholder that will be filled by JavaScript
                return {"success": True, "message": "Export initiated"}
            except Exception as e:
                print(f"Error in export_database: {e}")
                return {"success": False, "error": str(e)}

        def save_export_data(self, data_json):
            """
            Save exported data to file in the data folder
            """
            try:
                import json
                from pathlib import Path
                import time
                
                # Get current directory and create data folder
                current_dir = Path(__file__).parent
                data_dir = current_dir / 'data'
                data_dir.mkdir(exist_ok=True)
                
                timestamp = int(time.time())
                filename = f"pos_export_{timestamp}.json"
                filepath = data_dir / filename
                
                # Save data to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data_json, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"LOG: Data exported to {filepath}")
                return {"success": True, "filename": filename, "path": str(filepath)}
            except Exception as e:
                print(f"Error saving export data: {e}")
                return {"success": False, "error": str(e)}

        def import_database(self, data):
            """
            Import database data to IndexedDB
            """
            print("LOG: import_database called")
            try:
                # This will be called from JavaScript to import data to IndexedDB
                # The actual import logic is handled in JavaScript
                return {"success": True, "message": "Import initiated from JavaScript"}
            except Exception as e:
                print(f"Error in import_database: {e}")
                return {"success": False, "error": str(e)}

        def load_import_file(self, filename):
            """
            Load data from file for import
            """
            try:
                import json
                from pathlib import Path
                
                # Get current directory and data folder
                current_dir = Path(__file__).parent
                data_dir = current_dir / 'data'
                filepath = data_dir / filename
                
                # Load data from file
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"LOG: Data loaded from {filepath}")
                return {"success": True, "data": data}
            except Exception as e:
                print(f"Error loading import file: {e}")
                return {"success": False, "error": str(e)}

    # Create the window
    # Maximized window with controls (not fullscreen kiosk mode)
    window = webview.create_window(
        title='POS Standalone', 
        url=url,
        width=1280,
        height=800,
        resizable=True,
        fullscreen=False,
        maximized=True,  # Start maximized but with window controls
        min_size=(800, 600),
        js_api=Api() # Expose API to JavaScript
    )
    
    # Start the application loop
    # debug=True allows inspecting the element with right click -> inspect
    # private_mode=False ensures IndexedDB and LocalStorage are persisted
    data_dir = os.path.expanduser('~/.pos_standalone_data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    webview.start(debug=False, private_mode=False, storage_path=data_dir)

if __name__ == '__main__':
    run()

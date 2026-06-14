#!/usr/bin/env python3

import os
import sys

# Add the app directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

print("=== Starting Auto-Ingest Test ===")

try:
    from app.services.auto_ingest_service import AutoIngestService
    
    # Test with the correct path
    pdf_path = os.path.join('app', 'document', 'Solar_Energy_Report.pdf')
    print(f"Testing with PDF path: {pdf_path}")
    print(f"PDF exists: {os.path.exists(pdf_path)}")
    
    # Create service instance
    service = AutoIngestService(pdf_path)
    print(f"Service created successfully")
    print(f"Hash file path: {service.hash_file}")
    
    # Test hash functions
    print("\n=== Testing Hash Functions ===")
    current_hash = service.get_current_hash()
    stored_hash = service.get_stored_hash()
    
    print(f"Current hash: {current_hash[:16] if current_hash else 'None'}...")
    print(f"Stored hash: {stored_hash[:16] if stored_hash else 'None'}...")
    
    # Test change detection
    print("\n=== Testing Change Detection ===")
    if service.check_for_changes():
        print("✅ Document has changed - running auto-ingest")
        result = service.auto_ingest_if_changed()
        print(f"Auto-ingest result: {result}")
    else:
        print("❌ Document unchanged - no action needed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Completed ===")
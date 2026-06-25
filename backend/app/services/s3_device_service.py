"""
S3 Device Service - API Layer S3 Access

This service provides S3 access specifically for the API layer.
It's separate from the agent's S3 client to maintain clean separation
of concerns and deployment boundaries.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)

# Environment variables for S3 configuration
DEVICE_BUCKET = os.environ.get("DEVICE_BUCKET", "voltstream-storage")
DEVICE_KEY = os.environ.get("DEVICE_KEY", "devices/devices.json")

# Default power values for devices
_DEFAULT_POWER: Dict[str, float] = {
    "Heat pump": 2.1,
    "EV charger": 7.2,
    "Kitchen": 0.8,
    "HVAC": 1.4,
    "Water heater": 3.0,
    "Solar inverter": 0.2,
    "Dishwasher": 1.5,
    "Fan": 0.3,
}


class ApiS3DeviceService:
    """S3 service for API layer device management."""

    def __init__(self):
        """Initialize S3 client."""
        self.s3_client = boto3.client('s3')
        self.bucket = DEVICE_BUCKET
        self.key = DEVICE_KEY

    def _read_s3_json(self) -> List[Dict[str, Any]]:
        """Read and parse JSON from S3.
        
        Returns:
            List of device dictionaries
            
        Raises:
            RuntimeError: If S3 operation fails or JSON is invalid
        """
        try:
            logger.info(f"[API S3 READ] Bucket: {self.bucket}, Key: {self.key}")
            
            response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
            content = response['Body'].read().decode('utf-8')
            devices = json.loads(content)
            
            logger.info(f"[API S3 READ SUCCESS] Retrieved {len(devices)} devices")
            return devices
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"[API S3 READ ERROR] {error_code}: {str(e)}")
            
            if error_code == 'NoSuchBucket':
                raise RuntimeError(f"S3 bucket {self.bucket} does not exist")
            elif error_code == 'NoSuchKey':
                # Create default devices if file doesn't exist
                logger.warning(f"Creating default devices.json in {self.bucket}/{self.key}")
                return self._create_default_devices()
            elif error_code == 'AccessDenied':
                raise RuntimeError(f"Access denied to S3 bucket {self.bucket}")
            else:
                raise RuntimeError(f"S3 read error: {str(e)}")
                
        except json.JSONDecodeError as e:
            logger.error(f"[API S3 JSON PARSE ERROR] Invalid JSON in {self.bucket}/{self.key}: {str(e)}")
            raise RuntimeError(f"Invalid JSON in S3 object: {str(e)}")

    def _write_s3_json(self, devices: List[Dict[str, Any]]) -> None:
        """Write JSON data to S3.
        
        Args:
            devices: List of device dictionaries to store
            
        Raises:
            RuntimeError: If S3 write operation fails
        """
        try:
            json_data = json.dumps(devices, indent=2, default=str)
            logger.info(f"[API S3 WRITE] Uploading {len(devices)} devices to {self.bucket}/{self.key}")
            
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=self.key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info("[API S3 WRITE SUCCESS] Upload successful")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"[API S3 WRITE ERROR] {error_code}: {str(e)}")
            
            if error_code == 'NoSuchBucket':
                raise RuntimeError(f"S3 bucket {self.bucket} does not exist")
            elif error_code == 'AccessDenied':
                raise RuntimeError(f"Access denied to S3 bucket {self.bucket}")
            else:
                raise RuntimeError(f"S3 write error: {str(e)}")

    def _create_default_devices(self) -> List[Dict[str, Any]]:
        """Create default device configuration.
        
        Returns:
            List of default device dictionaries with timestamps
        """
        now = datetime.now()
        default_devices = [
            {"id": 1, "name": "Heat pump", "status": "on", "power_usage": 2.1},
            {"id": 2, "name": "EV charger", "status": "off", "power_usage": 0.0},
            {"id": 3, "name": "Kitchen", "status": "on", "power_usage": 0.8},
            {"id": 4, "name": "HVAC", "status": "on", "power_usage": 1.4},
            {"id": 5, "name": "Water heater", "status": "off", "power_usage": 0.0},
            {"id": 6, "name": "Solar inverter", "status": "on", "power_usage": 0.2},
            {"id": 101, "name": "Dishwasher", "status": "on", "power_usage": 1.5},
            {"id": 102, "name": "Fan", "status": "off", "power_usage": 0.0},
        ]
        
        # Add timestamps to all devices
        devices_with_timestamps = [
            {**device, "created_at": now, "updated_at": now}
            for device in default_devices
        ]
        
        # Write default devices to S3 for future use
        try:
            self._write_s3_json(devices_with_timestamps)
        except Exception as e:
            logger.warning(f"Failed to write default devices to S3: {str(e)}")
        
        return devices_with_timestamps

    def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from S3.
        
        Returns:
            List of device dictionaries with timestamps
            
        Raises:
            RuntimeError: If S3 operation fails
        """
        devices = self._read_s3_json()
        
        # Ensure all devices have proper timestamps
        now = datetime.now()
        for device in devices:
            if 'created_at' not in device:
                device['created_at'] = now
            if 'updated_at' not in device:
                device['updated_at'] = now
        
        return devices

    def get_device(self, device_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific device by ID.
        
        Args:
            device_id: ID of the device to retrieve
            
        Returns:
            Device dictionary if found, None otherwise
            
        Raises:
            RuntimeError: If S3 operation fails
        """
        devices = self.get_devices()
        device = next((d for d in devices if d['id'] == device_id), None)
        
        if device:
            logger.info(f"[API GET DEVICE] Found device {device_id}: {device['name']}")
        else:
            logger.warning(f"[API GET DEVICE] Device {device_id} not found")
        
        return device

    def update_device(self, device_id: int, status: str) -> Dict[str, Any]:
        """Update a device's status in S3.
        
        Args:
            device_id: ID of the device to update
            status: New status ('on' or 'off')
            
        Returns:
            Updated device dictionary
            
        Raises:
            RuntimeError: If S3 operation fails or device not found
        """
        devices = self.get_devices()
        device = next((d for d in devices if d['id'] == device_id), None)
        
        if device is None:
            logger.error(f"[API UPDATE ERROR] Device {device_id} not found")
            raise RuntimeError(f"Device with ID {device_id} not found")
        
        old_status = device['status']
        logger.info(f"[API UPDATE] Device: {device['name']}, Old Status: {old_status}, New Status: {status}")
        
        # Update device status and power usage
        device['status'] = status
        device['power_usage'] = _DEFAULT_POWER.get(device['name'], 0.5) if status == "on" else 0.0
        device['updated_at'] = datetime.now()
        
        # Write updated devices back to S3
        self._write_s3_json(devices)
        
        logger.info(f"[API UPDATE SUCCESS] Device {device_id} updated to {status}")
        return device

    def get_default_power(self) -> Dict[str, float]:
        """Get the default power mapping for devices.
        
        Returns:
            Dictionary mapping device names to their default power usage
        """
        return _DEFAULT_POWER


# Initialize the S3 service for API
device_service = ApiS3DeviceService()

# Export the service class for API usage
S3DeviceService = ApiS3DeviceService
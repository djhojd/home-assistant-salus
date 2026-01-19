#!/usr/bin/env python3
"""
Simple test script to verify connectivity with Salus UGE600 gateway.
This script uses the pyit600 library to connect and discover devices.

Usage:
    pip install pyit600
    python test_connection.py
"""

import asyncio
import logging
from pyit600.gateway import IT600Gateway

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Gateway configuration
GATEWAY_HOST = "192.168.1.X"  # Update with your gateway IP
# GATEWAY_EUID = "001E5E090901858F"  # Printed EUID on the back of the gateway
GATEWAY_EUID = "0000000000000000"  # Default EUID, update if needed


async def test_connection():
    """Test connection to the Salus gateway and discover devices."""
    print("=" * 60)
    print("Salus UGE600 Gateway Connection Test")
    print("=" * 60)
    print(f"Gateway IP: {GATEWAY_HOST}")
    print(f"EUID: {GATEWAY_EUID}")
    print("=" * 60)
    
    # Create gateway instance
    gateway = IT600Gateway(host=GATEWAY_HOST, euid=GATEWAY_EUID)
    
    try:
        # Attempt to connect
        print("\n[1] Connecting to gateway...")
        await gateway.connect()
        print("    ✓ Connected successfully!")
        
        # Poll for device status
        print("\n[2] Polling device status...")
        await gateway.poll_status()
        print("    ✓ Status polled successfully!")
        
        # Get all climate devices (thermostats)
        print("\n[3] Discovering climate devices (thermostats)...")
        climate_devices = gateway.get_climate_devices()
        if climate_devices:
            print(f"    Found {len(climate_devices)} climate device(s):")
            for device_id, device in climate_devices.items():
                print(f"\n    Device ID: {device_id}")
                print(f"      Name: {device.name}")
                print(f"      Current temp: {device.current_temperature}°C")
                print(f"      Target temp: {device.target_temperature}°C")
                print(f"      Available: {device.available}")
                # Try to print additional attributes if available
                for attr in ['preset_mode', 'hvac_mode', 'hvac_action', 'max_temp', 'min_temp']:
                    if hasattr(device, attr):
                        print(f"      {attr}: {getattr(device, attr)}")
        else:
            print("    No climate devices found")
        
        # Get all switch devices
        print("\n[4] Discovering switch devices...")
        switch_devices = gateway.get_switch_devices()
        if switch_devices:
            print(f"    Found {len(switch_devices)} switch device(s):")
            for device_id, device in switch_devices.items():
                print(f"\n    Device ID: {device_id}")
                print(f"      Name: {device.name}")
                print(f"      Is on: {device.is_on}")
                print(f"      Available: {device.available}")
        else:
            print("    No switch devices found")
        
        # Get all binary sensor devices
        print("\n[5] Discovering binary sensors...")
        binary_sensors = gateway.get_binary_sensor_devices()
        if binary_sensors:
            print(f"    Found {len(binary_sensors)} binary sensor(s):")
            for device_id, device in binary_sensors.items():
                print(f"\n    Device ID: {device_id}")
                print(f"      Name: {device.name}")
                print(f"      Is on: {device.is_on}")
                print(f"      Available: {device.available}")
        else:
            print("    No binary sensors found")
        
        # Get all sensor devices
        print("\n[6] Discovering sensor devices...")
        sensor_devices = gateway.get_sensor_devices()
        if sensor_devices:
            print(f"    Found {len(sensor_devices)} sensor device(s):")
            for device_id, device in sensor_devices.items():
                print(f"\n    Device ID: {device_id}")
                print(f"      Name: {device.name}")
                print(f"      Value: {device.value}")
                print(f"      Available: {device.available}")
        else:
            print("    No sensor devices found")
        
        # Get all cover devices
        print("\n[7] Discovering cover devices...")
        cover_devices = gateway.get_cover_devices()
        if cover_devices:
            print(f"    Found {len(cover_devices)} cover device(s):")
            for device_id, device in cover_devices.items():
                print(f"\n    Device ID: {device_id}")
                print(f"      Name: {device.name}")
                print(f"      Available: {device.available}")
        else:
            print("    No cover devices found")
        
        print("\n" + "=" * 60)
        print("CONNECTION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        print("\nTroubleshooting tips:")
        print("  1. Verify gateway IP is correct (check router or Salus app)")
        print("  2. Ensure 'Local WiFi Mode' is enabled in Salus app")
        print("  3. Try the actual EUID from your gateway label (16 hex chars)")
        print("  4. Check if gateway is powered on and connected to network")
        raise
    
    finally:
        # Close connection
        await gateway.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    asyncio.run(test_connection())

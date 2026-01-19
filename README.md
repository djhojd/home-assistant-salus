# Salus Smart Home Integration for Home Assistant

A custom Home Assistant integration for controlling Salus IT600 series devices via the UGE600 local gateway.

## Supported Devices

- **Thermostats**: SQ610RF, VS20WRF, VS20BRF, and other IT600 climate devices
- **Gateway**: UGE600 Universal Gateway (local WiFi mode)

## Features

- Local control (no cloud dependency)
- Real-time temperature monitoring
- Target temperature adjustment
- HVAC mode control (heat/off)
- Preset mode support

## Prerequisites

Before installing, ensure:

1. Your UGE600 gateway has a static IP or DHCP reservation
2. **Local WiFi Mode** is enabled in the Salus Smart Home app:
   - Go to Settings > Gateway
   - Set "Disable Local WiFi Mode" to **No**
   - Restart the gateway (power cycle)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu > Custom repositories
3. Add `https://github.com/djhojd/home-assistant-salus` as an Integration
4. Search for "Salus Smart Home" and install
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/salus` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings > Devices & Services**
2. Click **Add Integration**
3. Search for "Salus Smart Home"
4. Enter:
   - **Gateway IP Address**: Your gateway's local IP (e.g., `192.168.1.X`)
   - **EUID**: Leave as `0000000000000000` (default works for most gateways)
5. Click Submit

## Usage

After configuration, your thermostats will appear as climate entities:

- `climate.room_name` - Control temperature and mode
- Current temperature, target temperature, and heating status are displayed
- Use the climate card or automations to control your heating

## Troubleshooting

### Cannot connect to gateway

- Verify the gateway IP address is correct
- Ensure "Local WiFi Mode" is enabled in the Salus app
- Check that the gateway is powered on and connected to your network
- Try power cycling the gateway

### EUID issues

- Most gateways work with the default EUID `0000000000000000`
- If not, try the EUID printed on the back of your gateway (16 hex characters)

### Devices not appearing

- Ensure your thermostats are paired with the gateway in the Salus app
- Check Home Assistant logs for errors

## Development

### Test Script

A test script is included to verify gateway connectivity:

```bash
# Using Docker
docker build -f Dockerfile.test -t salus-test .
docker run --rm salus-test
```

## Credits

This integration uses the [pyit600](https://pypi.org/project/pyit600/) library for gateway communication.

## License

MIT License

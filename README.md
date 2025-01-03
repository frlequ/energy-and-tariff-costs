
# Energy and Tariff Costs

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Last Commit](https://img.shields.io/github/last-commit/frlequ/energy-and-tariff-costs)

A Home Assistant integration for calculating and displaying monthly energy and tariff costs based on Moje Elektro's energy distribution and tariff block usage. Customize your pricing inputs for different tariff blocks and energy consumption, and add additional costs based on your energy provider.
> [!NOTE]
> ⚠️ This integration requires the [Moj Elektro](https://github.com/frlequ/homeassistant-mojelektro) custom component to function properly.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Using HACS](#using-hacs)
  - [Manual Installation](#manual-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)
- [Links](#links)

## Features

- **Monthly Cost Calculation:** Automatically calculates your energy and tariff costs on a monthly basis.
- **Custom Price Inputs:** Define different prices for various tariff blocks and energy consumption tiers.
- **Additional Costs:** Add extra costs based on your energy provider’s fees or other charges.
- **Integration with Moje Elektro:** Seamlessly works with the Moj Elektro component to fetch energy usage data.

## Requirements

- **Home Assistant:** Latest version recommended.
- **Moj Elektro Integration:** Ensure the [Moj Elektro](https://github.com/frlequ/homeassistant-mojelektro) custom component is installed and configured.

## Installation

### Using HACS
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=frlequ&repository=energy-and-tariff-costs&category=integration)

1. **Add Repository:**
   - Open Home Assistant.
   - Navigate to **HACS** in the sidebar.
   - Click on **Integrations**.
   - Click the **+** button in the bottom right corner.
   - Enter the repository URL: `https://github.com/frlequ/energy-and-tariff-costs`
   - Follow the prompts to install.

2. **Restart Home Assistant:**
   - After installation, restart Home Assistant to activate the integration.

### Manual Installation

1. **Download the Repository:**
   - Clone or download the [energy-and-tariff-costs](https://github.com/frlequ/energy-and-tariff-costs) repository.

2. **Copy to Custom Components:**
   - Extract the downloaded files.
   - Copy the `energy_and_tariff_costs` folder to your Home Assistant's `custom_components` directory.

3. **Restart Home Assistant:**
   - Restart Home Assistant to load the new integration.

## Configuration

1. **Add Integration:**
   - Go to **Configuration** > **Devices & Services**.
   - Click on **Add Integration**.
   - Search for **Energy and Tariff Costs** and select it.

2. **Set Up Configuration:**
   - Enter the required details such as tariff block prices, energy costs, and any additional fees.
   - Save the configuration.

3. **Ensure Moj Elektro is Configured:**
   - Verify that the [Moj Elektro](https://github.com/frlequ/homeassistant-mojelektro) integration is properly set up and fetching your energy usage data.

## Usage

Once configured, the integration will display your monthly energy and tariff costs on your Home Assistant dashboard. You can customize the display using various Lovelace cards to fit your preferences.

## Screenshots

![Screenshot Controls.](/assets/energy_and_tariff_costs_controls.jpg)
![Screenshot Sensors.](/assets/energy_and_tariff_costs_sensors.jpg)

## Report any issues

Thanks and consider giving me a 🌟 star

<a href="https://www.buymeacoffee.com/frlequ" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>


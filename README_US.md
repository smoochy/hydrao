# Hydrao for Home Assistant

[Cliquez ici pour le texte français](./README.md)

Integration to report information from the Hydrao shower heads in Home Assistant.

## Installation

Use [hacs](https://hacs.xyz/). [![Open your Home Assistant instance and open the repository in the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sebcaps&repository=hydrao&category=integration)

## Configuration

### Get an API Key

- Request an API key from Hydrao using their [support form](https://www.hydrao.com/fr/besoin-d-aide-/sav).

### Configuration in Home Assistant

The configuration is done via the user interface.

First you need to enter the API [access credentials](#get-an-api-key) .

![image info](img/authent.png)

If having an installation with several shower heads, a selection of the device(s) is possible.

> **Note**
> The data is delivered from Hydrao servers via their API. This integration does not
> connect to the shower head and does not replace the mobile phone or the Hydrao gateway

### Data

The displayed data is:

- Average volume in L
- Total volume in L
- Number of showers
- Trend in %

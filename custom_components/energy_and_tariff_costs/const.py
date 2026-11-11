# const.py

DOMAIN = "energy_and_tariff_costs"
INITIALS = "etc"

# Price Keys
VT_PRICE = "energy_high_tariff_price"
MT_PRICE = "energy_low_tariff_price"
TAX = "tax"
ADDITIONAL_PRICE = "additional_price"
# Per-kWh contributions billed on total consumption:
# market operator (0.00013) + energy efficiency (0.0008) + excise (0.00153)
CONTRIB_PRICE = "contributions_price"

# Consumption Price Keys
BLOK_1_CONS_PRICE = "blok_1_consumption_price"
BLOK_2_CONS_PRICE = "blok_2_consumption_price"
BLOK_3_CONS_PRICE = "blok_3_consumption_price"
BLOK_4_CONS_PRICE = "blok_4_consumption_price"
BLOK_5_CONS_PRICE = "blok_5_consumption_price"

# Tariff Price Keys
BLOK_1_TAR_PRICE = "blok_1_tariff_price"
BLOK_2_TAR_PRICE = "blok_2_tariff_price"
BLOK_3_TAR_PRICE = "blok_3_tariff_price"
BLOK_4_TAR_PRICE = "blok_4_tariff_price"
BLOK_5_TAR_PRICE = "blok_5_tariff_price"

# Initial values (GEN-I bill, September 2026). Only used when a number
# entity has no restored state (fresh install or newly added entity).
VT_PRICE_INITIAL = 0.1199
MT_PRICE_INITIAL = 0.0979
TAX_INITIAL = 22.0
# Fixed monthly part: OVE/SPTE 2.71 + monthly fee 1.99 - eco discount 1.00
ADDITIONAL_PRICE_INITIAL = 3.70
CONTRIB_PRICE_INITIAL = 0.00246

BLOK_1_CONS_PRICE_INITIAL = 0.01998
BLOK_2_CONS_PRICE_INITIAL = 0.01998
BLOK_3_CONS_PRICE_INITIAL = 0.01717
BLOK_4_CONS_PRICE_INITIAL = 0.01805
BLOK_5_CONS_PRICE_INITIAL = 0.01299

BLOK_1_TAR_PRICE_INITIAL = 1.71126
BLOK_2_TAR_PRICE_INITIAL = 1.09230
BLOK_3_TAR_PRICE_INITIAL = 0.28902
BLOK_4_TAR_PRICE_INITIAL = 0.02436
BLOK_5_TAR_PRICE_INITIAL = 0.00245

# Sensor Definitions
MOJELEKTRO_PEAK = "sensor.moj_elektro_monthly_input_peak"
MOJELEKTRO_OFFPEAK = "sensor.moj_elektro_monthly_input_offpeak"

# New Block Sensors (agreed power per block, kW)
MOJELEKTRO_BLOK_1 = "sensor.moj_elektro_casovni_blok_1"
MOJELEKTRO_BLOK_2 = "sensor.moj_elektro_casovni_blok_2"
MOJELEKTRO_BLOK_3 = "sensor.moj_elektro_casovni_blok_3"
MOJELEKTRO_BLOK_4 = "sensor.moj_elektro_casovni_blok_4"
MOJELEKTRO_BLOK_5 = "sensor.moj_elektro_casovni_blok_5"

# Daily consumption per block (kWh, resets at midnight, holds yesterday's data)
MOJELEKTRO_DAILY_BLOK_1 = "sensor.moj_elektro_daily_input_blok_1"
MOJELEKTRO_DAILY_BLOK_2 = "sensor.moj_elektro_daily_input_blok_2"
MOJELEKTRO_DAILY_BLOK_3 = "sensor.moj_elektro_daily_input_blok_3"
MOJELEKTRO_DAILY_BLOK_4 = "sensor.moj_elektro_daily_input_blok_4"
MOJELEKTRO_DAILY_BLOK_5 = "sensor.moj_elektro_daily_input_blok_5"

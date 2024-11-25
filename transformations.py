import json
import pandas as pd
import re
import numpy as np
import math

def replace_range_with_mean_highthen(value):
    if isinstance(value, str):
        return re.sub(
            r'(\d+(\.\d+)?)(\s*-\s*)(\d+(\.\d+)?)',
            lambda m: str((float(m.group(1)) + float(m.group(4))) / 2),
            value
        )
    return value

def replace_set_values_with_mean_slash(x):
    if '/' in str(x):
        return str(np.mean(list(map(float, x.split('/')))))
    return x

def clean_double_dots(df, col):
    df[col] = df[col].str.replace(r'(\d+\.\d+)\.', r'\1', regex=True)
    return df

def replace_range_with_mean_space(value):
    if isinstance(value, str):
        return re.sub(
            r'(\d+(\.\d+)?)\s+(\d+(\.\d+)?)',
            lambda m: str((float(m.group(1)) + float(m.group(3))) / 2),
            value
        )
    return value

def convert_kg_by_100km_to_l_by_100km_and_remove_unit(text):
    return re.sub(r'(\d+(\.\d+)?)\s*kg/100\s*km', lambda m: f"{float(m.group(1)) / 0.74:.2f} ", str(text))

def convert_to_float(obj):
    import math
    if obj is not None and not (isinstance(obj, float) and math.isnan(obj)):
        try:
            return float(obj)
        except (ValueError, TypeError):
            return None
    return None


def clean_multiple_dots(value):
    if pd.isna(value):  # Check if the value is NaN
        return value
    if isinstance(value, str) and value.count('.') > 1:
        # Find first two segments separated by dots
        parts = value.split('.')
        return '.'.join(parts[:2])  # Keep only the first two parts
    return value

def clean_dot_before_highthen(obj):
    if obj is not None and not (isinstance(obj, float) and math.isnan(obj)):
        if isinstance(obj, str):
            obj = obj.replace('.-', '-')
    return obj

def remove_hyphen(s):
    if isinstance(s, str):
        return s.replace("-", "")
    return s

def remove_inf(s):
    if isinstance(s, str):
        return s.replace("<", "")
    return s

if __name__ == "__main__":

    # File paths
    input_file = "data/catalog_method/cars.jsonl"
    ml_output_csv_file = "data/catalog_method/cars_filtered_ml.csv"
    units_output_csv_file = "data/catalog_method/cars_filtered_units.csv"

    # Dictionnary to convert questions with specific names to general variables
    var_names_if_contains = {
        "What is the body type" : "q_body_type",
        "What is the fuel economy" : "q_fuel_economy",
        "How ECO is the car" : "q_eco",
        "What is the range of pure electric driving" : "q_electric_driving_range",
        "What is electricity consumption" : "q_electricity_consumption",
        "How fast is the car" : "q_speed",
        "How much power":"q_power",
        "What is the engine size":"q_engine_size",
        "How many cylinders":"q_n_cylinders",
        "What is the drivetrain":"q_drivetrain",
        "How long is this vehicle":"q_length",
        "How wide is the vehicle":"q_width",
        "What is the curb weight":"q_curb_weight",
        "What is the gross weight":"q_gross_weight",
        "How much trunk (boot) space":"q_trunk_boot_space",
        "How many gears":"q_n_gears",
        "Acceleration 0 - 60 mph (Calculated by Auto-Data.net)" : "Acceleration 0 - 60 mph"}

    processed_records = []

    # Process the JSONL file
    with open(input_file, "r") as infile:
        for line in infile:
            record = json.loads(line.strip())
            updated_record = {}
            for key, value in record.items():
                # Replace the key if it contains any specified pattern
                new_key = key
                for pattern, replacement in var_names_if_contains.items():
                    if pattern in key:
                        new_key = replacement
                        break
                updated_record[new_key] = value
            processed_records.append(updated_record)

    # Turn the data set to a pandas data frame
    df = pd.DataFrame(processed_records)

    # Drop useless columns
    df.drop(columns=[

        "image_path", # Not properly set during crawling

        "Electric motor 1", # Heading without value, ambiguous
        "Electric motor 2", # Heading without value, ambiguous
        "Electric motor 3", # Heading without value, ambiguous
        "Electric motor 4", # Heading without value, ambiguous

        "Modification (Engine)", # Redundant with Modification

        "Engine oil specification", # Log in to see column
        "Charging ports" # Log in to see column
        ], inplace=True)

    # Rename columns with unnecessary info
    df.rename(columns={'Acceleration 0 - 60 mph (Calculated by Auto-Data.net)': 'Acceleration 0 - 60 mph'}, inplace=True)

    # Add the proper images path
    df['images_path'] = df.apply(lambda row: f"data/catalog_method/images/{row['Brand']}/{row['Model']}/{row['Generation']}", axis=1)

    # Save the data set in df_original and keep df as the ML-oriented version of the data set
    df_original = df.copy()

    # Drop useless columns to build a machine learning dataset
    df.drop(columns=[
            "q_speed" # Bad quality since it contains the speed for some cars and acceleration for others
    ], inplace=True)

    # Remove units in the ML-oriented version of the data set
    df['q_fuel_economy'] = df['q_fuel_economy'].str.replace('l/100 km', '', regex=False)
    df['q_eco'] = df['q_eco'].str.replace('g/km CO', '', regex=False)
    df['q_power'] = df['q_power'].str.replace('Hp', '', regex=False)
    df['q_power'] = df['q_power'].str.replace('Nm', '', regex=False)
    df['q_power'] = df['q_power'].str.replace(',', '', regex=False)
    df['q_engine_size'] = df['q_engine_size'].str.replace('l', '', regex=False)
    df['q_length'] = df['q_length'].str.replace('mm', '', regex=False)
    df['q_width'] = df['q_width'].str.replace('mm', '', regex=False)
    df['q_curb_weight'] = df['q_curb_weight'].str.replace('kg', '', regex=False)
    df['Start of production'] = df['Start of production'].str.replace('year', '', regex=False)
    df['End of production'] = df['End of production'].str.replace('year', '', regex=False)
    df['Fuel consumption (economy) - urban'] = df['Fuel consumption (economy) - urban'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban'] = df['Fuel consumption (economy) - extra urban'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined'] = df['Fuel consumption (economy) - combined'].str.replace('l/100 km', '', regex=False)
    df['CO'] = df['CO'].str.replace('g/km', '', regex=False)
    df['Acceleration 0 - 100 km/h'] = df['Acceleration 0 - 100 km/h'].str.replace('sec', '', regex=False)
    df['Acceleration 0 - 62 mph'] = df['Acceleration 0 - 62 mph'].str.replace('sec', '', regex=False)
    df['Acceleration 0 - 60 mph'] = df['Acceleration 0 - 60 mph'].str.replace('sec', '', regex=False)
    df['Maximum speed'] = df['Maximum speed'].str.replace('km/h', '', regex=False)
    df['Weight-to-power ratio'] = df['Weight-to-power ratio'].str.replace('kg/Hp', '', regex=False)
    df['Weight-to-power ratio'] = df['Weight-to-power ratio'].str.replace('Hp/tonne', '', regex=False)
    df['Weight-to-power ratio'] = df['Weight-to-power ratio'].str.replace(',', '', regex=False)
    df['Weight-to-torque ratio'] = df['Weight-to-torque ratio'].str.replace('kg/Nm', '', regex=False)
    df['Weight-to-torque ratio'] = df['Weight-to-torque ratio'].str.replace('Nm/tonne', '', regex=False)
    df['Weight-to-torque ratio'] = df['Weight-to-torque ratio'].str.replace(',', '', regex=False)
    df['Power per litre'] = df['Power per litre'].str.replace('Hp/l', '', regex=False)
    df['Power'] = df['Power'].str.replace('Hp', '', regex=False)
    df['Torque'] = df['Torque'].str.replace('Nm', '', regex=False)
    df['Engine displacement'] = df['Engine displacement'].str.replace('cm', '', regex=False)
    df['Cylinder Bore'] = df['Cylinder Bore'].str.replace('mm', '', regex=False)
    df['Piston Stroke'] = df['Piston Stroke'].str.replace('mm', '', regex=False)
    df['Engine oil capacity'] = df['Engine oil capacity'].str.replace('l', '', regex=False)
    df['Coolant'] = df['Coolant'].str.replace('l', '', regex=False)
    df['Kerb Weight'] = df['Kerb Weight'].str.replace('kg', '', regex=False)
    df['Fuel tank capacity'] = df['Fuel tank capacity'].str.replace('l', '', regex=False)
    df['Length'] = df['Length'].str.replace('mm', '', regex=False)
    df['Width'] = df['Width'].str.replace('mm', '', regex=False)
    df['Height'] = df['Height'].str.replace('mm', '', regex=False)
    df['Wheelbase'] = df['Wheelbase'].str.replace('', '', regex=False)
    df['Wheelbase'] = df['Wheelbase'].str.replace('mm', '', regex=False)
    df['Front track'] = df['Front track'].str.replace('mm', '', regex=False)
    df['Rear (Back) track'] = df['Rear (Back) track'].str.replace('mm', '', regex=False)
    df['Minimum turning circle (turning diameter)'] = df['Minimum turning circle (turning diameter)'].str.replace('m', '', regex=False)
    df['q_electric_driving_range'] = df['q_electric_driving_range'].str.replace('km', '', regex=False)
    df['q_electricity_consumption'] = df['q_electricity_consumption'].str.replace('kwh/100 km', '', regex=False)
    df['q_electricity_consumption'] = df['q_electricity_consumption'].str.replace('kWh/100 km', '', regex=False)
    df['Gross battery capacity'] = df['Gross battery capacity'].str.replace('kwh', '', regex=False)
    df['Gross battery capacity'] = df['Gross battery capacity'].str.replace('kWh', '', regex=False)
    df['Net (usable) battery capacity'] = df['Net (usable) battery capacity'].str.replace('kWh', '', regex=False)
    df['Battery voltage'] = df['Battery voltage'].str.replace('V', '', regex=False)
    df['Battery technology'] = df['Battery technology'].str.replace('', '', regex=False)
    df['Battery weight'] = df['Battery weight'].str.replace('kg', '', regex=False)
    df['All-electric range (WLTP)'] = df['All-electric range (WLTP)'].str.replace('km', '', regex=False)
    df['Average Energy consumption (WLTP)'] = df['Average Energy consumption (WLTP)'].str.replace('kWh/100 km', '', regex=False)
    df['Electric motor power'] = df['Electric motor power'].str.replace('Hp', '', regex=False)
    df['Electric motor power'] = df['Electric motor power'].str.replace('rpm.', '', regex=False)
    df['Electric motor Torque'] = df['Electric motor Torque'].str.replace('Nm', '', regex=False)
    df['Electric motor Torque'] = df['Electric motor Torque'].str.replace('rpm.', '', regex=False)
    df['Electric motor location'] = df['Electric motor location'].str.replace('', '', regex=False)
    df['System power'] = df['System power'].str.replace('Hp', '', regex=False)
    df['System torque'] = df['System torque'].str.replace('Nm', '', regex=False)
    df['Width including mirrors'] = df['Width including mirrors'].str.replace('mm', '', regex=False)
    df['q_gross_weight'] = df['q_gross_weight'].str.replace('kg', '', regex=False)
    df['q_trunk_boot_space'] = df['q_trunk_boot_space'].str.replace('l', '', regex=False)
    df['Fuel consumption (economy) - urban (NEDC)'] = df['Fuel consumption (economy) - urban (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (NEDC)'] = df['Fuel consumption (economy) - extra urban (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (NEDC)'] = df['Fuel consumption (economy) - combined (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Max. weight'] = df['Max. weight'].str.replace('kg', '', regex=False)
    df['Max load'] = df['Max load'].str.replace('kg', '', regex=False)
    df['Trunk (boot) space - minimum'] = df['Trunk (boot) space - minimum'].str.replace('l', '', regex=False)
    df['Trunk (boot) space - maximum'] = df['Trunk (boot) space - maximum'].str.replace('l', '', regex=False)
    df['Front overhang'] = df['Front overhang'].str.replace('mm', '', regex=False)
    df['Rear overhang'] = df['Rear overhang'].str.replace('mm', '', regex=False)
    df['Permitted trailer load with brakes (12%)'] = df['Permitted trailer load with brakes (12%)'].str.replace('kg', '', regex=False)
    df['Fuel consumption at Low speed (WLTP)'] = df['Fuel consumption at Low speed (WLTP)'].str.replace('l/100 lm', '', regex=False)
    df['Fuel consumption at Low speed (WLTP)'] = df['Fuel consumption at Low speed (WLTP)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption at Medium speed (WLTP)'] = df['Fuel consumption at Medium speed (WLTP)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption at high speed (WLTP)'] = df['Fuel consumption at high speed (WLTP)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption at very high speed (WLTP)'] = df['Fuel consumption at very high speed (WLTP)'].str.replace('l/100 km', '', regex=False)
    df['Combined fuel consumption (WLTP)'] = df['Combined fuel consumption (WLTP)'].str.replace('l/100 km', '', regex=False)
    df['Max. roof load'] = df['Max. roof load'].str.replace('kg', '', regex=False)
    df['Fuel consumption (economy) - urban (Ethanol - E85)'] = df['Fuel consumption (economy) - urban (Ethanol - E85)'].str.replace('l/100 km', '',regex=False)
    df['Fuel consumption (economy) - extra urban (Ethanol - E85)'] = df['Fuel consumption (economy) - extra urban (Ethanol - E85)'].str.replace('l/100 km', '', regex=False)
    df['Acceleration 0 - 100 km/h (Ethanol - E85)'] = df['Acceleration 0 - 100 km/h (Ethanol - E85)'].str.replace('sec', '', regex=False)
    df['Maximum speed (Ethanol - E85)'] = df['Maximum speed (Ethanol - E85)'].str.replace('km/h', '', regex=False)
    df['Power (Ethanol - E85)'] = df['Power (Ethanol - E85)'].str.replace('Hp', '', regex=False)
    df['Power (Ethanol - E85)'] = df['Power (Ethanol - E85)'].str.replace('rpm.', '', regex=False)
    df['Power per litre (Ethanol - E85)'] = df['Power per litre (Ethanol - E85)'].str.replace('Hp/l', '', regex=False)
    df['Ride height (ground clearance)'] = df['Ride height (ground clearance)'].str.replace('mm', '', regex=False)
    df['Approach angle'] = df['Approach angle'].str.replace('Â°', '', regex=False)
    df['Departure angle'] = df['Departure angle'].str.replace('Â°', '', regex=False)
    df['Ramp-over (brakeover) angle'] = df['Ramp-over (brakeover) angle'].str.replace('Â°', '', regex=False)
    df['Permitted trailer load without brakes'] = df['Permitted trailer load without brakes'].str.replace('kg', '', regex=False)
    df['Permitted towbar download'] = df['Permitted towbar download'].str.replace('kg', '', regex=False)
    df['Maximum engine speed'] = df['Maximum engine speed'].str.replace('rpm.', '', regex=False)
    df['Fuel consumption (economy) - urban (EPA)'] = df['Fuel consumption (economy) - urban (EPA)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (EPA)'] = df['Fuel consumption (economy) - extra urban (EPA)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (EPA)'] = df['Fuel consumption (economy) - combined (EPA)'].str.replace('l/100 km', '', regex=False)
    df['Width with mirrors folded'] = df['Width with mirrors folded'].str.replace('mm', '', regex=False)
    df['All-electric range (EPA)'] = df['All-electric range (EPA)'].str.replace('km', '', regex=False)
    df['All-electric range (CLTC)'] = df['All-electric range (CLTC)'].str.replace('km', '', regex=False)
    df['All-electric range (WLTC)'] = df['All-electric range (WLTC)'].str.replace('km', '', regex=False)
    df['Average Energy consumption (CLTC)'] = df['Average Energy consumption (CLTC)'].str.replace('kWh/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (WLTC)'] = df['Fuel consumption (economy) - combined (WLTC)'].str.replace('l/100 km', '', regex=False)
    df['Average Energy consumption (WLTC)'] = df['Average Energy consumption (WLTC)'].str.replace('kWh/100 km', '', regex=False)
    df['All-electric range'] = df['All-electric range'].str.replace('km', '', regex=False)
    df['Average Energy consumption'] = df['Average Energy consumption'].str.replace('kWh/100 km', '', regex=False)
    df['Maximum revolutions of the electric motor'] = df['Maximum revolutions of the electric motor'].str.replace('rpm.', '', regex=False)
    df['100 km/h - 0'] = df['100 km/h - 0'].str.replace('m', '', regex=False)
    df['AdBlue tank'] = df['AdBlue tank'].str.replace('l', '', regex=False)
    df['Fuel consumption (economy) - urban (LPG)'] = df['Fuel consumption (economy) - urban (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (LPG)'] = df['Fuel consumption (economy) - extra urban (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (LPG)'] = df['Fuel consumption (economy) - combined (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Acceleration 0 - 100 km/h (LPG)'] = df['Acceleration 0 - 100 km/h (LPG)'].str.replace('sec', '', regex=False)
    df['Fuel tank capacity (LPG)'] = df['Fuel tank capacity (LPG)'].str.replace('l', '', regex=False)
    df['Wading depth'] = df['Wading depth'].str.replace('mm', '', regex=False)
    df['Max speed (electric)'] = df['Max speed (electric)'].str.replace('km/h', '', regex=False)
    df['Acceleration 0 - 200 km/h'] = df['Acceleration 0 - 200 km/h'].str.replace('sec', '', regex=False)
    df['Fuel consumption (economy) - urban (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - urban (NEDC, WLTP equivalent)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - extra urban (NEDC, WLTP equivalent)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - combined (NEDC, WLTP equivalent)'].str.replace('l/100 km', '', regex=False)
    df['Permitted trailer load with brakes (8%)'] = df['Permitted trailer load with brakes (8%)'].str.replace('kg', '', regex=False)
    df['All-electric range (NEDC)'] = df['All-electric range (NEDC)'].str.replace('km', '', regex=False)
    df['Acceleration 0 - 300 km/h'] = df['Acceleration 0 - 300 km/h'].str.replace('sec', '', regex=False)
    df['Recuperation output'] = df['Recuperation output'].str.replace('kW', '', regex=False)
    df['Average Energy consumption (NEDC)'] = df['Average Energy consumption (NEDC)'].str.replace('kWh/100 km', '', regex=False)
    df['Fuel consumption at Low speed (WLTP) (CNG)'] = df['Fuel consumption at Low speed (WLTP) (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption at Medium speed (WLTP) (CNG)'] = df['Fuel consumption at Medium speed (WLTP) (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption at high speed (WLTP) (CNG)'] = df['Fuel consumption at high speed (WLTP) (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption at very high speed (WLTP) (CNG)'] = df['Fuel consumption at very high speed (WLTP) (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Combined fuel consumption (WLTP) (CNG)'] = df['Combined fuel consumption (WLTP) (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - urban (CNG) (NEDC)'] = df['Fuel consumption (economy) - urban (CNG) (NEDC)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (CNG) (NEDC)'] = df['Fuel consumption (economy) - extra urban (CNG) (NEDC)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (CNG) (NEDC)'] = df['Fuel consumption (economy) - combined (CNG) (NEDC)'].str.replace('kg/100 km', '', regex=False)
    df['CNG cylinder capacity'] = df['CNG cylinder capacity'].str.replace('kg', '', regex=False)
    df['Fuel consumption (economy) - urban (CNG)'] = df['Fuel consumption (economy) - urban (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (CNG)'] = df['Fuel consumption (economy) - extra urban (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (LPG) (NEDC)'] = df['Fuel consumption (economy) - combined (LPG) (NEDC)'].str.replace('', '', regex=False)
    df['Fuel consumption (economy) - combined (CNG)'] = df['Fuel consumption (economy) - combined (CNG)'].str.replace('kg/100 km', '', regex=False)
    df['All-electric range (NEDC, WLTP equivalent)'] = df['All-electric range (NEDC, WLTP equivalent)'].str.replace('km', '', regex=False)
    df['Average Energy consumption (NEDC, WLTP equivalent)'] = df['Average Energy consumption (NEDC, WLTP equivalent)'].str.replace('kWh/100 km', '', regex=False)
    df['Climb angle'] = df['Climb angle'].str.replace('Â°', '', regex=False)
    df['Average Energy consumption (EPA)'] = df['Average Energy consumption (EPA)'].str.replace('kWh/100 km', '', regex=False)
    df['200 km/h - 0'] = df['200 km/h - 0'].str.replace('m', '', regex=False)
    df['Fuel consumption (economy) - combined (CLTC)'] = df['Fuel consumption (economy) - combined (CLTC)'].str.replace('l/100 km', '', regex=False)
    df['Torque (Ethanol - E85)'] = df['Torque (Ethanol - E85)'].str.replace('Nm', '', regex=False)
    df['Torque (Ethanol - E85)'] = df['Torque (Ethanol - E85)'].str.replace('rpm.', '', regex=False)
    df['Fuel consumption (economy) - combined (Ethanol - E85)'] = df['Fuel consumption (economy) - combined (Ethanol - E85)'].str.replace('l/100 km', '', regex=False)
    df['Power (CNG)'] = df['Power (CNG)'].str.replace('Hp', '', regex=False)
    df['Power (CNG)'] = df['Power (CNG)'].str.replace('rpm.', '', regex=False)
    df['Power per litre (CNG)'] = df['Power per litre (CNG)'].str.replace('Hp/l', '', regex=False)
    df['Torque (CNG)'] = df['Torque (CNG)'].str.replace('Nm', '', regex=False)
    df['Torque (CNG)'] = df['Torque (CNG)'].str.replace('rpm.', '', regex=False)
    df['Fuel consumption (economy) - urban (LPG) (NEDC)'] = df['Fuel consumption (economy) - urban (LPG) (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (LPG) (NEDC)'] = df['Fuel consumption (economy) - extra urban (LPG) (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (LPG) (NEDC)'] = df['Fuel consumption (economy) - combined (LPG) (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Maximum speed (LPG)'] = df['Maximum speed (LPG)'].str.replace('km/h', '', regex=False)
    df['Power (LPG)'] = df['Power (LPG)'].str.replace('Hp', '', regex=False)
    df['Power (LPG)'] = df['Power (LPG)'].str.replace('rpm.', '', regex=False)
    df['Power per litre (LPG)'] = df['Power per litre (LPG)'].str.replace('Hp/l', '', regex=False)
    df['Torque (LPG)'] = df['Torque (LPG)'].str.replace('Nm', '', regex=False)
    df['Torque (LPG)'] = df['Torque (LPG)'].str.replace('rpm.', '', regex=False)
    df['Fuel consumption at Low speed (WLTP) (LPG)'] = df['Fuel consumption at Low speed (WLTP) (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption at Medium speed (WLTP) (LPG)'] = df['Fuel consumption at Medium speed (WLTP) (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption at high speed (WLTP) (LPG)'] = df['Fuel consumption at high speed (WLTP) (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption at very high speed (WLTP) (LPG)'] = df['Fuel consumption at very high speed (WLTP) (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Combined fuel consumption (WLTP) (LPG)'] = df['Combined fuel consumption (WLTP) (LPG)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - urban (LPG) (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - urban (LPG) (NEDC, WLTP equivalent)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (LPG) (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - extra urban (LPG) (NEDC, WLTP equivalent)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (LPG) (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - combined (LPG) (NEDC, WLTP equivalent)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - urban (Ethanol - E85) (NEDC)'] = df['Fuel consumption (economy) - urban (Ethanol - E85) (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (Ethanol - E85) (NEDC)'] = df['Fuel consumption (economy) - extra urban (Ethanol - E85) (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (Ethanol - E85) (NEDC)'] = df['Fuel consumption (economy) - combined (Ethanol - E85) (NEDC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - urban (WLTC)'] = df['Fuel consumption (economy) - urban (WLTC)'].str.replace('l/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (WLTC)'] = df['Fuel consumption (economy) - extra urban (WLTC)'].str.replace('l/100 km', '', regex=False)
    df['Acceleration 0 - 100 km/h (CNG)'] = df['Acceleration 0 - 100 km/h (CNG)'].str.replace('sec', '', regex=False)
    df['Maximum speed (CNG)'] = df['Maximum speed (CNG)'].str.replace('km/h', '', regex=False)
    df['Fuel consumption (economy) - urban (CNG) (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - urban (CNG) (NEDC, WLTP equivalent)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - extra urban (CNG) (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - extra urban (CNG) (NEDC, WLTP equivalent)'].str.replace('kg/100 km', '', regex=False)
    df['Fuel consumption (economy) - combined (CNG) (NEDC, WLTP equivalent)'] = df['Fuel consumption (economy) - combined (CNG) (NEDC, WLTP equivalent)'].str.replace('kg/100 km', '', regex=False)
    df['Compression ratio'] = df['Compression ratio'].str.replace(':1', '', regex=False)
    df['Wheel rims size'] = df['Wheel rims size'].str.replace('Front wheel rims:', '', regex=False)
    df['Wheel rims size'] = df['Wheel rims size'].str.replace('ET37', '', regex=False)
    df['Wheel rims size'] = df['Wheel rims size'].str.replace('ET34', '', regex=False)
    df['Wheel rims size'] = df['Wheel rims size'].str.replace('ET33', '', regex=False)
    df['Maximum speed'] = df['Maximum speed'].str.replace(', Electronically limited', '', regex=False)

    # Keep only the peak power in power/rpm columns
    power_columns = [
    "Power",
    "Torque",
    "Electric motor power",
    "Electric motor Torque",
    "Power (Ethanol - E85)",
    "Torque (Ethanol - E85)",
    "Power (CNG)",
    "Torque (CNG)",
    "Power (LPG)",
    "Torque (LPG)",
    "System power",
    "System torque"]
    for col in power_columns:
        df[col] = df[col].str.split(' @').str[0]

    # Separate Power and Torque in power/torque columns and create additional columns for torque
    df['q_power_torque'] = df['q_power'].str.split().str[-1]
    df['q_power'] = df['q_power'].str.split().str[0]

    # Keep only the first value for redundant units
    df["Weight-to-power ratio"] = df["Weight-to-power ratio"].apply(lambda x: x.split()[0] if isinstance(x, str) else x)
    df["Weight-to-torque ratio"] = df["Weight-to-torque ratio"].apply(lambda x: x.split()[0] if isinstance(x, str) else x)

    # Keep only wheels diameter
    df['Wheel rims size'] = df['Wheel rims size'].str.split('x').str[-1].str.strip()

    # Keep only the year in dates
    df['Start of production'] = df['Start of production'].str.split(',').str[-1].str.strip()
    df['End of production'] = df['End of production'].str.split(',').str[-1].str.strip()

    # Average interval values separated by "-" or " - "
    to_average_cols = [
        "q_length",
        "q_width",
        "q_curb_weight",
        "Seats",
        "Doors"#,
        #"Fuel consumption (economy)"
        ]

    for col in to_average_cols:
        df[col] = df[col].apply(replace_range_with_mean_highthen)

    # Average when there are multiple values separated by "/"
    to_average_cols = [
        "q_length",
        "q_width",
        "q_curb_weight",
        "Doors"
        ]
    for col in to_average_cols:
        df[col] = df[col].apply(replace_set_values_with_mean_slash)

    col = "q_fuel_economy"
    df = clean_double_dots(df, col)
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(replace_range_with_mean_space)
    df[col] = df[col].apply(convert_kg_by_100km_to_l_by_100km_and_remove_unit)
    df[col] = df[col].apply(convert_to_float)

    col = "Fuel consumption (economy) - urban"
    df[col] = df[col].apply(clean_dot_before_highthen)
    df[col] = df[col].apply(clean_multiple_dots)
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(convert_to_float)

    col = "Fuel consumption (economy) - extra urban"
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(convert_kg_by_100km_to_l_by_100km_and_remove_unit)
    df[col] = df[col].apply(convert_to_float)

    col = "Fuel consumption (economy) - combined"
    df[col] = df[col].apply(clean_multiple_dots)
    df = clean_double_dots(df, col)
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(replace_range_with_mean_space)
    df[col] = df[col].apply(convert_kg_by_100km_to_l_by_100km_and_remove_unit)
    df[col] = df[col].apply(convert_to_float)


    col = "CO"
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(remove_hyphen)
    df[col] = df[col].apply(convert_to_float)    

    col = "Acceleration 0 - 100 km/h"
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(clean_multiple_dots)
    df[col] = df[col].apply(remove_inf)
    df[col] = df[col].apply(convert_to_float)

    col = "Acceleration 0 - 62 mph"
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(remove_inf)
    df[col] = df[col].apply(clean_multiple_dots)
    df[col] = df[col].apply(clean_multiple_dots)
    df[col] = df[col].apply(convert_to_float)

    col = "Acceleration 0 - 60 mph"
    df[col] = df[col].apply(replace_range_with_mean_highthen)
    df[col] = df[col].apply(remove_inf)
    df[col] = df[col].apply(convert_to_float)

    # Save both frames as csv
    df.to_csv(ml_output_csv_file, index=False)
    df_original.to_csv(units_output_csv_file, index=False)
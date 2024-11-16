import json


if __name__ == "__main__":

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
        "How many gears":"q_n_gears"
                }

    # File paths
    input_file = "away_abarth_cars.jsonl"
    output_file = "away_abarth_cars_new.jsonl"

    # Process the JSONL file
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
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
            # Write the updated record to the output file
            outfile.write(json.dumps(updated_record) + "\n")
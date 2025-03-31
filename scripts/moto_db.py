#! .venv/bin/python
import io
import os
import sys
from collections import namedtuple, defaultdict
from typing import List, Any, Dict

import pandas
import pyzipper
from fuzzywuzzy import process

with pyzipper.AESZipFile('store/moto-db-2025-03.tsv.zip', 'r') as zip_ref:
    zip_ref.setpassword(os.environ['MOTO_DB_PASS'].encode())
    file_content = zip_ref.read('moto-db-2025-03.tsv')

    # Create a file-like object
    file_like_object = io.BytesIO(file_content)


df_specs = pandas.read_csv(file_like_object, delimiter='\t')

cols_descriptions: dict[str, str] = {
    "str_page_url": "URL of the motorcycle's page",
    "str_image_url": "URL of the motorcycle's image",
    "str_make": "Manufacturer/brand of the motorcycle",
    "str_model": "Model name of the motorcycle",
    "int_year": "Production year of the motorcycle",
    "str_category": "Category type (e.g., Sport, Cruiser, Adventure)",
    "float_rating": "User/expert rating of the motorcycle",
    "float_price_new": "New motorcycle price value",
    "str_price_currency": "Currency of the price (e.g., USD, EUR)",
    "float_displacement": "Engine displacement in cc/cubic centimeters",
    "str_engine_details": "Detailed engine specifications",
    "str_engine_type": "Type of engine (e.g., V-twin, Inline-4)",
    "float_power_hp": "Maximum power output in horsepower",
    "int_power_at_rpm": "RPM at which maximum power is achieved",
    "float_torque_nm": "Maximum torque in Newton-meters",
    "int_torque_at_rpm": "RPM at which maximum torque is achieved",
    "float_top_speed_kmh": "Maximum speed in kilometers per hour",
    "float_top_speed_miles": "Maximum speed in miles per hour",
    "float_acceleration_0_100_secs": "Acceleration time from 0 to 100 km/h in seconds",
    "float_acceleration_60_140_sec": "Acceleration time from 60 to 140 km/h in seconds",
    "int_max_rpm": "Maximum engine RPM",
    "str_compression": "Engine compression ratio",
    "str_original_bore_stroke": "Bore and stroke dimensions",
    "int_valves_per_cylinder": "Number of valves per cylinder",
    "str_fuel_system": "Type of fuel system",
    "str_fuel_control": "Fuel control mechanism",
    "str_ignition": "Ignition system type",
    "str_lubrication_system": "Engine lubrication system",
    "str_cooling_system": "Engine cooling system",
    "str_gearbox": "Gearbox/transmission specification",
    "str_transmission_final_drive": "Final drive type (chain, belt, shaft)",
    "str_clutch": "Clutch type and specification",
    "str_driveline": "Driveline configuration",
    "float_fuel_consumption_l_on_100km": "Fuel consumption in liters per 100 km",
    "float_greenhouse_gases_co2": "CO2 emissions",
    "str_emission_details": "Emission compliance and details",
    "str_exhaust_system": "Exhaust system specification",
    "str_frame_type": "Type of frame/chassis",
    "float_rake_deg": "Rake/caster angle in degrees",
    "int_trail_mm": "Trail measurement in millimeters",
    "str_front_suspension": "Front suspension type and features",
    "str_front_wheel_travel": "Front wheel travel distance",
    "str_rear_suspension": "Rear suspension type and features",
    "str_rear_wheel_travel": "Rear wheel travel distance",
    "str_front_tyre": "Front tire size and specification",
    "str_rear_tyre": "Rear tire size and specification",
    "str_front_brakes": "Front brakes type",
    "str_front_brakes_diameter": "Front brakes diameter",
    "str_rear_brakes": "Rear brakes type",
    "str_rear_brakes_diameter": "Rear brakes diameter",
    "str_wheels": "Wheels specification",
    "int_height_seat_mm": "Seat height in millimeters",
    "float_dry_weight_kg": "Dry weight (without fluids) in kilograms",
    "float_weight_incl_fluids_kg": "Weight including fluids in kilograms",
    "int_overall_height_mm": "Overall height in millimeters",
    "int_overall_length_mm": "Overall length in millimeters",
    "int_overall_width_mm": "Overall width in millimeters",
    "int_ground_clearance_mm": "Ground clearance in millimeters",
    "int_wheelbase_mm": "Wheelbase in millimeters",
    "int_fuel_capacity_litres": "Fuel tank capacity in liters",
    "float_reserve_fuel_capacity_litres": "Reserve fuel capacity in liters",
    "float_oil_capacity_litres": "Oil capacity in liters",
    "str_color_options": "Available color options",
    "str_starter_options": "Starter mechanism options",
    "str_instruments": "Dashboard/instrument panel details",
    "str_electrical": "Electrical system specification",
    "str_light": "Lighting system details",
    "str_carrying_capacity": "Cargo/load carrying capacity",
    "str_factory_warranty": "Manufacturer warranty information",
    "str_anonimous_comments": "Anonymous user comments",
    "str_modifications": "Common modifications",
    "str_engine_oil": "Recommended engine oil",
    "str_oil_filter": "Recommended oil filter",
    "str_brake_fluid": "Recommended brake fluid",
    "str_coolant": "Recommended coolant",
    "str_battery": "Battery specification",
    "str_spark_plugs": "Recommended spark plugs",
    "str_idle_speed_rpm": "Idle speed in RPM",
    "int_chain_size": "Drive chain size",
    "int_chain_links": "Number of links in the drive chain",
    "str_sprockets": "Sprocket specification",
    "str_tire_pressure_front": "Recommended front tire pressure",
    "str_tire_pressure_rear": "Recommended rear tire pressure",
    "float_fork_tube_size_mm": "Fork tube diameter in millimeters"
}

for col_name, description in cols_descriptions.items():
    if col_name in df_specs:
        pass
        # print(col_name, description)
    else:
        print(f"{col_name} has no description.", file=sys.stderr)

LevResult = namedtuple('LevResult', ['key', 'score'])


def _get_vehs_by_levenstain(df: pandas.DataFrame, query: str, col_name: str, threshold: int = 75) -> List[LevResult]:
    # Находим лучшие совпадения
    cols = df[col_name].values.tolist()
    # cols = [c.strip().lower() for c in cols]
    matches = process.extract(query.strip(), cols, limit=None)
    print(f"Levenstain search in {col_name}: {query=}, {len(matches)=} "
          f"Top1: {matches[0] if matches else None}, {threshold=}")
    return [LevResult(key, score) for key, score in matches if score >= threshold]


def _filter_by(col_name: str, col_strict_value: str, df: pandas.DataFrame) -> pandas.DataFrame:
    df = df_specs if df is None else df
    return df[df[col_name] == col_strict_value]


def get_make_levenstain(query: str, threshold: int = 75, df: pandas.DataFrame = df_specs) -> List[LevResult]:
    if query is None:
        return []
    df = df.copy()
    df['first_letter'] = df['str_model'].str[0].str.lower()
    df = df[df['first_letter'] == query[0].lower()]
    return _get_vehs_by_levenstain(df, query, 'str_make', threshold)


def get_model_levenstain(query: str, threshold: int = 75, df: pandas.DataFrame = df_specs) -> List[LevResult]:
    if query is None:
        return []
    query = query.replace(" ", "")
    df = df.copy()
    df['first_letter'] = df['str_model'].str[0].str.lower()
    df = df[df['first_letter'] == query[0].lower()]
    return _get_vehs_by_levenstain(df, query, 'str_model', threshold)


def get_specs_by_model(model_name_strict: str, df: pandas.DataFrame = None) -> pandas.DataFrame:
    return _filter_by('str_model', model_name_strict, df)


def get_specs_by_make(make_name_strict: str, df: pandas.DataFrame = None) -> pandas.DataFrame:
    return _filter_by('str_make', make_name_strict, df)


def get_spec_by_make(make_name_strict: str, df: pandas.DataFrame = None) -> pandas.DataFrame:
    return _filter_by('str_make', make_name_strict, df)


def dictify(df: pandas.DataFrame, top_n: int = 2) -> List[Dict[str, Any]]:
    result = []

    counter = 0
    for index, r in df.iterrows():
        if counter == top_n:
            break
        dictified = r.to_dict()
        dictified = {k: v for k, v in dictified.items() if pandas.notna(v)}
        result.append(dictified)
    return result


# def with_descriptions(df_dicted: List[str:Any]) -> List[Dict[str, Any]]:
#     result = [{cols_descriptions[k]: v for k, v in result_item.items()} for result_item in df_dicted]
#     return result


def get_list_of_models(df: pandas.DataFrame) -> List[str]:
    return sorted(list(set(df['str_model'].values.tolist())))


def get_list_of_makes(df: pandas.DataFrame = df_specs) -> List[str]:
    return sorted(list(set(df['str_make'].values.tolist())))


if __name__ == '__main__':
    print('MAKES: ', get_list_of_makes())
    levs_make = get_make_levenstain('Yamha')
    top1_make = levs_make[0] if levs_make else None

    df_make = get_specs_by_make(top1_make.key)
    print(f'MODELS for {top1_make.key}', get_list_of_models(df_make))

    levs_model = get_model_levenstain('R 1', df=df_make)
    top1_model = levs_model[0] if levs_model else None

    print(top1_make)
    print(top1_model)

    df = get_specs_by_model(top1_model.key, df_make)

    import pprint

    for d in dictify(df):
        pprint.pprint(d)

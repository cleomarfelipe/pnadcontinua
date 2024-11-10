import os
import shutil
import json
import requests
import polars as pl
from pnadcontinua.metadata import (
    SCHEMA, COLUMN_WIDTHS, VARIABLES_MAPPING, REGULAR_INCOME_GROUP
)
from pnadcontinua.constants import (
    DATA_FOLDER, TEMP_FOLDER, DATA_SOURCE_URL, DEFLATOR_SOURCE_URL
)
from pnadcontinua.utils import (
    download_zip_content_from_url, convert_fwf_to_parquet
)


CURRENT_DIR = os.path.dirname(__file__)
DATA_FOLDER_PATH = os.path.join(CURRENT_DIR, DATA_FOLDER)
TEMP_FOLDER_PATH = os.path.join(CURRENT_DIR, TEMP_FOLDER)


def get_quarter_data_urls():
    api_response = requests.get(DATA_SOURCE_URL).content
    api_response_json = json.loads(api_response)
    year_folders = [f for f in api_response_json if f["name"].isdigit()]
    quarter_file_urls = []
    for year_folder in year_folders:
        for quarter in year_folder["children"]:
            quarter_file_urls.append(quarter["url"])
    return quarter_file_urls


def download_data(file_url, variables):
    if variables:
        col_widths = {col: width for col, width in COLUMN_WIDTHS.items()
                      if col in variables}
        schema = {col: dtype for col, dtype in SCHEMA.items()
                  if col in variables}
    else:
        col_widths = {col: width for col, width in COLUMN_WIDTHS.items()}
        schema = {col: dtype for col, dtype in SCHEMA.items()}

    os.makedirs(DATA_FOLDER_PATH, exist_ok=True)
    if os.path.exists(TEMP_FOLDER_PATH):
        shutil.rmtree(TEMP_FOLDER_PATH)
    os.makedirs(TEMP_FOLDER_PATH)
    print(f"Downloading data...")
    download_zip_content_from_url(file_url, TEMP_FOLDER_PATH)
    file_name = os.listdir(TEMP_FOLDER_PATH)[0]
    fwf_file = os.path.join(TEMP_FOLDER_PATH, file_name)
    parquet_file = os.path.join(DATA_FOLDER_PATH, file_name[:-4] + ".parquet")
    parquet_file_temp = parquet_file + ".temp"
    convert_fwf_to_parquet(fwf_file, parquet_file_temp, col_widths, schema)
    os.replace(parquet_file_temp, parquet_file)
    os.remove(fwf_file)
    print("Download complete")


def load_data():
    return pl.scan_parquet(f"{DATA_FOLDER_PATH}/*.parquet")


def filter_cat_column(data, column, values):
    return data.filter(pl.col(column).is_in(values))


def filter_num_column(data, column, operation, value):
    if operation == "Igual a":
        return data.filter(pl.col(column) == value)
    elif operation == "Maior que":
        return data.filter(pl.col(column) > value)
    elif operation == "Menor que":
        return data.filter(pl.col(column) < value)
    elif operation == "Maior ou igual a":
        return data.filter(pl.col(column) >= value)
    elif operation == "Menor ou igual a":
        return data.filter(pl.col(column) <= value)


def count_total_expr():
    return (pl.col("V1028").sum().alias(f"qnt_pessoas"))


def ops_total_exprs(agg_list):
    agg_exprs = []
    for col, operation, deflator in agg_list:
        if deflator:
            col = col + "_def"
        if operation == "Soma":
            agg_exprs.append(
                ((pl.col(col) * pl.col("V1028")).sum()).alias(f"{col}_soma")
            )
        elif operation == "Média":
            agg_exprs.append(
                ((pl.col(col) * pl.col("V1028")).sum() / pl.col("V1028").sum())
                .alias(f"{col}_media")
            )
    return agg_exprs


def calculate_totals(data, group_cols, agg_list, include_count, deflator_data):
    if deflator_data is not None:
        data = data.join(
            deflator_data, on=["Ano", "Trimestre", "UF"], how="inner"
        )
        cols_to_def = set()
        for col, _, deflator in agg_list:
            if deflator:
                cols_to_def.add(col)
        for col in cols_to_def:
            def_type = "Habitual" if col in REGULAR_INCOME_GROUP else "Efetivo"
            data = data.with_columns(
                (pl.col(col) * pl.col(def_type)).alias(f"{col}_def")
            )
    agg_exprs = ops_total_exprs(agg_list)
    cnt_expr = None
    if include_count:
        cnt_expr = count_total_expr()
        agg_exprs.append(cnt_expr)
    result = data.group_by(group_cols).agg(agg_exprs).collect()
    for col in result.columns:
        if col in VARIABLES_MAPPING.keys():
            result = result.with_columns(
                pl.col(col)
                .cast(pl.Utf8)
                .replace(VARIABLES_MAPPING[col])
                .alias(col)
            )
    print(result)
    return result

def get_deflator():
    if os.path.exists(TEMP_FOLDER_PATH):
        shutil.rmtree(TEMP_FOLDER_PATH)
    os.makedirs(TEMP_FOLDER_PATH)
    download_zip_content_from_url(DEFLATOR_SOURCE_URL, TEMP_FOLDER_PATH)
    file_name = os.listdir(TEMP_FOLDER_PATH)[0]
    excel_file = os.path.join(TEMP_FOLDER_PATH, file_name)
    deflator = pl.read_excel(excel_file)
    os.remove(excel_file)
    quarters = {"01-02-03": 1, "04-05-06": 2, "07-08-09": 3, "10-11-12": 4}
    deflator = deflator.filter(pl.col("trim").is_in(quarters.keys()))
    deflator = deflator.with_columns(
        pl.col("trim").replace(quarters).alias("Trimestre").cast(pl.Int64),
        pl.col("Ano").cast(pl.Int64),
        pl.col("UF").cast(pl.Int64)
    )
    deflator = deflator.select(
        pl.col("Ano", "Trimestre", "UF", "Habitual", "Efetivo")
    )
    return deflator.lazy()

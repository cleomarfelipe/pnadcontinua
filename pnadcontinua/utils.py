import io
import zipfile
import requests
import textwrap
import pyarrow as pa
import pyarrow.parquet as pq
import polars as pl


def download_zip_content_from_url(url, folder):
    response = requests.get(url)
    if response.status_code != 200:
        return False
    zip = zipfile.ZipFile(io.BytesIO(response.content))
    zip.extractall(folder)
    return True


def save_parquet_from_rows(rows, col_names, parquet_writer, dtypes):
    df = pl.DataFrame(rows, orient='row')
    df.columns = col_names
    df = df.cast(dtypes, strict=False)
    parquet_writer.write_table(df.to_arrow())


def convert_fwf_to_parquet(fwf_file, parquet_file, columns, schema):
    names = list(columns.keys())
    widths = list(columns.values())
    chunk_size = 50_000
    parquet_writer = pq.ParquetWriter(parquet_file, pa.schema(schema))
    dtypes = {col: getattr(pl, dtype) for col, dtype in schema.items()}
    with open(fwf_file, 'r') as f_in:
        rows = []
        for line in f_in:
            row = [line[start:end].strip() for start, end in widths]
            rows.append(row)
            if len(rows) >= chunk_size:
                save_parquet_from_rows(rows, names, parquet_writer, dtypes)
                rows = []
        if len(rows) > 0:
            save_parquet_from_rows(rows, names, parquet_writer, dtypes)
    parquet_writer.close()


def get_vars_from_bin_dict(bin_dict):
    return [k for k, v in bin_dict.items() if v == 1]


def wrap_string(text, max_length):
    return textwrap.fill(text, width=max_length)


def get_var_desc(vars_desc, var, show_var=True):
    if show_var:
        return f"[{var}] {vars_desc[var]}"
    return vars_desc[var]


def has_duplicates(list_):
    aux = []
    for e in list_:
        if e not in aux:
            aux.append(e)
    return len(list_) != len(aux)


def is_numeric(value):
    try:
        float(value)
        return True
    except:
        return False

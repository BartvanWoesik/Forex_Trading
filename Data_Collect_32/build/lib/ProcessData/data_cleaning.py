import pandas as pd


def collect_data(data_path: str) -> pd.DataFrame:
    df = pd.read_csv(data_path)
    df = df.fillna(0)
    return df


def round_label(df: pd.DataFrame) -> pd.DataFrame:
    assert "Label" in df.columns
    df["Label"] = round(df["Label"], 3)
    return df


def drop_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["Datum", "Label"])
    return df


def make_group(df: pd.DataFrame) -> pd.DataFrame:
    df["Group_column"] = df["Datum"].apply(lambda x: x.split()[0])
    return df


def add_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.reset_index()
    return df


def check_is_in_time(df: pd.DataFrame) -> pd.DataFrame:
    _df = df[df["is_in_time"] == 1]
    _df = _df.reset_index()
    return _df


def extract_y(df: pd.DataFrame()) -> pd.DataFrame:
    df["y"] = df["Label"]
    return df


def shift_close(df: pd.DataFrame) -> pd.DataFrame:
    _df = df.copy()
    _df["next_close_price"] = df["close_price"].shift(-1)
    _df["next_open_price"] = df["open_price"].shift(-1)
    return _df


def create_label(df: pd.DataFrame) -> pd.DataFrame:
    _df = df.copy()
    diff = _df["next_close_price"] - _df["close_price"]
    _df["diff"] = diff * 1000
    _df["sample_weight"] = [
        2.1 if ((x >= -4.0) | (x < 3.0)) else 1 for x in _df["diff"]
    ]
    _df["y"] = (diff >= 0.001).astype(int)
    return _df


def drop_empty_window(df: pd.DataFrame) -> pd.DataFrame:
    _df = df.copy()
    return _df.dropna()

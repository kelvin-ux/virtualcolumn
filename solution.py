import pandas as pd
import re

VALID_COLUMN_NAME_PATTERN = re.compile(r'^[a-zA-Z_]+$')
VALID_OPERATORS = {"+", "-", "*"}
TOKEN_PATTERN = re.compile(r'[a-zA-Z_]+|[+\-*]')


def _validate_column_name(column_name: str) -> bool:
    return VALID_COLUMN_NAME_PATTERN.match(column_name) is not None


def _extract_tokens(expression: str) -> list[str]:
    return TOKEN_PATTERN.findall(expression)


def _validate_expression(expression: str) -> bool:
    tokens = _extract_tokens(expression)
    return all(_validate_column_name(token) or token in VALID_OPERATORS for token in tokens)


def _validate_columns_exist(tokens: list[str], df: pd.DataFrame) -> bool:
    return all(token in df.columns for token in tokens if _validate_column_name(token))


def add_virtual_column(df: pd.DataFrame, role: str, new_column: str) -> pd.DataFrame:
    if not _validate_column_name(new_column):
        return pd.DataFrame()

    role = role.strip()

    if not _validate_expression(role):
        return pd.DataFrame()

    tokens = _extract_tokens(role)
    if not _validate_columns_exist(tokens, df):
        return pd.DataFrame()

    try:
        result_df = df.copy()
        result_df[new_column] = result_df.eval(role)
        return result_df
    except (SyntaxError, KeyError, ValueError):
        return pd.DataFrame()
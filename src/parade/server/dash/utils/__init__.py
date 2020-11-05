from datetime import datetime

from cerberus import Validator


def validate(document, schema, **validator_kwargs):
    """Validate a data structure. Return errors if any found.

    Cerberus Documentation: https://docs.python-cerberus.org/en/stable/validation-rules.html

    Args:
        document: data structure to validate
        schema: expected structure
        validator_kwargs: additional keyword arguments for Validator class

    Returns:
        list: validation errors

    """
    validator = Validator(schema, **validator_kwargs)
    validator.validate(document)
    return validator.errors


# ----------------------------------------------------------------------------------------------------------------------
# Time Helpers

US_TIME_FORMAT = '%m/%d/%Y %H:%M:%S'
"""String time format with month/year (MM/DD/YYYY HH:MM:SS)."""

DASHED_TIME_FORMAT_US = '%m-%d-%Y %H:%M:%S'
"""Dashed time format with month first (MM-DD-YYYY HH:MM:SS)."""

DASHED_TIME_FORMAT_YEAR = '%Y-%m-%d %H:%M:%S'
"""Dashed time format with year first (YYYY-MM-DD HH:MM:SS)."""

TIME_FORMAT_FILE = '%Y-%m-%d_%H%M%S'
"""Filename-safe time format with year first (YYYY-MM-DD_HHMMSS)."""

GDP_TIME_FORMAT = '%d%b%Y %H:%M:%S'
"""Good Documentation Practice time format (DDMMMYYYY HH:MM:SS)."""


def get_unix(str_ts, date_format):
    """Get unix timestamp from a string timestamp in date_format.

    Args:
        str_ts: string timestamp in `date_format`
        date_format: datetime time stamp format

    Returns:
        int: unix timestamp

    """
    return datetime.strptime(str_ts, date_format).timestamp()


def format_unix(unix_ts, date_format):
    """Format unix timestamp as a string timestamp in date_format.

    Args:
        unix_ts: unix timestamp
        date_format: datetime time stamp format

    Returns:
        string: formatted timestamp in `date_format`

    """
    return datetime.fromtimestamp(unix_ts).strftime(date_format)


# ----------------------------------------------------------------------------------------------------------------------

FIGURE_PLACEHOLDER = {'data': [], 'layout': {}, 'frames': []}
"""Figure placeholder."""

import dash_core_components as dcc


def min_graph(config=None, figure=FIGURE_PLACEHOLDER, **kwargs):
    """Return dcc.Graph element with Plotly overlay removed.

    See: https://community.plot.ly/t/is-it-possible-to-hide-the-floating-toolbar/4911/7

    Args:
        config: dictionary passed to `dcc.Graph`. Default is to disable the `displayModeBar`
        figure: figure argument. Default is an empty placeholder (`FIGURE_PLACEHOLDER`)
        kwargs: any kwargs to pass to the dash initializer other than `assets_folder`

    Returns:
        dict: Dash `dcc.Graph` object

    """
    if config is None:
        config = {'displayModeBar': False}
    return dcc.Graph(config=config, figure=figure, **kwargs)

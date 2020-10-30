import dash
import yaml

from parade.core.context import Context
from . import Dashboard


class YamlDashboard(Dashboard):
    """
    SimpleDashboard adds some strong constraints to dashboard system.
    In SimpleDashboard, we assume the dashboard contains two section:
    **Filters** and **Widgets**.

    Filter section contains one or more filters to compose a filter-chain
    with the last one as **trigger**. When the trigger filter is fired,
    one or several data frame will be retrieved and cached to render
    the widget section.

    Widget section is used to layout all visualized widgets. All these
    widget is rendered with a single data frame cached and retrieved
    when trigger filter is fired.
    """

    def __init__(self, app: dash.Dash, context: Context):
        Dashboard.__init__(self, app, context)
        config_dict = YamlDashboard.load_config('test.yaml')
        layout_dict = config_dict['layout']



    @staticmethod
    def load_config(config_path):
        return yaml.safe_load(open(config_path))

    @staticmethod
    def parse_rows(rows):
        for row in rows:


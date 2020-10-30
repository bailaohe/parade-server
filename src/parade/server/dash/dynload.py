import dash
import dash_html_components as html
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
        self.config_dict = self.load_config()
        self.layout_dict = YamlDashboard.parse_rows(self.config_dict['layout'])

    @property
    def display_name(self):
        """
        get the display name of the dashboard
        :return: the display name of the dashboard
        """
        return self.config_dict['displayName']

    def load_config(self):
        raise NotImplementedError("The target is required")
        # return yaml.safe_load(open(config_path))

    @staticmethod
    def parse_rows(rows):
        rows_layout = []
        for row in rows:
            row_layout = YamlDashboard.parse_row(row['columns'])
            rows_layout.append(html.Div(row_layout, className='parade-row'))

        return rows_layout

    @staticmethod
    def parse_row(row):
        row_layout = []
        for col in row:
            col_width = col['width']
            col_type = col['type']
            if col_type == 'widget':
                row_layout.append(html.Div('widget', className='parade-widget ' + col_width))
            elif col_type == 'segment':
                row_layout.append(html.Div('segment', className=col_width))
            elif col_type == 'row-container':
                sub_rows_layout = YamlDashboard.parse_rows(col['rows'])
                row_layout.append(html.Div(sub_rows_layout, className='parade-col ' + col_width))
        return row_layout

    @property
    def layout(self):
        """
        get the dash-layout segment of the dashboard
        :return: the dash-layout segment of the dashboard
        """
        return self.layout_dict;

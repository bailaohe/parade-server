import dash
import dash_html_components as html
from flask_caching import Cache

from parade.core.context import Context


class Dashboard(object):

    def __init__(self, app: dash.Dash, context: Context):
        self.app = app
        self.context = context

        self.cache = Cache(app.server, config={
            # Note that filesystem cache doesn't work on systems with ephemeral
            # filesystems like Heroku.
            'CACHE_TYPE': 'filesystem',
            'CACHE_DIR': 'cache-directory',

            # should be equal to maximum number of users on the app at a single time
            # higher numbers will store more data in the filesystem / redis cache
            'CACHE_THRESHOLD': 200
        })

    @property
    def name(self):
        """
        get the identifier of the dashboard, the default is the class name of dashboard
        :return: the dashboard identifier
        """
        return self.__module__.split('.')[-1]

    @property
    def display_name(self):
        """
        get the display name of the dashboard
        :return: the display name of the dashboard
        """
        return self.name

    @property
    def layout(self):
        """
        get the dash-layout segment of the dashboard
        :return: the dash-layout segment of the dashboard
        """
        return html.Div([html.H1('Content of dashboard [' + self.name + ']')])


class ConfigurableDashboard(Dashboard):
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
        self.layout_dict = ConfigurableDashboard.parse_rows(self.config_dict['layout'])

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
            row_layout = ConfigurableDashboard.parse_row(row['columns'])
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
                sub_rows_layout = ConfigurableDashboard.parse_rows(col['rows'])
                row_layout.append(html.Div(sub_rows_layout, className='parade-col ' + col_width))
        return row_layout

    @property
    def layout(self):
        """
        get the dash-layout segment of the dashboard
        :return: the dash-layout segment of the dashboard
        """
        return self.layout_dict

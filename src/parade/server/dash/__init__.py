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


from importlib import import_module

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output
from flask_caching import Cache
from flask_login import current_user
import uuid

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
        self.parsed_layout = self.parse_rows(self.config_dict['layout'])
        self.init_component_subscription()

    @property
    def display_name(self):
        """
        get the display name of the dashboard
        :return: the display name of the dashboard
        """
        return self.config_dict['displayName']

    def load_config(self):
        """
        load the config into dict and return
        :return: the loaded config dict
        """
        raise NotImplementedError("The target is required")

    def parse_rows(self, rows):
        """
        parse the rows in the layout
        :param rows: the array of row layout config items
        :return: the parsed rows layout
        """
        rows_layout = []
        for row in rows:
            row_layout = self.parse_row(row['columns'])
            rows_layout.append(html.Div(row_layout, className='parade-row'))

        return rows_layout

    def parse_row(self, row):
        """
        parse the single row layout
        :param row: the single row layout config item
        :return: the parsed single row layout
        """
        row_layout = []
        for col in row:
            col_width = col['width']
            col_type = col['type']
            if col_type == 'container':
                sub_rows_layout = self.parse_rows(col['rows'])
                row_layout.append(html.Div(sub_rows_layout, className='parade-col ' + col_width))
            elif col_type == 'component':
                if 'component' in col:
                    row_layout.append(html.Div(self.parse_component(col['component']),
                                               className='parade-widget ' + col_width))
                else:
                    row_layout.append(html.Div(['HOLDER', html.Br(), col_width],
                                               className='parade-widget ' + col_width))
            else:
                row_layout.append(html.Div('', className=col_width))

        return row_layout

    def parse_component(self, comp_key):
        """
        parse the component layout
        :param comp_key: the component key
        :return: the parsed component
        """
        if comp_key in self.config_dict['components']:
            auto_render = 'subscribes' not in self.config_dict or comp_key not in self.config_dict['subscribes']
            component = self.config_dict['components'][comp_key]
            comp_data = self._load_component_data(component) if auto_render else []
            component_id = self.name + '_' + comp_key

            if component['type'] == 'filter':
                return dcc.Dropdown(
                    id=component_id,
                    #options=self._load_component_data(component) if auto_render else [{'label': '-', 'value': '-'}],
                    options=comp_data,
                    value=None,
                    clearable=False,
                    # placeholder='placeholder'
                )
            elif component['type'] == 'widget':
                return html.Div([], id=component_id)
            return 'children'
        return 'INVALID COMPONENT [' + comp_key + ']'

        # import plotly.figure_factory as ff
        # if comp_key in self.config_dict['components']:
        #     df = [dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28'),
        #           dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15'),
        #           dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30')]
        #
        #     fig = ff.create_gantt(df, title='FUCK gantt')
        #
        #     return dcc.Graph(
        #         id=self.name + '_' + comp_key,
        #         config=dict(displayModeBar=False),
        #         figure=fig
        #     )

    def init_component_subscription(self):
        def _get_input_field(comp_key):
            if comp_key in self.config_dict['components']:
                component = self.config_dict['components'][comp_key]
                if component['type'] == 'filter':
                    return 'options'
                elif component['type'] == 'widget':
                    return 'children'
                return 'children'
            return None

        def _get_output_field(comp_key):
            return 'value'

        subscribes = self.config_dict['subscribes'] if 'subscribes' in self.config_dict else dict()
        for (output_key, inputs) in subscribes.items():
            add_callback = self.app.callback(Output(self.name + '_' + output_key, _get_input_field(output_key)),
                                             [Input(self.name + '_' + input_item['key'],
                                                    _get_output_field(input_item['key']))
                                              for input_item in inputs])

            input_as = [input_item['as'] for input_item in inputs]
            add_callback(self._render_component_func(output_key, input_as))

    def _load_component_data(self, comp, **kwargs):
        import pandas as pd
        import json
        raw_data = self.context.get_task(comp['task']).execute_internal(self.context, **kwargs)

        if isinstance(raw_data, pd.DataFrame):
            data = json.loads(raw_data.to_json(orient='records'))
        else:
            data = raw_data

        return data

    def _render_component(self, comp, data):
        if 'subtype' in comp and comp['subtype'] == 'table':
            import pandas as pd
            df = pd.DataFrame.from_records(data)
            return dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in df.columns],
            )
        return data

    def _render_component_func(self, comp_key, input_arg_names):
        import functools

        def render_func_generator(key, *args):
            kwargs = dict(zip(input_arg_names, args))
            comp = self.config_dict['components'][key]
            cached = 'cache' in comp and comp['cache'] == 'true'

            if not cached:
                comp_data = self._load_component_data(comp, **kwargs)
            else:
                # set the default cache timeout to 10 seconds
                cache = self.cache
                @cache.memoize(timeout=10)
                def reload_data(cache_key):
                    data = self._load_component_data(comp, **kwargs)
                    return data

                param_key = ''
                for param in sorted(kwargs.keys()):
                    if kwargs.get(param):
                        param_key += '-' + kwargs.get(param)

                # If we enable auth check then we can get our user id & session id from current_user
                cache_key = self.name + '-' + key + '-' + param_key
                if current_user is not None:
                    session_id = current_user.token
                    cache_key = self.name + '-' + session_id + '-' + key + '-' + param_key
                comp_data = reload_data(cache_key)

            if 'convert' in comp:
                dash_mod = import_module(self.context.name + '.dashboard')
                output_processor = getattr(dash_mod, '_processor_' + comp['convert'])
                comp_data = output_processor(comp_data)

            output = self._render_component(comp, comp_data)

            return output

        return functools.partial(render_func_generator, comp_key)

    @property
    def layout(self):
        """
        get the dash-layout segment of the dashboard
        :return: the dash-layout segment of the dashboard
        """

        # Initialize session id & user id
        session_id = str(uuid.uuid4())
        user_id = None

        # If we enable auth check then we can get our user id & session id from current_user
        if current_user is not None:
            session_id = current_user.token
            user_id = current_user.id

        layout = []
        layout.extend(self.parsed_layout)
        layout.append(html.Div(session_id, id=self.name + '_session-id', style={'display': 'none'}))
        layout.append(html.Div(user_id, id=self.name + '_user-id', style={'display': 'none'}))

        return layout

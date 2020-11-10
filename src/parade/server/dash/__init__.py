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
from parade.server.dash.utils import min_graph


class Dashboard(object):

    def __init__(self, app: dash.Dash, context: Context, **kwargs):
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


class DashboardComponent(object):
    def __init__(self, context):
        self.context = context

    def init_layout(self, component_id, component, data):
        pass

    def refresh_layout(self, component, data):
        pass


class ConfigurableDashboard(Dashboard):
    """
    ConfigurableDashboard adds some strong constraints to dashboard system.
    In ConfigurableDashboard, we assume every dashboard can be describe with
    three kind of info: **Layout**, **Components**, and *Subscriptions*.

    Layout describes the position information of all components in the
    dashboard.

    Components is the core parts of a dashboard. They retrieve the backend
    data and render the output in different widgets (charts / table). They
    can be divided into two categories: **Filters** and **Widgets**. Filters
    act as **trigger** to fire the output rendering of other widgets.

    Subscriptions indicate the data subscription relationship from filters to
    widgets.
    """

    def __init__(self, app: dash.Dash, context: Context, **kwargs):
        Dashboard.__init__(self, app, context)
        self.config_name = kwargs.get('config_name', None)
        self.config_dict = kwargs.get('config', None)
        if not self.config_dict:
            self.config_dict = self.load_config()
        self.parsed_layout = self.parse_layout()
        self.init_component_subscription()

    @property
    def name(self):
        """
        get the identifier of the dashboard, the default is the class name of dashboard
        :return: the dashboard identifier
        """
        return self.config_name or self.__module__.split('.')[-1]

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

    def parse_layout(self):
        layout = []
        if 'components' in self.config_dict:
            for comp_key, comp in self.config_dict['components'].items():
                if comp['type'] == 'store':
                    store_id = self.name + '_' + comp_key
                    store_type = comp.get('subType', 'session')
                    assert store_type in ('local', 'session', 'memory'), 'invalid store type'
                    layout.append(dcc.Store(id=store_id, storage_type=store_type))
        layout.extend(self.parse_rows(self.config_dict['layout']))
        return layout

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
                    row_layout.append(html.Div(self.init_component(col['component']),
                                               className='parade-widget ' + col_width))
                else:
                    row_layout.append(html.Div(['HOLDER', html.Br(), col_width],
                                               className='parade-widget ' + col_width))
            else:
                row_layout.append(html.Div('', className=col_width))

        return row_layout

    def init_component(self, comp_key):
        """
        parse the component layout
        :param comp_key: the component key
        :return: the parsed component
        """

        def loading_wrapper(comp_id, layout):
            return dcc.Loading(
                id=comp_id + "-loading",
                children=layout,
                type="circle",
            )

        def demo_map():
            import plotly.graph_objects as go
            import json
            import pandas as pd
            from os.path import join
            import numpy as np

            dataset_dir = join(self.context.workdir, 'dataset')

            with open(join(dataset_dir, "china_province.geojson")) as f:
                provinces_map = json.load(f)

            df = pd.read_csv(join(dataset_dir, 'data_radar.csv'))
            df['确诊_log'] = df.确诊.map(np.log)
            fig = go.Figure(
                go.Choroplethmapbox(
                    featureidkey="properties.NL_NAME_1",
                    geojson=provinces_map,
                    locations=df.地区,
                    z=df.确诊_log,
                    zauto=True,
                    colorscale='viridis',
                    reversescale=False,
                    marker_opacity=0.8,
                    marker_line_width=0.8,
                    customdata=np.vstack((df.地区, df.确诊, df.疑似, df.治愈, df.死亡)).T,
                    hovertemplate="<b>%{customdata[0]}</b><br><br>"
                                  + "确诊：%{customdata[1]}<br>"
                                  + "疑似：%{customdata[2]}<br>"
                                  + "治愈：%{customdata[3]}<br>"
                                  + "死亡：%{customdata[4]}<br>"
                                  + "<extra></extra>",
                    showscale=True,
                ),
            )
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox_zoom=3,
                mapbox_center={"lat": 37.110573, "lon": 106.493924},
                height=800
            )
            config = {'displayModeBar': False}
            return dcc.Graph(config=config, figure=fig)

        if comp_key in self.config_dict['components']:
            component = self.config_dict['components'][comp_key]
            auto_render = 'subscribes' not in self.config_dict or comp_key not in self.config_dict['subscribes']
            comp_data = self._load_component_data(component) if auto_render else []
            component_id = self.name + '_' + comp_key

            assert component['type'] != 'store', 'the component to render cannot be of type store'

            if component['type'] == 'filter':
                return self._init_component_filter(component_id, component, comp_data)
            if component['type'] == 'chart':
                return loading_wrapper(component_id, self._init_component_chart(component_id, component, comp_data))
            if component['type'] == 'table':
                return loading_wrapper(component_id, self._init_component_table(component_id, component, comp_data))
            if component['type'] == 'map':
                return demo_map()

            return html.Div(id=component_id)
        return 'INVALID COMPONENT [' + comp_key + ']'

    def init_component_subscription(self):
        def _get_input_field(comp_key):
            if comp_key in self.config_dict['components']:
                component = self.config_dict['components'][comp_key]
                if component['type'] == 'filter':
                    return 'options'
                if component['type'] == 'widget':
                    return 'children'
                if component['type'] == 'store':
                    return 'data'
                return 'children'
            return None

        def _get_output_field(comp_key):
            if comp_key in self.config_dict['components']:
                component = self.config_dict['components'][comp_key]
                if component['type'] == 'store':
                    return 'data'
                return 'value'
            return None

        subscribes = self.config_dict['subscribes'] if 'subscribes' in self.config_dict else dict()
        for (output_key, inputs) in subscribes.items():
            output_id = self.name + '_' + output_key
            add_callback = self.app.callback(Output(output_id, _get_input_field(output_key)),
                                             [Input(self.name + '_' + input_item['key'],
                                                    _get_output_field(input_item['key']))
                                              for input_item in inputs])

            input_as = [input_item['as'] for input_item in inputs]
            add_callback(self._render_component_func(output_key, input_as))

    def _load_component_data(self, comp, **kwargs):
        import pandas as pd
        import json

        if 'task' in comp:
            raw_data = self.context.get_task(comp['task']).execute_internal(self.context, **kwargs)
        else:
            assert comp['type'] != 'store', 'the task of store is *REQUIRED*'
            raw_data = kwargs.get('data', [])

        if isinstance(raw_data, pd.DataFrame):
            data = json.loads(raw_data.to_json(orient='records'))
        else:
            data = raw_data

        return data

    def _render_component(self, comp, data):
        if comp['type'] == 'filter':
            return self._render_component_filter(comp, data)
        if comp['type'] == 'table':
            return self._render_component_table(comp, data)
        if comp['type'] == 'chart':
            return self._render_component_chart(comp, data)
        return data

    def _render_component_filter(self, component, data):
        assert component['type'] == 'filter', 'invalid filter component'
        from .filter import load_filter_component_class
        filter_class = load_filter_component_class(self.context, component['subType'])
        filter_main = filter_class(self.context)
        return filter_main.refresh_layout(component, data)

    def _init_component_filter(self, filter_id, component, data):
        assert component['type'] == 'filter', 'invalid filter component'
        from .filter import load_filter_component_class
        filter_class = load_filter_component_class(self.context, component['subType'])
        filter_main = filter_class(self.context)
        return filter_main.init_layout(filter_id, component, data)

    def _render_component_chart(self, chart, data):
        assert chart['type'] == 'chart', 'invalid chart component'
        from .chart import load_chart_component_class
        chart_class = load_chart_component_class(self.context, chart['subType'])
        chart_main = chart_class(
            self.context,
            title=chart['title'],
            xlabel=None,
            ylabel=None,
        )
        return chart_main.refresh_layout(chart, data)

    def _init_component_chart(self, chart_id, chart, data):
        assert chart['type'] == 'chart', 'invalid chart component'
        from parade.server.dash.chart import load_chart_component_class
        chart_class = load_chart_component_class(self.context, chart['subType'])
        chart_main = chart_class(
            self.context,
            title=chart['title'],
            xlabel=None,
            ylabel=None,
        )
        return chart_main.init_layout(chart_id, chart, data)

    def _init_component_table(self, table_id, table, data):
        assert table['type'] == 'table', 'invalid table component'
        from .table import load_table_component_class
        table_class = load_table_component_class(self.context, table['subType'] if 'subType' in table else 'core')
        table_main = table_class(self.context)
        return table_main.init_layout(table_id, table, data)

    def _render_component_table(self, table, df):
        assert table['type'] == 'table', 'invalid table component'
        from .table import load_table_component_class
        table_class = load_table_component_class(self.context, table['subType'] if 'subType' in table else 'core')
        table_main = table_class(self.context)
        return table_main.refresh_layout(table, df)

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
                output_processor = getattr(dash_mod, '_converter_' + comp['convert'])
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

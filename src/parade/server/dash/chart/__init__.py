import plotly.graph_objects as go

from .. import DashboardComponent
from ..utils import validate, min_graph


class CustomChart(DashboardComponent):  # noqa: H601
    """Base Class for Custom Charts."""

    annotations = []
    """Store annotations. Default is an empty list.

    See documentation: https://plot.ly/python/reference/#layout-annotations

    """

    _axis_range = {}
    _axis_range_schema = {
        'x': {
            'items': [{'type': ['integer', 'float', 'string']}, {'type': ['integer', 'float', 'string']}],
            'required': False,
            'type': 'list',
        },
        'y': {
            'items': [{'type': ['integer', 'float']}, {'type': ['integer', 'float']}],
            'required': False,
            'type': 'list',
        },
    }

    @property
    def axis_range(self):
        """Specify x/y axis range or leave as empty dictionary for autorange.

        Returns:
            dict: dictionary potentially with keys `(x, y)`

        """
        return self._axis_range

    @axis_range.setter
    def axis_range(self, axis_range):
        errors = validate(axis_range, self._axis_range_schema)
        if errors:
            raise RuntimeError(f'Validation of self.axis_range failed: {errors}')
        # Assign new axis_range
        self._axis_range = axis_range

    def __init__(self, context, *, title, xlabel, ylabel, layout_overrides=()):
        """Initialize Custom Dash Chart and store parameters as data members.

        Args:
            title: String title for chart (can be an empty string for blank)
            xlabel: XAxis string label (can be an empty string for blank)
            ylabel: YAxis string label (can be an empty string for blank)
            layout_overrides: Custom parameters in format [ParentKey, SubKey, Value] to customize 'go.layout'

        """
        super(CustomChart, self).__init__(context)
        self.title = title
        self.labels = {'x': xlabel, 'y': ylabel}
        self.layout_overrides = layout_overrides
        self.initialize_mutables()

    def initialize_mutables(self):
        """Initialize the mutable data members to prevent modifying one attribute and impacting all instances."""
        pass

    def create_figure(self, df_raw, **kwargs_data):
        """Create the figure dictionary.

        Args:
            df_raw: data to pass to formatter method
            kwargs_data: keyword arguments to pass to the data formatter method

        Returns:
            dict: keys `data` and `layout` for Dash

        """
        return {
            'data': self.create_traces(df_raw, **kwargs_data),
            'layout': go.Layout(self.apply_custom_layout(self.create_layout(df_raw))),
        }

    def create_traces(self, df_raw, **kwargs_data):
        """Return traces for plotly chart.

        Should return, list: trace data points. List may be empty

        Args:
            df_raw: data to pass to formatter method
            kwargs_data: keyword arguments to pass to the data formatter method

        Raises:
            NotImplementedError: Must be overridden by child class

        """
        raise NotImplementedError('create_traces must be implemented by child class')  # pragma: no cover

    def create_layout(self, df_raw, **kwargs):
        """Return the standard layout. Can be overridden and modified when inherited.

        Returns:
            dict: layout for Dash figure

        """
        layout = {
            'annotations': self.annotations,
            # 'title': go.layout.Title(text=self.title),
            'xaxis': {
                'automargin': True,
                'title': self.labels['x'],
            },
            'yaxis': {
                'automargin': True,
                'title': self.labels['y'],
                'zeroline': True,
            },
            'legend': {'orientation': 'h', 'y': -0.25},  # below XAxis label
            'hovermode': 'closest',
        }

        # Optionally apply the specified range
        for axis in ['x', 'y']:
            axis_name = f'{axis}axis'
            if axis in self.axis_range:
                layout[axis_name]['range'] = self.axis_range[axis]
            else:
                layout[axis_name]['autorange'] = True

        return layout

    def apply_custom_layout(self, layout):
        """Extend and/or override layout with custom settings.

        Args:
            layout: base layout dictionary. Typically from self.create_layout()

        Returns:
            dict: layout for Dash figure

        """
        for parent_key, sub_key, value in self.layout_overrides:
            if sub_key is not None:
                layout[parent_key][sub_key] = value
            else:
                layout[parent_key] = value

        return layout

    def refresh_layout(self, chart, data):
        import dash_html_components as html
        render_output = [
            html.H4(children=chart['title'], style={
                'text-align': 'center'
            }),
        ]
        if len(data) > 0:
            fig = self.create_figure(df_raw=data, **chart['args']) if 'args' in chart and chart[
                'args'] else self.create_figure(df_raw=data)
            render_output.append(min_graph(figure=fig))
        return render_output

    def init_layout(self, chart_id, chart, data):
        import dash_html_components as html
        if len(data) == 0:
            return html.Div(id=chart_id)
        return html.Div(self.refresh_layout(chart, data), id=chart_id)


_driver_class_cache = {}


def load_chart_component_class(context, driver):
    from parade.utils.modutils import iter_classes
    if driver not in _driver_class_cache:
        for chart_class in iter_classes(CustomChart, 'parade.server.dash.chart', context.name + '.dashboard.chart',
                                        class_filter=lambda cls: cls != CustomChart):
            chart_key = chart_class.__module__.split('.')[-1]
            if chart_key not in _driver_class_cache:
                _driver_class_cache[chart_key] = chart_class
    return _driver_class_cache[driver]

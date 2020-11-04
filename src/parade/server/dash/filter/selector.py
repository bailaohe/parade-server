from . import CustomFilter
import dash_core_components as dcc
import dash_html_components as html


class Selector(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return dcc.Dropdown(
            id=filter_id,
            # options=self._load_component_data(component) if auto_render else [{'label': '-', 'value': '-'}],
            options=data,
            value=None,
            clearable=False,
            placeholder=component['title']
        )

    def refresh_layout(self, component, data):
        return data

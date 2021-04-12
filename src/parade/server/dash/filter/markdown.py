from . import CustomFilter
import dash_core_components as dcc
import dash_html_components as html
from parade.server.dash.utils.dictUtils import get_or_default


class MarkDown(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return [
            dcc.Markdown(
                id=filter_id,
                className=get_or_default(component, "className", None),
                style=get_or_default(component, "style", None),
                children=data,
            ),
        ]

    def refresh_layout(self, component, data):
        return data

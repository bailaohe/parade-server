from . import CustomFilter
import dash_core_components as dcc
from ..utils.dictUtils import get_or_default


class Selector(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return dcc.Dropdown(
            id=filter_id,
            options=data,
            clearable=get_or_default(component,"clearable",False),
            placeholder=get_or_default(component, "title", None),
            className=get_or_default(component, "className", None),
            multi=get_or_default(component,"multi",False)
        )

    def refresh_layout(self, component, data):
        return data

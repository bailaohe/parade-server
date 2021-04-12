from . import CustomFilter
import dash_core_components as dcc
from ..utils.dictUtils import get_or_default


class InputText(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return dcc.Input(
            id=filter_id,
            type=get_or_default(component, "input_type", "text"),
            placeholder=get_or_default(component, "placeholder", ""),
            value=data,
            className=get_or_default(component, "className", None),
            style=get_or_default(component, "style", None),
            debounce=True if get_or_default(component,"debounce","True") == "True" else False

        )

    def refresh_layout(self, component, data):
        return data

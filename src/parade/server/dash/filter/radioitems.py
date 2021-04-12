from . import CustomFilter
import dash_core_components as dcc
from ..utils.dictUtils import get_or_default


class RadioItems(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return dcc.RadioItems(
            id=filter_id,
            options=data,
            value=[],
            style=get_or_default(component, "style", None),
            inputStyle=get_or_default(component, "inputStyle", None),
            inputClassName=get_or_default(component, "inputClassName", None),
            labelStyle=get_or_default(component, "labelStyle", None),
            labelClassName=get_or_default(component, "labelClassName", None),
            className=get_or_default(component, "className", None)

        )

    def refresh_layout(self, component, data):
        return data

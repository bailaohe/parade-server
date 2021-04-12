from parade.server.dash.filter import CustomFilter
import dash_core_components as dcc
from ..utils.dictUtils import get_or_default


class Slide(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return dcc.Slider(
            id=filter_id,
            className=get_or_default(component, "className", None),
            min=get_or_default(component, "min", 0),
            max=get_or_default(component, "min", 100),
            step=get_or_default(component, "step", 1),
            value=int(data[0]) if data != [] and data is not None else 0,

        )

    def refresh_layout(self, component, data):
        return data

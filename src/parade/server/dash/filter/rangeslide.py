from parade.server.dash.filter import CustomFilter
import dash_core_components as dcc

from ..utils.dictUtils import get_or_default


class RangeSlide(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return dcc.RangeSlider(
                id=filter_id,
                className=get_or_default(component,"className",None),
                min=get_or_default(component,"min",0),
                max=get_or_default(component,"max",100),
                value=data if data is not None and len(data) == 2 else [0,100],
                step=get_or_default(component,"step",1)

            )

    def refresh_layout(self, component, data):
        return data

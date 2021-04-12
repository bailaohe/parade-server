from . import CustomFilter
import dash_core_components as dcc
import dash_html_components as html
from ..utils.dictUtils import get_or_default


class DateRangePicker(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return [
            dcc.DatePickerRange(
                id=filter_id,
                className=get_or_default(component, "className", None),
                style=get_or_default(component, "style", None),
                clearable=get_or_default(component,"clearable",False),
                min_date_allowed=get_or_default(component, "min_date_allowed", None),
                max_date_allowed=get_or_default(component, "max_date_allowed", None),
                calendar_orientation=get_or_default(component, "calendar_orientation","horizontal")

            ),
        ]

    def refresh_layout(self, component, data):
        return data

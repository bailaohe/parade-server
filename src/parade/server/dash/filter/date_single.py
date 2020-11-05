from . import CustomFilter
import dash_core_components as dcc
import dash_html_components as html


class DateSinglePicker(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return [
            dcc.DatePickerSingle(
                id=filter_id,
                placeholder=component['title'],
                style={
                    'width': '100%'
                }
            ),
        ]

    def refresh_layout(self, component, data):
        return data

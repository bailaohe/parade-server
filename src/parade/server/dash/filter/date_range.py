from . import CustomFilter
import dash_core_components as dcc
import dash_html_components as html


class DateRangePicker(CustomFilter):
    def init_layout(self, filter_id, component, data):
        return [
            dcc.DatePickerRange(
                id=filter_id,
                # min_date_allowed=date(1995, 8, 5),
                # max_date_allowed=date(2017, 9, 19),
                # initial_visible_month=date(2017, 8, 5),
                # end_date=date(2017, 8, 25)
                style={
                    'float': 'right'
                }
            ),
            html.Label(component['title'], style={
                'margin-right': 10,
                'line-height': 48
            })
        ]

    def refresh_layout(self, component, data):
        return data

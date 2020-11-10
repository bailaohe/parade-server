import dash_table

from . import CustomTable

import dash_html_components as html


class CoreTable(CustomTable):

    def refresh_layout(self, table, df):
        assert table['type'] == 'table', 'invalid chart component'
        return html.Div(
            dash_table.DataTable(
                data=df.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in df.columns],
                style_cell={'textAlign': 'left'},
            ))

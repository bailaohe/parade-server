import dash_table

from . import CustomTable

import dash_html_components as html


class CoreTable(CustomTable):

    def refresh_layout(self, table, df):
        assert table['type'] == 'table', 'invalid chart component'
        render_output = [
            html.H4(children=table['title'], style={
                'text-align': 'center'
            }),
        ]
        if len(df) > 0:
            render_output.append(html.Div(
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{'id': c, 'name': c} for c in df.columns],
                    style_cell={'textAlign': 'left'},
                    **table['args']
                )))
        return render_output


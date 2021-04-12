import plotly.graph_objects as go

from . import CustomChart


class HeatMapChart(CustomChart):

    def create_figure(self, df_raw, **kwargs):

        from pandas.core.dtypes.common import is_numeric_dtype

        x_column = kwargs.get("x_column")
        y_column = kwargs.get("y_column")
        z_column = kwargs.get("z_column")

        assert x_column, 'the x_column not found'
        assert y_column, 'the y_column not found'
        assert z_column, 'the z_column not found'

        if not is_numeric_dtype(df_raw[z_column]):
            assert "the z_column is not numeric"
        else:
            fig = go.Figure(
                go.Heatmap(x=df_raw[x_column], y=df_raw[y_column], z=df_raw[z_column], colorscale='Viridis')
            )
            return fig

import plotly.graph_objects as go

from . import CustomChart


class Indicator(CustomChart):  # noqa: H601
    """Radar Chart: task and milestone timeline."""

    DEFAULT_OBJ_COL = 'key'

    def create_traces(self, data_raw, **kwargs):
        """Return traces for plotly chart.

        Args:
            df_raw: pandas dataframe with columns: `(category, label, start, end, progress)`

        Returns:
            list: Dash chart traces

        """
        return [go.Indicator(
            mode="number+delta",
            value=400,
            number={'prefix': "$"},
            delta={'position': "top", 'reference': 320},
            domain={'x': [0, 1], 'y': [0, 1]})]

    #
    # def create_layout(self, df_raw, **kwargs):
    #     """Extend the standard layout.
    #
    #     Returns:
    #         dict: layout for Dash figure
    #
    #     """
    #     layout = super().create_layout(df_raw, **kwargs)
    #     # Suppress Y axis ticks/grid
    #     layout['yaxis']['showgrid'] = False
    #     layout['yaxis']['showticklabels'] = False
    #     layout['yaxis']['zeroline'] = False
    #
    #     layout['polar'] = go.layout.Polar(
    #         radialaxis=dict(
    #             visible=True,
    #             range=[0, 5]
    #         )),
    #     layout['showlegend'] = False
    #
    #     return layout

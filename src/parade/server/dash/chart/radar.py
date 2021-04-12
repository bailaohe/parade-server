import plotly.graph_objects as go
from . import CustomChart

class RadarChart(CustomChart):  # noqa: H601
    """Radar Chart: task and milestone timeline."""

    DEFAULT_OBJ_COL = 'key'
    # 默认数值型的填充值
    DEFAULT_NUMERIC_PLACEHOlDER = 0

    def create_figure(self, df_raw, **kwargs):
        from pandas.core.dtypes.common import is_numeric_dtype
        index_column = self.DEFAULT_OBJ_COL
        if index_column not in df_raw.columns:
            index_column = kwargs.get('key')

        assert index_column, 'the index column not found'

        placeholder = self.DEFAULT_NUMERIC_PLACEHOlDER
        if "placeholder" in kwargs:
            try:
                placeholder = float(kwargs.get("placeholder"))
            except ValueError as e:
                placeholder = 0

        categories = []
        for column in df_raw.columns:
            if column != index_column and is_numeric_dtype(df_raw[column]) and 'Unname' not in column:
                df_raw[column] = df_raw[column].fillna(placeholder)
                categories.append(column)

        assert categories, 'no category column provided'

        traces = []

        for _, item in df_raw.iterrows():
            key = item[index_column]
            r = [item[c] for c in categories]
            trace = go.Scatterpolar(
                r=r,
                theta=categories,
                fill='toself',
                name=key
            )
            traces.append(trace)

        fig = go.Figure()
        for trace in traces:
            fig.add_trace(trace)

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                )),
            showlegend=True if kwargs.get("showlegend") == "true" else False
        )

        return fig

    # def create_traces(self, data_raw, **kwargs):
    #     """Return traces for plotly chart.
    #
    #     Args:
    #         df_raw: pandas dataframe with columns: `(category, label, start, end, progress)`
    #
    #     Returns:
    #         list: Dash chart traces
    #
    #     """
    #     import pandas as pd
    #     from pandas.core.dtypes.common import is_numeric_dtype
    #     df_raw = pd.DataFrame.from_records(data_raw)
    #     index_column = self.DEFAULT_OBJ_COL
    #     if index_column not in df_raw.columns:
    #         index_column = kwargs.get('key')
    #
    #     assert index_column, 'the index column not found'
    #     categories = []
    #     for column in df_raw.columns:
    #         if column != index_column and is_numeric_dtype(df_raw[column]) and 'Unname' not in column:
    #             df_raw[column] = df_raw[column].fillna(0)
    #             categories.append(column)
    #
    #     assert categories, 'no category column provided'
    #
    #     traces = []
    #
    #     for _, item in df_raw.iterrows():
    #         key = item[index_column]
    #         r = [item[c] for c in categories]
    #         trace = go.Scatterpolar(
    #             r=r,
    #             theta=categories,
    #             fill='toself',
    #             name=key
    #         )
    #         traces.append(trace)
    #
    #     return traces
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

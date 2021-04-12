import plotly.graph_objects as go

from . import CustomChart


class multiaxisChart(CustomChart):  # noqa: H601

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

        scatter_column = [] if "scattercolumn" not in kwargs else kwargs['scattercolumn']
        for c in categories:
            if str(c) in scatter_column:
                trace = go.Scatter(
                    x=df_raw[index_column],
                    y=df_raw[c],
                    name=c,
                    xaxis='x',
                    yaxis='y2'
                )
            else:
                trace = go.Bar(
                    x=df_raw[index_column],
                    y=df_raw[c],
                    name=c,



                )
            traces.append(trace)

        layout = go.Layout(
            yaxis2=dict(anchor='x', overlaying='y', side='right'),
            barmode=kwargs.get("barmode")
        )
        fig = go.Figure(data = traces,layout=layout)
        return fig


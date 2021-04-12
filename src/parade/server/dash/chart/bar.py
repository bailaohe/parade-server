import plotly.graph_objects as go
from . import CustomChart


class BarChart(CustomChart):

    # 默认充当x轴的列名
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

        for c in categories:
            trace = go.Bar(
                x=df_raw[index_column],
                y=df_raw[c],
                name=c
            )
            traces.append(trace)

        fig = go.Figure()
        for trace in traces:
            fig.add_trace(trace)
        fig.update_layout(barmode=kwargs.get("barmode"))
        return fig


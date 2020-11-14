import plotly.graph_objects as go

from . import CustomChart
import pandas as pd


class Indicator(CustomChart):
    """Radar Chart: task and milestone timeline."""

    def create_traces(self, data, **kwargs):
        """Return traces for plotly chart.

        Args:
            data: pandas dataframe with columns: `(category, label, start, end, progress)`

        Returns:
            list: Dash chart traces

        """

        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')

        if len(data) == 0:
            return [go.Indicator(
                mode="number",
                value=0,
                number={'prefix': "$"},
                domain={'x': [0, 1], 'y': [0, 1]})]

        traces = []
        number = kwargs.get('number')
        if not number:
            if 'prefix' in kwargs or 'suffix' in kwargs:
                number = {}
                if 'prefix' in kwargs:
                    number['prefix'] = kwargs.get('prefix')
                if 'suffix' in kwargs:
                    number['suffix'] = kwargs.get('suffix')

        for item in data:
            mode = kwargs.get('mode', 'number+delta' if 'reference' in item else 'number')
            delta = {'reference': item['reference']} if 'reference' in item else None
            title = {'text': item['title']} if 'title' in item else None
            trace = go.Indicator(
                mode=mode,
                title=title,
                value=item['value'],
                number=number,
                delta=delta,
                domain={'x': [0, 1], 'y': [0, 1]}
            )
            traces.append(trace)

        return traces



from . import CustomChart
import plotly.graph_objects as go


class ChoroplethMap(CustomChart):  # noqa: H601
    """Gantt Chart: task and milestone timeline."""

    def create_figure(self, df_raw, **kwargs):
        """Return traces for plotly chart.

        Args:
            df_raw: pandas dataframe with columns: `(category, label, start, end, progress)`

        Returns:
            list: Dash chart traces

        """
        def get_geojson():
            import json
            from urllib.request import urlopen

            geojson_map = kwargs.get('geojson_map', {})

            if not geojson_map:
                geojson_path = kwargs.get('geojson', None)
                assert geojson_path, 'no geojson resource provided'

                try:
                    f = urlopen(geojson_path)
                except ValueError:  # invalid URL
                    import os
                    f = open(geojson_path if os.path.isabs(geojson_path) else os.path.join(self.context.workdir, geojson_path), 'r')

                try:
                    geojson_map = json.load(f)
                finally:
                    f.close()

            return geojson_map

        location_column = kwargs.get('location')
        z_column = kwargs.get('z')

        import pandas as pd
        df = pd.DataFrame.from_records(df_raw)

        fig = go.Figure(go.Choroplethmapbox(
            featureidkey="properties.NL_NAME_1",
            geojson=get_geojson(),
            locations=df[location_column],
            z=df[z_column],
            zauto=True,
            colorscale='viridis',
            reversescale=False,
            showscale=True,
        ))

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=3,
            mapbox_center={"lat": 37.110573, "lon": 106.493924},
            height=800
        )

        return fig


from . import CustomChart
import plotly.graph_objects as go


class ChoroplethMap(CustomChart):  # noqa: H601
    """Gantt Chart: task and milestone timeline."""

    def create_traces(self, df_raw, **kwargs):
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
                    f = open(geojson_path, 'r')

                try:
                    geojson_map = json.load(f)
                finally:
                    f.close()

            return geojson_map

        location_column = kwargs.get('location')
        z_column = kwargs.get('z')

        import pandas as pd
        df = pd.DataFrame.from_records(df_raw)

        return go.Figure(go.Choroplethmapbox(
            featureidkey="properties.NL_NAME_1",
            geojson=get_geojson(),
            locations=df[location_column],
            z=df[z_column],
            zauto=True,
            colorscale='viridis',
            reversescale=False,
            showscale=True,
            # marker_opacity=0.8,
            # marker_line_width=0.8,
            # customdata=np.vstack((df.地区, df.确诊, df.疑似, df.治愈, df.死亡)).T,
            # hovertemplate="<b>%{customdata[0]}</b><br><br>"
            #               + "确诊：%{customdata[1]}<br>"
            #               + "疑似：%{customdata[2]}<br>"
            #               + "治愈：%{customdata[3]}<br>"
            #               + "死亡：%{customdata[4]}<br>"
            #               + "<extra></extra>",
        ))

    def create_layout(self, df_raw, **kwargs):
        """Extend the standard layout.

        Returns:
            dict: layout for Dash figure

        """
        layout = super().create_layout(df_raw, **kwargs)
        # Suppress Y axis ticks/grid
        layout['yaxis']['showgrid'] = False
        layout['yaxis']['showticklabels'] = False
        layout['yaxis']['zeroline'] = False

        # TODO 参数化
        layout['mapbox_style'] = "open-street-map"
        layout['mapbox_zoom'] = 3
        layout['mapbox_center'] = {"lat": 37.110573, "lon": 106.493924}
        layout['height'] = 800
        return layout

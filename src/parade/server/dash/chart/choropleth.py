# from . import CustomChart
# import plotly.graph_objects as go
#
#
# class ChoroplethMap(CustomChart):  # noqa: H601
#     """Gantt Chart: task and milestone timeline."""
#
#     def create_traces(self, df_raw, **kwargs):
#         """Return traces for plotly chart.
#
#         Args:
#             df_raw: pandas dataframe with columns: `(category, label, start, end, progress)`
#
#         Returns:
#             list: Dash chart traces
#
#         """
#         return traces
#
#
#     def create_layout(self, df_raw, **kwargs):
#         """Extend the standard layout.
#
#         Returns:
#             dict: layout for Dash figure
#
#         """
#         layout = super().create_layout(df_raw, **kwargs)
#         # Suppress Y axis ticks/grid
#         layout['yaxis']['showgrid'] = False
#         layout['yaxis']['showticklabels'] = False
#         layout['yaxis']['zeroline'] = False
#         layout['height'] = (len(df_raw) + 5) * 20 + 260
#         return layout

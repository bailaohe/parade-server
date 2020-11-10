from ..utils import format_unix, get_unix
from . import CustomChart
import plotly.graph_objects as go
from palettable.tableau import tableau
import arrow


class GanttChart(CustomChart):  # noqa: H601
    """Gantt Chart: task and milestone timeline."""

    date_format = '%Y-%m-%d'
    """Date format for bar chart."""

    pallette = tableau.get_map('TableauMedium_10').hex_colors
    """Default color pallette for project colors."""

    hover_label_settings = {'bgcolor': 'white', 'font_size': 12, 'namelength': 0}
    """Plotly hover label settings."""

    rh = 1
    """Height of each rectangular task."""

    color_lookup = {}

    def create_traces(self, df_raw, **kwargs):
        """Return traces for plotly chart.

        Args:
            df_raw: pandas dataframe with columns: `(category, label, start, end, progress)`

        Returns:
            list: Dash chart traces

        """
        # If start is None, assign end to start so that the sort is correct
        start_index = df_raw.columns.get_loc('start')
        end_index = df_raw.columns.get_loc('end')
        for index in [idx for idx, is_na in enumerate(df_raw['start'].isna()) if is_na]:
            df_raw.iloc[index, start_index] = df_raw.iloc[index, end_index]
        df_raw['progress'] = df_raw['progress'].fillna(0)  # Fill possibly missing progress values for milestones
        df_raw['level'] = df_raw['issue_type'].apply(lambda t: 0 if t == 'Task' else 1)
        df_raw = (df_raw
                  .sort_values(by=['category', 'level', 'start', 'end'], ascending=False)
                  .reset_index(drop=True))

        # Create color lookup using categories in sorted order
        categories = set(df_raw['category'])
        self.color_lookup = {cat: self.pallette[idx] for idx, cat in enumerate(categories)}
        # Track which categories have been plotted
        plotted_categories = []
        # Create the Gantt traces
        traces = []
        # the current timestamp
        now = arrow.now()
        # the minimum task start timestamp
        min_task_start = None
        # the maximum task end timestamp
        max_task_end = None
        for task in df_raw.itertuples():
            if not min_task_start or arrow.get(task.start) < arrow.get(min_task_start):
                min_task_start = task.start
            if not max_task_end or arrow.get(task.end) > arrow.get(max_task_end):
                max_task_end = task.end

            y_pos = task.Index * self.rh
            is_first = task.category not in plotted_categories
            plotted_categories.append(task.category)
            traces.append(self._create_task_shape(task, y_pos, is_first))
            if task.progress > 0:
                traces.append(self._create_progress_shape(task, y_pos))
            traces.append(self._create_annotation(task, y_pos))

        if now.is_between(arrow.get(min_task_start), arrow.get(max_task_end)):
            today = now.format('YYYY-MM-DD')
            traces.append(self._create_date_boundary(today, len(df_raw) * self.rh))

        return traces

    def _create_date_boundary(self, mark_date, y_pos):
        """
        create the date mark on the gantt chart
        :param mark_date:
        :param y_pos:
        :return:
        """
        return go.Scatter(
            line={'width': 4, 'dash': 'dash', 'color': 'firebrick'},
            mode='lines',
            x=[mark_date, mark_date],
            y=[0, y_pos],
            showlegend=False,
        )

    def _create_hover_text(self, task):
        """Return hover text for given trace.

        Args:
            task: row tuple from df_raw with: `(category, label, start, end, progress)`

        Returns:
            string: HTML-formatted hover text

        """
        dates = [format_unix(get_unix(str_ts, self.date_format), '%a, %Y-%m-%d') for str_ts in [task.start, task.end]]
        if task.start != task.end:
            date_range = f'<br><b>Start</b>: {dates[0]}<br><b>End</b>: {dates[1]}'
        else:
            date_range = f'<br><b>Milestone</b>: {dates[1]}'
        return f'<b>{task.category}</b><br>{task.label} ({int(task.progress * 100)}%)<br>{date_range}'

    def _create_task_shape(self, task, y_pos, is_first):
        """Create colored task scatter rectangle.

        Args:
            task: row tuple from df_raw with: `(category, label, start, end, progress)`
            y_pos: top y-coordinate of task
            is_first: if True, this is the first time a task of this category will be plotted

        Returns:
            trace: single Dash chart Scatter trace

        """

        color = self.color_lookup[task.category]
        if task.sub_count > 0:
            scatter_kwargs = dict(
                hoverlabel=self.hover_label_settings,
                legendgroup=color,
                line={'width': 4, 'color': color},
                mode='lines',
                showlegend=is_first,
                text=self._create_hover_text(task),
                x=[task.start, task.start, task.end, task.end],
                y=[y_pos - self.rh/2, y_pos, y_pos, y_pos - self.rh/2],
            )
        else:
            scatter_kwargs = dict(
                fill='toself',
                fillcolor=color,
                hoverlabel=self.hover_label_settings,
                legendgroup=color,
                line={'width': 2, 'color': color},
                mode='lines',
                showlegend=is_first,
                text=self._create_hover_text(task),
                x=[task.start, task.end, task.end, task.start, task.start],
                y=[y_pos, y_pos, y_pos - self.rh, y_pos - self.rh, y_pos],
            )
        if is_first:
            scatter_kwargs['name'] = task.category
        return go.Scatter(**scatter_kwargs)

    def _create_progress_shape(self, task, y_pos):
        """Create semi-transparent white overlay `self.shapes` to indicate task progress.

        Args:
            task: row tuple from df_raw with: `(category, label, start, end, progress)`
            y_pos: top y-coordinate of task

        Returns:
            trace: single Dash chart Scatter trace

        """
        unix_start = get_unix(task.start, self.date_format)
        unix_progress = (get_unix(task.end, self.date_format) - unix_start) * task.progress + unix_start
        end = format_unix(unix_progress, self.date_format)
        return go.Scatter(
            fill='toself',
            fillcolor='white',
            hoverinfo='skip',
            legendgroup=self.color_lookup[task.category],
            line={'width': 1},
            marker={'color': 'white'},
            mode='lines',
            opacity=0.5,
            showlegend=False,
            x=[task.start, end, end, task.start, task.start],
            y=[y_pos, y_pos, y_pos - self.rh, y_pos - self.rh, y_pos],
        )

    def _create_annotation(self, task, y_pos):
        """Add task label to chart as text overlay.

        Args:
            task: row tuple from df_raw with: `(category, label, start, end, progress)`
            y_pos: top y-coordinate of task

        Returns:
            trace: single Dash chart Scatter trace

        """
        # For milestones with narrow fill, hover can be tricky, so intended to make the whole length of the text
        #   hoverable, but only the x/y point appears to be hoverable although it makes a larger hover zone at least
        return go.Scatter(
            hoverlabel=self.hover_label_settings,
            hovertemplate=self._create_hover_text(task) + '<extra></extra>',
            hovertext=self._create_hover_text(task),
            legendgroup=self.color_lookup[task.category],
            mode='text',
            showlegend=False,
            text=('' if not task.warn else '[' + task.warn + ']') + task.label,
            textposition='middle right',
            textfont=dict(color='SteelBlue' if not task.warn else 'firebrick'),
            x=[task.end],
            y=[y_pos - self.rh / 2],
        )

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
        layout['height'] = (len(df_raw) + 5) * 20 + 260
        return layout

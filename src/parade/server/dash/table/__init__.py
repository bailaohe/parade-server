from .. import DashboardComponent


class CustomTable(DashboardComponent):

    def init_layout(self, table_id, table, data):
        import dash_html_components as html
        if len(data) == 0:
            return html.Div(id=table_id)
        return html.Div(self.refresh_layout(table, data), id=table_id)


_driver_class_cache = {}


def load_table_component_class(context, driver):
    from parade.utils.modutils import iter_classes
    if driver not in _driver_class_cache:
        for table_class in iter_classes(CustomTable, 'parade.server.dash.table', context.name + '.dashboard.table',
                                        class_filter=lambda cls: cls != CustomTable):
            table_key = table_class.__module__.split('.')[-1]
            if table_key not in _driver_class_cache:
                _driver_class_cache[table_key] = table_class
    return _driver_class_cache[driver]

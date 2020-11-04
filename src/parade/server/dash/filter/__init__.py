from .. import DashboardComponent


class CustomFilter(DashboardComponent):
    pass


_driver_class_cache = {}


def load_filter_component_class(context, driver):
    from parade.utils.modutils import iter_classes
    if driver not in _driver_class_cache:
        for filter_class in iter_classes(CustomFilter, 'parade.server.dash.filter', context.name + '.dashboard.filter',
                                         class_filter=lambda cls: cls != CustomFilter):
            filter_key = filter_class.__module__.split('.')[-1]
            if filter_key not in _driver_class_cache:
                _driver_class_cache[filter_key] = filter_class
    return _driver_class_cache[driver]

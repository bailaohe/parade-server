def get_or_default(component,key,default):
    if key not in component:
        return default
    else:
        return component[key]
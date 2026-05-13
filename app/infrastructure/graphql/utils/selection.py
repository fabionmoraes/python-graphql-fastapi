from strawberry.types import Info


def parse_selected_fields(info: Info) -> dict:
    root = info.selected_fields[0]
    return _parse_selection(root.selections)


def _parse_selection(selections) -> dict:
    result = {}
    for field in selections:
        if field.selections:
            result[field.name] = _parse_selection(field.selections)
        else:
            result[field.name] = True
    return result

'''jsonpath parsing utilities for drench sdk lambdas'''
import jsonpath_ng

def find_subs(dic, event):
    ''' Substitute params from the event dict '''
    for key, val in dic.items():
        if isinstance(val, dict):
            dic[key] = find_subs(dic[key], event)
        else:
            try:
                expr = jsonpath_ng.parse(val)
                dic[key] = expr.find(event)[0].value
            except: #pylint:disable=bare-except
                pass
    return dic

def build_path(path, event):
    '''parse elements from api path'''
    parsed = []
    for element in path.split('/'):
        try:
            expr = jsonpath_ng.parse(element)
            parsed.append(str(expr.find(event)[0].value))
        except: #pylint:disable=bare-except
            parsed.append(str(element))
    return '/'.join(parsed)

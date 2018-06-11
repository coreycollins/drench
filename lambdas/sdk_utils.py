'''jsonpath parsing utilities for drench sdk lambdas'''
import jsonpath_ng

def find_subs(dic, base, env=None):
    ''' Substitute params from the event dict '''
    env = env or {}

    for key, val in dic.items():
        if isinstance(val, dict):
            dic[key] = find_subs(dic[key], base, env)
        else:
            new_val = val
            if isinstance(val, str):
                for e, v in env.items():
                    new_val = val.replace(e, v)

            try:
                expr = jsonpath_ng.parse(new_val)
                dic[key] = expr.find(base)[0].value
            except: #pylint:disable=bare-except
                dic[key] = new_val
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

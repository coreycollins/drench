'''jsonpath parsing utilities for drench sdk lambdas'''
import re
import jsonpath_ng

def find_subs(dic, base):
    ''' Substitute params from the event dict '''
    for key, val in dic.items():
        if isinstance(val, dict):
            dic[key] = find_subs(dic[key], base)
        else:
            try:
                if isinstance(val, str):
                    new_val = val
                    for match in re.finditer(r'\{\{(\$[a-zA-Z_.]*)\}\}', val):

                        if val == match[0]:
                            expr = jsonpath_ng.parse(match[1])
                            new_val = expr.find(base)[0].value
                        else:
                            expr = jsonpath_ng.parse(match[1])
                            repl = expr.find(base)[0].value
                            new_val = new_val.replace(match[0], str(repl))

                    dic[key] = str(new_val)
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

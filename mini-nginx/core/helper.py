import os

def parse_http_request(data):
    try:
        text = data.decode()
        lines = text.split('\r\n')
        request_line = lines[0]
        method, path, http_version = request_line.split()
        headers = {}
        i = 1
        while lines[i]:
            k, v = lines[i].split(":", 1)
            headers[k.strip()] = v.strip()
            i += 1
        body = "\r\n".join(lines[i+1:])
        return dict({'method':method, 'path':path, 'http_version':http_version, 'headers':headers, 'body':body if body else None})
    except Exception as e:
        return None

def get_routes(config):
    routes = {}

    for route in config.get('routes'):
        routes[route['path']]=route
    return routes
    
def match_route(path, config):
    # Sort keys by descending length
    sorted_routes = sorted(config['available_routes'].keys(), key=len, reverse=True)

    for route_path in sorted_routes:
        if path.startswith(route_path):
            return config['available_routes'][route_path], route_path 

    return None, None


def handle_route(route, path, config):
    try:
        if route['type'] == 'static':
            static_dir = os.getcwd()
            file_path = os.path.join(static_dir, "static", route['file'])

            if not os.path.exists(file_path):
                return {
                    'content': "Static file not found.",
                    'status': "404 Not Found"
                }

            with open(file_path, 'r') as f:
                content = f.read()
            return {
                'content': content,
                'status': "200 OK"
            }

        elif route['type'] == 'response':
            return {
                'content': route['message'],
                'status': "200 OK"
            }

        elif route['type'] == 'proxy':
            # Just a stub here
            return {
                'content': "Proxying not implemented yet.",
                'status': "501 Not Implemented"
            }

        elif route['type'] == 'upstream':
            return {
                'content': "Upstream load balancing not implemented yet.",
                'status': "501 Not Implemented"
            }

        else:
            return {
                'content': f"Unknown route type: {route['type']}",
                'status': "501 Not Implemented"
            }

    except Exception as e:
        return {
            'content': f"Internal Server Error: {str(e)}",
            'status': "500 Internal Server Error"
        }


def create_response(context):
    response = f"HTTP/1.1 {context['status']}\n"
    response += "Content-Length: {}\n".format(len(context['content']))
    response += "Content-Type: text\n"
    response += "\n"
    return response.encode() + context['content'].encode()

def get_default_page(status_code):
    static_dir = os.getcwd()
    
    with open(f"{static_dir}/static/errors/{status_code}.html") as f:
        content =f.read()
            
    return content

def handle_request(full_request,config):
    context = parse_http_request(full_request)
    # errro handle
    if context is None:
        response = {
            'content':"Malformed HTTP request or unable to parse request.",
            'status':"400 Bad Request"
        }
        final_response = create_response(response)
        return final_response
    
    route,path = match_route(context['path'],config)
    # error handle
    if route is None or path is None:
        response={
            'content':get_default_page(404),
            'status':"404 Not Found"
        }
        final_response = create_response(response)
        return final_response
    

    response = handle_route(route,path,config)

    
    final_response = create_response(response)

    return final_response
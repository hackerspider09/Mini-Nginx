import os
import socket
import selectors
from functools import partial
from core.logger import error_print,log_print


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
    available_routes = {}

    routes = config.get('routes',{})

    if routes is None:
        available_routes['/'] = {'path': '/', 'type': 'static', 'file': 'root.html'}
        config['welcome_page'] = True  # mini nginx is setup freshly so if no route is present show welcome page
        return available_routes

    for route in routes:
        available_routes[route['path']]=route
    return available_routes

    # 1st method
    # routes = {}

    # for route in config.get('routes'):
    #     routes[route['path']]=route
    # return routes
    
def match_route(path, config):
    # Sort keys by descending length
    sorted_routes = sorted(config['available_routes'].keys(), key=len, reverse=True)

    if config.get('welcome_page',False):
        return config['available_routes']['/'],'/'

    for route_path in sorted_routes:
        if path.startswith(route_path):
            return config['available_routes'][route_path], route_path 

    return None, None

def handle_proxy(host,port,request_data,requesting_client,sel):
    try:
        upstream_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        upstream_sock.setblocking(False)
        upstream_sock.connect_ex((host,int(port)))


        proxy_state = {
            'stage':'connecting',
            'upstream':upstream_sock,
            'requesting_client':requesting_client,
            'upstream_response':b'',
            # request data is full request string from client 
            'upstream_data':request_data
        }
        sel.register(upstream_sock,selectors.EVENT_WRITE,partial(proxy_send_request, state=proxy_state, sel=sel))
        return None
    
    except Exception as e:
        error_print(f"Proxy setup failed: {e}")
        return {
            'content': "Upstream error",
            'status': "502 Bad Gateway"
        }
    
def proxy_send_request(upstream_conn, mask, state, sel):
    try:
        if mask & selectors.EVENT_WRITE:
            sent = upstream_conn.send(state['upstream_data'])
            state['upstream_data'] = state['upstream_data'][sent:]
            if not state['upstream_data']:
                sel.modify(upstream_conn, selectors.EVENT_READ, partial(proxy_read_response, state=state, sel=sel))
    except Exception as e:
        error_print(f"Proxy send error: {e}")
        send_error_and_cleanup(state, sel)

def proxy_read_response(upstream_conn, mask, state, sel):
    try:
        data = upstream_conn.recv(4096)
        if data:
            state['upstream_response'] += data
        else:
            sel.modify(state['requesting_client'], selectors.EVENT_WRITE, partial(proxy_send_to_client, state=state, sel=sel))
            sel.unregister(upstream_conn)
            upstream_conn.close()
    except Exception as e:
        error_print(f"Proxy read error: {e}")
        send_error_and_cleanup(state, sel)

def proxy_send_to_client(client_conn, mask, state, sel):
    try:
        if mask & selectors.EVENT_WRITE:
            sent = client_conn.send(state['upstream_response'])
            state['upstream_response'] = state['upstream_response'][sent:]
            if not state['upstream_response']:
                sel.unregister(client_conn)
                client_conn.close()
    except Exception as e:
        error_print(f"Send to client error: {e}")
        cleanup_proxy(state, sel)

def send_error_and_cleanup(state, sel):
    err = create_response({'status': '502 Bad Gateway', 'content': 'Upstream error'})
    try:
        state['requesting_client'].sendall(err)
    except: pass
    cleanup_proxy(state, sel)

def cleanup_proxy(state, sel):
    """Clean up proxy resources"""
    try:
        sel.unregister(state['upstream'])
        state['upstream'].close()
    except:
        pass
    try:
        sel.unregister(state['requesting_client'])
        state['requesting_client'].close()
    except:
        pass
    
def handle_route(route, path,full_request,requesting_client_conn,sel, config):
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
                'status': "200 OK",
            }

        elif route['type'] == 'response':
            return {
                'content': route['message'],
                'status': "200 OK"
            }

        elif route['type'] == 'proxy':
            # Just a stub here
            host,port = route['target'].split(':')
            return {
                'proxy':True,
                'host':host,
                'port':port
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
    response = f"HTTP/1.1 {context['status']}\r\n"
    response += f"Content-Length: {len(context['content'])}\r\n"
    # text/plain return plain text 
    response += "Content-Type: text\r\n\r\n"
    return response.encode() + context['content'].encode()

def get_default_page(status_code):
    static_dir = os.getcwd()
    
    with open(f"{static_dir}/static/errors/{status_code}.html") as f:
        content =f.read()
            
    return content

def handle_request(full_request,requesting_client_conn,sel,config):
    context = parse_http_request(full_request)
    # print log
    log_print(f"{context['method']} {context['path']} {context['http_version']}" )

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

    response = handle_route(route,path,full_request,requesting_client_conn,sel,config)
    if response.get('proxy'):
        # to handle proxy
        return response
    
    final_response = create_response(response)

    return final_response
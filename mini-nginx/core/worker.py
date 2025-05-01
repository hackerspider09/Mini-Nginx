import struct
from core.config import load_config
from core.logger import debug_log,log_print,error_print
import selectors
import os
import socket
from functools import partial
from core.helper import create_response, handle_request,handle_proxy,cleanup_proxy

sel = selectors.DefaultSelector()

def accept_connection(socket_obj, mask,w_data,config):
    if mask & selectors.EVENT_READ:
        try:
            conn, addr = socket_obj.accept()
            log_print(f"Worker{w_data['w_id']} accepted {addr}")

            conn.setblocking(False)
            sel.register(conn, selectors.EVENT_READ, partial(read_connection, w_data=w_data,config=config))
        except Exception as e:
            error_print(f"Error accepting connection: {e}")
            try:
                sel.unregister(conn)
            except Exception:
                pass
            conn.close()


def send_connection(conn,mask,w_data,response):
    if not (mask & selectors.EVENT_WRITE):
        error_print(f"Socket not writable: {conn.getpeername()}")
        try:
            sel.unregister(conn)
        except Exception:
            pass
        conn.close()
        return
    
    try:
        conn.sendall(response)
        log_print(f"Worker{w_data['w_id']} served {conn.getpeername()}")
    except ConnectionError as e:
        error_print(f"Error sending to {conn.getpeername()}: {e}")
    finally:
        try:
            sel.unregister(conn)
        except Exception:
            pass
        conn.close()

# Dictionary to store connection states
connection_states = {}

def read_connection(conn, mask, w_data, config):
    
    # Get connection state or initialize
    fileno = conn.fileno()
    if fileno not in connection_states:
        connection_states[fileno] = {
            'buffer': b'',
            'headers_complete': False,
            'content_length': 0,
            'headers_part': b'',
            'conn': conn  # Keep reference to connection
        }
    
    state = connection_states[fileno]
    
    try:
        # Read available data
        data = conn.recv(1024*4)
        '''uncomment print statement you will notice some unusual behavior
        this happens due to event loop (as client send data in packats not all data present in same packat so we have to get all data in diff event loop
        and to get its state we use global var to store its status)
        case 1 : in request there is only header oart initialy we will get that and in next event loop we  get body part 
        thats logic is there like if header part is complete make it true so in next loop we will avoid preosesing header and we know that we processed header so it must be body'''
        debug_log(f"0=> {data}")
        debug_log(f"1=> {state['buffer']}")
        if not data:
            error_print("Connection closed by client")
            cleanup_context(fileno)
            sel.unregister(conn)
            conn.close()
            return
            
        state['buffer'] += data
        debug_log(f"2=> {state['buffer']}")
        # Check for complete headers
        if not state['headers_complete']:
            if b'\r\n\r\n' in state['buffer']:
                state['headers_part'], _, body_part = state['buffer'].partition(b'\r\n\r\n')
                headers = state['headers_part'].decode('utf-8', errors='ignore').split('\r\n')
                # Find Content-Length
                for header in headers[1:]:
                    if header.lower().startswith('content-length:'):
                        state['content_length'] = int(header.split(':')[1].strip())
                        break
                
                state['headers_complete'] = True
                state['buffer'] = body_part
                debug_log(f"3=> {state['buffer']}")
            else:
                # Need more headers data
                cleanup_context(fileno)
                sel.unregister(conn)
                conn.close()
                return

        # Check for complete body
        # 2nd condiiton works for both with and without body as
        # if there is no body content_length is 0 and buffer is also 0 and similar for with body  
        if state['headers_complete'] and len(state['buffer']) >= state['content_length']:
            # Full request received
            body = state['buffer'][:state['content_length']] if state['content_length'] > 0 else b''
            full_request = state['headers_part'] + b'\r\n\r\n' + body

            response = handle_request(full_request,conn,sel,config)
            if isinstance(response,dict) and response.get('proxy'):
                proxy_result = handle_proxy(response['host'],response['port'],full_request,conn,sel)
                if proxy_result is None:
                    cleanup_context(fileno)
                    return
                else:
                    try:
                        # to handle erro of already register or modify selector
                        sel.unregister(conn)
                    except:
                        pass
                    formated_response = create_response(proxy_result)
                    sel.register(conn, selectors.EVENT_WRITE,partial(send_connection, w_data=w_data, response=formated_response))
            else:
                try:
                    # to handle erro of already register
                    sel.unregister(conn)
                except:
                    pass
                cleanup_context(fileno)
                sel.register(conn, selectors.EVENT_WRITE, partial(send_connection, w_data=w_data,response=response))

    except Exception as e:
        error_print(f"Error in read_connection: {e}")
        cleanup_context(fileno)
        try:sel.unregister(conn)
        except:pass
        conn.close()
        


def cleanup_context(fileno):
    """Clean up connection resources"""
    try:
        if fileno in connection_states:
            del connection_states[fileno]
    except Exception as e:
        error_print(f"Cleanup error: {e}")



def run_worker(w_data,config):
    config = config
    host = config.get("host", "127.0.0.1")
    port = config.get("port", 8080)
    

    socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # To solve problem of already bind 
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_obj.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    socket_obj.bind((host,port))
    socket_obj.listen()
    socket_obj.setblocking(False)

    sel.register(socket_obj, selectors.EVENT_READ, partial(accept_connection, w_data=w_data, config=config))


    log_print(f"Mini-Nginx running on Worker{w_data['w_id']} PID: {w_data['w_pid']} -> {host}:{port}")
    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                callback = key.data
                try:
                    callback(key.fileobj, mask)
                except Exception as e:
                    # error_print(f"Error handling event: {e}")

                    try:sel.unregister(key.fileobj)
                    except:pass
                    key.fileobj.close()


    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


        
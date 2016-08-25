# -*- coding: utf-8 -*-
# tcp mapping created by hutaow(hutaow.com) at 2014-08-31

import socket
import threading

# 端口映射配置信息
CFG_DEST_IP = '127.0.0.1'
CFG_DEST_PORT = 3389
CFG_SRC_IP = '0.0.0.0'
CFG_SRC_PORT = 2196

# 接收数据缓存大小
PKT_BUFF_SIZE = 2048

# 调试日志封装
def send_log(content):
  print content
  return

# 单向流数据传递
def tcp_mapping_worker(conn_receiver, conn_sender):
  while True:
    try:
      data = conn_receiver.recv(PKT_BUFF_SIZE)
    except Exception:
      send_log('Event: Connection closed.')
      break

    if not data:
      send_log('Info: No more data is received.')
      break

    try:
      conn_sender.sendall(data)
    except Exception:
      send_log('Error: Failed sending data.')
      break

    # send_log('Info: Mapping data > %s ' % repr(data))
    send_log('Info: Mapping > %s -> %s > %d bytes.' % (conn_receiver.getpeername(), conn_sender.getpeername(), len(data)))

  conn_receiver.close()
  conn_sender.close()

  return

# 端口映射请求处理
def tcp_mapping_request(src_conn, dest_ip, dest_port):
  dest_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  try:
    dest_conn.connect((dest_ip, dest_port))
  except Exception:
    src_conn.close()
    send_log('Error: Unable to connect to the remote server.')
    return

  threading.Thread(target=tcp_mapping_worker, args=(src_conn, dest_conn)).start()
  threading.Thread(target=tcp_mapping_worker, args=(dest_conn, src_conn)).start()

  return

# 端口映射函数
def tcp_mapping(dest_ip, dest_port, src_ip, src_port):
  src_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  src_server.bind((src_ip, src_port))
  src_server.listen(5)

  send_log('Event: Starting mapping service on ' + src_ip + ':' + str(src_port) + ' ...')

  while True:
    try:
      (src_conn, src_addr) = src_server.accept()
    except KeyboardInterrupt, Exception:
      src_server.close()
      send_log('Event: Stop mapping service.')
      break

    threading.Thread(target=tcp_mapping_request, args=(src_conn, dest_ip, dest_port)).start()

    send_log('Event: Receive mapping request from %s:%d.' % src_addr)

  return

# 主函数
if __name__ == '__main__':
  tcp_mapping(CFG_DEST_IP, CFG_DEST_PORT, CFG_SRC_IP, CFG_SRC_PORT)


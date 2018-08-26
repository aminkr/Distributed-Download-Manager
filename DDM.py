#!/usr/bin/python
"""
Distributed Download Manager (DDM).
"""

__author__ = 'amin.kavosi'
__email__ = 'amin.kavosi@yahoo.com'
__date__ = '2018-Aug-1'
__version__ = '1.0.0'

import argparse
import os
import requests
import paramiko
import threading
from logger import logger
import time


class RemoteDownloadManager(object):

    def __init__(self, servers, url):

        self.url = url
        self.servers = servers
        self.remote_script_file_name = 'download.py'
        self.threads_list = []

    def workon(self, server, file_name, start, end, url):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            cwd = os.getcwd()

            logger.info('connecting to server {}'.format(server))

            client.connect(server['ip'], username=server['username'], password=server['password'])

            sftp = client.open_sftp()
            server_script = cwd + '/ServerScript.py'
            sftp.put(server_script, '/tmp/{}'.format(self.remote_script_file_name))
            sftp.close()

            stdin, stdout, stderr = client.exec_command('python /tmp/{} {} {} {}'.format(self.remote_script_file_name, start, end, url))

            exit_status = stdout.channel.recv_exit_status()

            server_file_name = str(start) + '-' + str(end)

            if exit_status == 0:
                logger.info ("Parts {} Downloaded".format(server_file_name))
            else:
                logger.error("Error status code {} in get Parts {}".format(exit_status, server_file_name))

            logger.debug('after exec command')

            sftp = client.open_sftp()
            sftp.get('/tmp/{}'.format(server_file_name), '/tmp/{}'.format(server_file_name))
            sftp.remove('/tmp/{}'.format(server_file_name))
            sftp.remove('/tmp/{}'.format(self.remote_script_file_name))
            sftp.close()

            client.close()

            with open(file_name, "r+b") as fp:
                fp.seek(start)
                var = fp.tell()
                with open('/tmp/' + server_file_name, "r+b") as sfp:
                    fp.write(sfp.read())

            os.remove("/tmp/{}".format(server_file_name))

        except Exception as e:
            logger.error('an exception raised in workon function : {} '.format(e))

    def start_downloading(self):

        r = requests.head(self.url)

        file_name = self.url.split('/')[-1]
        file_name = file_name.split('?')[0]

        try:
            file_size = int(r.headers['content-length'])

            logger.info('file_size is {}'.format(file_size))

        except:
            logger.error("Invalid URL {}".format(self.url))
            return

        part = int(file_size) / len(self.servers)

        fp = open(file_name, "wb")

        fp.write('\0' * file_size)

        fp.close()

        try:
            for i in range(len(self.servers)):
                start = part * i
                end = start + part

                t = threading.Thread(target=self.workon,
                                     kwargs={'server': self.servers[i], 'file_name': file_name,
                                             'start': start, 'end': end, 'url': self.url })
                t.setDaemon(True)
                t.start()
                self.threads_list.append(t)

            for t in self.threads_list:
                t.join()
                logger.info('join for thread {}'.format(t.ident))
            logger.info('file {} has been downloaded successfully'.format(file_name))

        except Exception as e:
            logger.error('an exception raised in start downloading: {} '.format(e.message))


if __name__ == '__main__':

    servers = []
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-u', '--url', help='url of file', type=str, required=True)
    parser.add_argument('-s', '--servers', help='in format user@ip:pass'
                        , type=str, required=False, default='./servers.txt')
    args = parser.parse_args()

    try:
        with open(args.servers, "r") as sf:
            server_file_content = sf.read().splitlines()

        for server in server_file_content:
            username = server.split('@')[0]
            ip = (server.split('@')[1]).split(':')[0]
            password = (server.split('@')[1]).split(':')[1]
            servers.append({'ip': ip, 'username': username, 'password': password})

        for server in servers:
            logger.info('server {}'.format(server))

    except Exception as e:
        logger.error('invalid server file {}'.format(e))
        exit(1)

    start_time = time.time()
    rdm = RemoteDownloadManager(servers, args.url)
    rdm.start_downloading()
    end_time = time.time()
    logger.info('elapsed time {} minute'.format(int(end_time - start_time)/60))





import paramiko


class SSHClient:
    def __init__(self, hostname, username, password, port=22, timeout=20):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp_client = None
        self.shell = None
        self.client_state = 0

    def connect(self):
        try:
            self.client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password,
                                timeout=self.timeout)
            self.client_state = 1
        except Exception:
            try:
                self.client.close()
            except Exception:
                pass

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass

    def run_cmd(self, cmd):
        _, stdout, stderr = self.client.exec_command(cmd)
        err = stderr.read().decode()
        if err:
            return err
        return stdout.read().decode()

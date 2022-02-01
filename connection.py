import paramiko
import os

sftpURL   =  None
sftpUser  =  None
sftpPass  =  None
sftpKey = None
local_path = None

def get_ssh_test():
    try:
        ssh = paramiko.SSHClient()
        # automatically add keys without requiring human intervention
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        ssh.connect(sftpURL, username=sftpUser, password=sftpPass )
        return ssh, True
    except Exception as e:
        return str(e), False

def get_ssh(sftpURL, sftpUser, sftpPass, key_filename=None):
    try:
        ssh = paramiko.SSHClient()
        # automatically add keys without requiring human intervention
        ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
        if key_filename:
            ssh.connect(sftpURL, username=sftpUser, password=sftpPass, key_filename=key_filename)
        else:
            ssh.connect(sftpURL, username=sftpUser, password=sftpPass)
        return ssh, True
    except Exception as e:
        return str(e), False

def run_command(ssh, cmd:str):
    (stdin, stdout, stderr) = ssh.exec_command(cmd)
    outputs = []
    for line in stdout.readlines():
        outputs.append(line)
    return outputs


def get_sftp(ssh):
    ftp = ssh.open_sftp()
    return ftp

def change_folder(ftp, path):
    ftp.chdir(path)

def change_local_folder(path):
    global local_path
    if path.startswith("/"):
        local_path = os.path.abspath(path)
    else:
        p = os.path.join(local_path, path)
        local_path = os.path.abspath(p)


def get_cwd(ftp):
    return ftp.getcwd()

def get_local_cwd():
    return local_path


def get_folder_contents(ftp):
    contents = ftp.listdir()
    folders = []
    files = []
    for i in contents:
        lstatout=str(ftp.lstat(i)).split()[0]
        if 'd' in lstatout: 
            # print(i,'is a directory')
            folders.append(i)
        else:
            # print(i,'is a file')
            files.append(i)
    return folders, files

def get_local_contents():
    path = local_path
    fs = os.listdir(path)
    dirs = []
    files = []
    for f in fs:
        if os.path.isdir(os.path.join(path,f)):
            # print(f, "is folder")
            dirs.append(f)
        elif os.path.isfile(os.path.join(path,f)):
            # print(f, "is file")
            files.append(f)
    return dirs, files

def init_env_local():
    global local_path
    local_path = os.path.abspath(os.getcwd())

def init_env():
    global local_path
    ssh,_ = get_ssh_test()
    ftp = get_sftp(ssh)
    local_path = os.path.abspath(os.getcwd())
    change_folder(ftp,".")
    remote_path = get_cwd(ftp)
    print("local=", local_path)
    print("remote=", remote_path)

    return ssh, ftp, local_path, remote_path

def join_path(path, filename):
    if path[0] == '/':
        # linux
        if path[-1] == '/':
            return path[:-1] + "/" + filename
        return path + "/" + filename
    else:
        # windows
        if path[-1] == '\\':
            return path[:-1] + "/" + filename
        return path + "/" + filename

def upload_to_folder(ftp, local_file, remote_folder):
    fname = os.path.basename(local_file)
    remote_dest = join_path(remote_folder, fname)
    ftp.put(local_file, remote_dest)

def download(ftp, src, dest):
    ftp.get(src, dest)


class EnhancedFTP:
    @staticmethod
    def put_dir(ftp, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are 
            created under target.
        '''
        if target[0] == "/":
            is_linux = True
        for item in os.listdir(source):
            if is_linux:
                dest_ = '%s/%s' % (target, item)
            else:
                dest_ = '%s\\%s' % (target, item)
            if os.path.isfile(os.path.join(source, item)):
                ftp.put(os.path.join(source, item), dest_)
            else:
                EnhancedFTP.mkdir(ftp, dest_, ignore_existing=True)
                EnhancedFTP.put_dir(ftp, os.path.join(source, item), dest_)

    @staticmethod
    def mkdir(ftp, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            ftp.mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise
    
    @staticmethod
    def upload_folder_to_folder(ftp, source, dest):
        folder_name = os.path.basename(source)
        dest_path = join_path(dest, folder_name)
        EnhancedFTP.mkdir(ftp, dest_path, ignore_existing=True)
        EnhancedFTP.put_dir(ftp, source, dest_path)


if __name__ == "__main__":
    ssh, ftp, local_path, remote_path = init_env()
    print("local_path=",local_path)
    change_folder(ftp, "Documents")
    print("remote cwd=", ftp.getcwd())
    # dirs, files = get_folder_contents(ftp)
    print("-" * 30)
    change_local_folder("ss")
    get_local_contents()

    source = "C:\\Users\\ray_hou\\OneDrive - Dell Technologies\\Documents\\FileTransfer"
    dest = "/home/cyc/Downloads"
    EnhancedFTP.upload_folder_to_folder(ftp, source, dest)

    ssh.close()
    

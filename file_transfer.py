import npyscreen
import os
import connection
import curses
import json
from pathlib import Path

COLUMNS = 0
LINES = 0
ssh = None
ftp = None
ssh_creds=None
ssh_cred_obj={}

def init():
    global COLUMNS
    global LINES
    global ssh_creds
    global ssh_cred_obj

    size = os.get_terminal_size()
    COLUMNS = size.columns
    LINES = size.lines
    print("size=", size)
    home = str(Path.home())
    config_dir = os.path.join(home, "file_transfer")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    ssh_creds = os.path.join(config_dir, ".ssh_creds")
    if not os.path.exists(ssh_creds):
        json.dump({}, open(ssh_creds, 'w'))
    ssh_cred_obj = json.load(open(ssh_creds))
    print("You can edit", ssh_creds, "to save accounts.")
    

def adapt_center(form):
    line_at = (LINES - form.lines) // 2
    column_at = (COLUMNS - form.columns) // 2
    form.show_atx = column_at
    form.show_aty = line_at
    form.draw_line_at = line_at + form.lines - 6

def calc_size(width_ratio, height_ratio):
    return int(COLUMNS * width_ratio), int(LINES * height_ratio)

    
class FileSelectorLocalUpload(npyscreen.MultiLineAction):
    # show local files in 
    def actionHighlighted(self, act_on_this, key_press):
        # npyscreen.notify_confirm(f"{key_press} {act_on_this}", "AA", editw=1)
        selected = act_on_this
        if selected[-1] == "/":
            connection.change_local_folder(selected)
            dirs, files = connection.get_local_contents()
            dirs_slash = ['../'] + [f"{s}/" for s in dirs]
            content_list = dirs_slash + files
            self.parent.select.values=content_list
            self.parent.local_path_input.value = connection.get_local_cwd()

            self.parent.refresh()
            self.parent.select.update()
            self.parent.local_path_input.update()
            
        else:
            remote_path = self.parent.server_path_button.value
            source = connection.get_local_cwd()
            fpath = os.path.join(source, selected)
            is_upload = npyscreen.notify_yes_no(f"Do you want to upload file {fpath}<local> to {remote_path}<server>?", "Upload folder", editw=1)
            if is_upload:
                connection.upload_to_folder(ftp, fpath, remote_path)
                npyscreen.notify_confirm("Upload finished.", "Notification")

class AccountSelection(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, key_press):
        # npyscreen.notify_confirm(f"{key_press} {act_on_this}", "AA", editw=1)
        selected = act_on_this
        info = ssh_cred_obj.get(selected, None)
        ip,name,pwd = info["serverIP"], info["username"], info["password"]
        # self.parent.acc_input
        self.parent.ip_input.value = ip
        self.parent.username_input.value = name
        self.parent.password_input.value  = pwd
        self.parent.account_.value = selected
        self.parent.account_.update()
        self.parent.ip_input.update()
        self.parent.username_input.update()
        self.parent.password_input.update()
        

class FileSelectorRemoteUpload(npyscreen.MultiLineAction):
    # show local files in 
    def actionHighlighted(self, act_on_this, key_press):
        # npyscreen.notify_confirm(f"{key_press} {act_on_this}", "AA", editw=1)
        selected = act_on_this
        if selected[-1] == "/":
            connection.change_folder(ftp, selected)
            dirs, files = connection.get_folder_contents(ftp)
            dirs_slash = ['../'] + [f"{s}/" for s in dirs]
            content_list = dirs_slash + files
            self.parent.select.values=content_list
            self.parent.remote_path_input.value = connection.get_cwd(ftp)

            self.parent.refresh()
            self.parent.select.update()
            self.parent.remote_path_input.update()
            
        else:
            # self.parent.remote_path_input.edit()
            pass


class ServerDestinationUploadWindow(npyscreen.ActionForm):
    def create(self):
        adapt_center(self)
        # ssh, ftp, local_path, remote_path = connection.init_env()
        global ssh
        global ftp
        # dirs, files = connection.get_folder_contents(ftp)
        # dirs_slash = ['../'] + [f"{s}/" for s in dirs]
        # content_list = dirs_slash + files
        self.remote_path_input = self.add(npyscreen.TitleText, name="Server Path", value="~")
        self.select = self.add(FileSelectorRemoteUpload, values=["1", "2"], scroll_exit=True)
        # self.remote_path_input.value = connection.get_cwd(ftp)
    
    def update_data(self):
        global ssh
        global ftp
        dirs, files = connection.get_folder_contents(ftp)
        dirs_slash = ['../'] + [f"{s}/" for s in dirs]
        content_list = dirs_slash + files
        self.select.values=content_list
        remote_path = connection.get_cwd(ftp)
        self.remote_path_input.value = remote_path
        self.parentApp.form_upload.server_path_button.value = remote_path

        self.remote_path_input.update()
        self.parentApp.form_upload.server_path_button.update() 

        

    def on_cancel(self):
        self.parentApp.setNextForm("upload_win")

    def on_ok(self):
        self.parentApp.upload_data['dest'] = self.remote_path_input.value
        self.parentApp.form_upload.server_path_button.value = self.remote_path_input.value
        self.parentApp.setNextForm("upload_win")




class TransferWindow(npyscreen.ActionForm, npyscreen.FormWithMenus):
    def create(self):
        adapt_center(self)
        # self.aa = self.ip_input = self.add(npyscreen.TitleText, name="AA")
        # self.username_input = self.add(npyscreen.TitleText, name="BB")
        self.mode_selector = self.add(npyscreen.TitleFixedText, name="Mode", value = "<Upload>")
        self.server_path_button = self.add(npyscreen.TitleText, name="Server Path", value = "~")
        # self.operation_selector = self.add(OperationSelector, values=["(*) Upload", "( ) Download"])
        self.local_path_input = self.add(npyscreen.TitleText, name="Local Path", value="sssee")

        # dirs, files = connection.get_folder_contents(ftp)
        connection.init_env_local()
        dirs, files = connection.get_local_contents()
        dirs_slash = ['../'] + [f"{s}/" for s in dirs]
        content_list = dirs_slash + files
        self.select = self.add(FileSelectorLocalUpload, values=content_list, scroll_exit=True)
        self.local_path_input.value = connection.get_local_cwd()

        new_handlers = {
            curses.ascii.CR: self.on_change_mode
        }
        # self.mode_selector.add_handlers(new_handlers)

        self.server_path_button.add_handlers({
            curses.ascii.CR: self.on_change_remote_dest,
            curses.ascii.NL: self.on_change_remote_dest
        })

        # self.files = self.add(npyscreen.Autocomplete, name="files", values=["1","2","3","4"])
    
    def on_change_remote_dest(self, key):
        self.parentApp.form_server_dest.update_data()
        self.parentApp.switchForm("remote_dest_upload")
        

    def on_change_mode(self, key):
        if self.mode_selector.value == "<Upload>":
            self.mode_selector.value = "<Download>"
        elif self.mode_selector.value == "<Download>":
            self.mode_selector.value = "<Upload>"
        
        # self.mode_selector.add_handlers({
        #     curses.ascii.CR: self.on_change_mode
        # })
        
        # self.select.values
        self.refresh()
        self.mode_selector.update()

    def afterEditing(self):
        # self.parentApp.setNextForm(None)
        pass
        # npyscreen.notify_confirm("bye", "DDD", editw=1)


    def on_ok(self):
        folder_name = self.local_path_input.value
        remote_path = self.server_path_button.value
        source = connection.get_local_cwd()
        is_upload = npyscreen.notify_yes_no(f"Do you want to upload folder {source}<local> to {remote_path}<server>?", "Upload folder", editw=1)
        if is_upload:
            # connection.upload_to_folder(ftp, source, remote_path)
            connection.EnhancedFTP.upload_folder_to_folder(ftp, source, remote_path)
            npyscreen.notify_confirm("Upload finished.", "Notification")


    def on_cancel(self):
        self.parentApp.setNextForm(None)
        

class FormObject(npyscreen.ActionForm, npyscreen.SplitForm, npyscreen.FormWithMenus):
    def create(self):
        adapt_center(self)
        account_list = list(ssh_cred_obj.keys())
        self.account_ = self.add(npyscreen.TitleFixedText, name="Account")
        self.acc_input = self.add(AccountSelection, name="Account", values=account_list, max_height=3, scroll_exit=True)
        self.ip_input = self.add(npyscreen.TitleText, name="ServerIP") # value="10.249.108.181"
        self.username_input = self.add(npyscreen.TitleText, name="Username") # value="cyc"
        self.password_input = self.add(npyscreen.TitleText, name="Password") # value="cycpass"
        self.key_input = self.add(npyscreen.TitleText, name="KeyFile", value="") 

    def on_ok(self):
        global ssh
        global ftp
        ip = str(self.ip_input.value).strip()
        user = str(self.username_input.value).strip()
        password = str(self.password_input.value).strip()
        keyfile = str(self.key_input.value).strip()

        if self.key_input.value.strip() == "":
            obj, success = connection.get_ssh(ip, user, password)
        else:
            obj, success = connection.get_ssh(ip, user, password, keyfile)
        if success:
            ssh = obj
            ftp = connection.get_sftp(ssh)
            npyscreen.notify_confirm(f"Connection has been established to {ip}!", "Connected!", editw=1)
            #upload_win
            self.parentApp.switchForm("upload_win")
        else:
            msg = obj
            npyscreen.notify_confirm(f"Connection to {ip} failed! Reason: {msg}", "Unconnected!", editw=1)
            

    def on_cancel(self):
        self.parentApp.setNextForm(None)
    
    def afterEditing(self):
        pass
        # self.parentApp.setNextForm(None)

class App(npyscreen.NPSAppManaged):
    upload_data = {
        'src': None,
        'dest':None
    }
    download_data = {
        'src':None,
        'dest':None
    }
    def onStart(self):
        columns,lines = calc_size(0.6,0.6)
        self.form_login = self.addForm("MAIN", FormObject, name="Superb Remote File manager")

        columns,lines = calc_size(0.9,0.9)
        # upload_win
        self.form_upload = self.addForm("upload_win", TransferWindow, name="Superb Remote File manager")
        columns,lines = calc_size(0.9,0.9)
        # remote_dest_upload
        self.form_server_dest = self.addForm("remote_dest_upload", ServerDestinationUploadWindow, name="Choose Destination")


if __name__ == "__main__":
    init()
    app = App().run()

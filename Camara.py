# 		no leading slash after folder name
save_folder_path = '/home/pi/usb/Juan/Media/sec.cam'
db_file_name = '/frames.db'
#save_folder_path = '/run/user/1000/gvfs/sftp:host=192.168.0.112,user=pi/home/pi/usb/Juan/Media/sec.cam'

def InStore():
    camaras = {
    #'myPhone': '192.168.0.144:8080',
    'lg':'192.168.0.147:8080',
    }

    return camaras

def save_folder(save_folder=save_folder_path):
    return save_folder



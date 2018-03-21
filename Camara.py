# 		no leading slash after folder name
save_folder_path = '/home/pi/usb/Juan/Media/sec.cam'
db_file_name = '/frames.db'




def InStore():
    camaras = {
    #'Tree':"192.168.0.144:8080",
    #'House':"192.168.0.107:8080",
    'Living': '192.168.0.147:8080',
    #'myPhone': '192.168.1.135:8080',
    #'lg':'192.168.1.122:8080'
    # 'Samsung': '192.168.0.129:8080'
    }

    return camaras

def save_folder(save_folder=save_folder_path):
    return save_folder



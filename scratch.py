# import configparser

# config = configparser.ConfigParser(allow_no_value=True)
# config.read("./sentences.ini")
# new_query = ""
# for section in config.sections():
#     new_query += "\n[{}]".format(section)
#     for key in config[section]: 
#         new_query += "\n{}".format(key)
        
# print(new_query)

from sys import platform

def get_master_volume_linux():
    proc = subprocess.Popen('/usr/bin/amixer', shell=True, stdout=subprocess.PIPE, encoding='utf8')
    amixer_stdout = proc.communicate()[0].split('\n')[4]
    proc.wait()
    find_start = amixer_stdout.find('[') + 1
    find_end = amixer_stdout.find('%]', find_start)
    return float(amixer_stdout[find_start:find_end])


def set_master_volume_linux(volume):
    proc = subprocess.Popen('/usr/bin/amixer', shell=True, stdout=subprocess.PIPE, encoding='utf8')
    amixer_stdout = proc.communicate()[0].split('\n')[0]
    proc.wait()
    find_start = amixer_stdout.find('[') + 1
    find_end = amixer_stdout.find('%]', find_start)
    device_name = amixer_stdout[find_start:find_end]
    val = float(int(volume))
    proc = subprocess.Popen('/usr/bin/amixer sset ' + device_name + ' ' + str(val) + '%', shell=True, stdout=subprocess.PIPE)
    proc.wait()

if platform == "linux" or platform == "linux2" or platform == "darwin":
    import subprocess
    print(get_master_volume_linux())
    set_master_volume_linux(50)

elif platform == "win32":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError:
        print("Error loading module: Windows modules\n")

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    vol_range = volume.GetVolumeRange()
    rawvol = volume.GetMasterVolumeLevel()
    print(rawvol)
    vol = int(round((rawvol - (vol_range[0])) / (vol_range[1] - (vol_range[0])) * 100, 0))
    print(vol)
    #print(volume.GetMute())
    #volume.SetMute(False, None)
    #volume.SetMasterVolumeLevel(-37, None) #-0.0 = 100%, -9.3 = 50%, -37 = 0%










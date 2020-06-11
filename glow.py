import pymem
import pymem.process
import keyboard
from win32gui import GetWindowText, GetForegroundWindow
import re

def get_sig(modname, pattern, extra = 0, offset = 0, relative = True):
    pm = pymem.Pymem("csgo.exe") #Application we are getting
    module = pymem.process.module_from_name(pm.process_handle, modname)
    bytes = pm.read_bytes(module.lpBaseOfDll, module.SizeOfImage)
    match = re.search(pattern, bytes).start()
    non_relative = pm.read_int(module.lpBaseOfDll + match + offset) + extra
    yes_relative = pm.read_int(module.lpBaseOfDll + match + offset) + extra - module.lpBaseOfDll
    return "0x{:X}".format(yes_relative) if relative else "0x{:X}".format(non_relative)

GetdwEntityList = get_sig('Client.dll', rb'\xBB....\x83\xFF\x01\x0F\x8C....\x3B\xF8', 0, 1)
dwEntityList = int(GetdwEntityList, 0)
GetdwLocalPlayer = get_sig('Client.dll', rb'\x8D\x34\x85....\x89\x15....\x8B\x41\x08\x8B\x48\x04\x83\xF9\xFF', 4, 3)
dwLocalPlayer = int(GetdwLocalPlayer, 0)
m_iTeamNum = (0xF4)
GetdwGlowObjectManager = get_sig('Client.dll', rb'\xA1....\xA8\x01\x75\x4B', 4, 1)
dwGlowObjectManager = int(GetdwGlowObjectManager, 0)
m_iGlowIndex = (0xA438)

def main():
    pm = pymem.Pymem("csgo.exe") #Application we are getting
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll #Process Handle

    #Glow Hack
    while True:
        glow_manager = pm.read_int(client + dwGlowObjectManager)
        for i in range(1, 32):
            entity = pm.read_int(client + dwEntityList + i * 0x10)

            if entity:
                entity_team_id = pm.read_int(entity + m_iTeamNum)
                entity_glow = pm.read_int(entity + m_iGlowIndex)

                if entity_team_id == 2: #terrorist
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(1)) #R
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(0)) #G
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(0)) #B
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(1)) #Alpha
                    pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1) #Enabling the Glow

                elif entity_team_id == 3: #counter terrorist
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x4, float(0)) #R
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x8, float(0)) #G
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0xC, float(1)) #B
                    pm.write_float(glow_manager + entity_glow * 0x38 + 0x10, float(1)) #Alpha
                    pm.write_int(glow_manager + entity_glow * 0x38 + 0x24, 1) #Enabling the Glow

        #Kill Key
        if keyboard.is_pressed('end'):
            exit(0)

if __name__ == '__main__':
    main()

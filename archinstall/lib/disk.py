from command import SysCommand
from pathlib import Path

PROPERTIES = [
    'path',
    'size',
    'type',
    'mountpoint',
    'label',
    'PTUUID',
    'PTTYPE',
]


class Disk:

    def __init__(self, path):
        self.partitions_cache = {}
    
        if self._is_disk(path):
            self.path = path
    
        self.information = self._get_information()

    def __len__(self):
        return len(self.partitions)


    def _is_disk(self, path):
        drives = SysCommand('lsblk -J -o path,type').json('blockdevices')
        for drive in drives:
            if drive['type'] != 'part' and drive['path'] == path:
                return True
        else:
            return False

    def _get_information(self):
        properties = ','.join(PROPERTIES)
        lsblk = SysCommand(f'lsblk -J -o {properties}').json('blockdevices')
        for drive in lsblk:
            if drive['path'] == self.path:
                return drive
        else:
            return None

    @property
    def partition_table(self):
        return self.information['pttype']
    
    @property
    def partitions(self):
        SysCommand(f'partprobe {self.path}')
        result = SysCommand(f'lsblk -J {self.path}').json('blockdevices')
        if len(result) > 0 and 'children' in result[0]:
            disk = result[0]
            root_path = f"/dev/{disk['name']}"

            for partition in disk['children']:
                partition_id = partition['name'].removeprefix(disk['name'])

                if partition_id is not self.partitions_cache or self.partitions_cache[partition_id].size != partition['size']:
                    self.partitions_cache[partition_id] = Partition(
                        path = root_path + partition_id,
                    )

        return { k: self.partitions_cache[k] for k in sorted(self.partitions_cache) }

    @property
    def size(self):
        return self.convert_size_to_gb(self.information['size'])
    

    @staticmethod
    def convert_size_to_gb(size):
        unit = size[-1]
        units = {
            'P': lambda x : float(x) * 2**(11),
            'T': lambda x : float(x) * 2**(10),
            'G': lambda x : float(x) * 2**(0),
            'M': lambda x : float(x) * 2**(-10),
            'K': lambda x : float(x) * 2**(-11),
            'B': lambda x : float(x) * 2**(-12)
        }
        return float(units.get(unit, lambda x: None)(size[:-1]))
         
    def partition(self, layout_partition):
        filesystem = layout_partition['filesystem']
        start = layout_partition['start']
        end = layout_partition['end']
        label = layout_partition['label']
        opts_partition = layout_partition['opts_partition']
        bootable = layout_partition['bootable']

        if len(self):
            SysCommand(f'parted --script {self.path}', message='Abrir el disco', debug=True)
            SysCommand('parted -script mklabel gpt', message='Crear tabla de particion', debug=True)
        
        SysCommand(f'parted --script mkpart "{label}" {filesystem} {start} {end}', message='Crear particion', debug=True)
        if bootable:
            SysCommand('parted --script set 1 esp on', message='Establecer como booteable', debug=True)
        self.partitions()
        

class Partition:

    def __init__(self, path, filesystem=None):
        if Path(path).exists():
            self.path = path
        self.information = SysCommand(f'lsblk -J -l -o {",".join(PROPERTIES)} {self.path}').json('blockdevices')[0]
        self.filesystem = filesystem

        self._size = self.information.get('size', None)
           
    @property
    def is_mounted(self):
        if self.information['mountpoint'] is not None:
            return True
        return False

    
    @property
    def size(self):
        return self._size
    
    def mount(self):
        pass


layout = {
    'filesystem': 'vfat',
    'start': '1Mb',
    'end': '524Mb',
    'label': 'EFI',
    'bootable': True
}

disk = Disk('/dev/sda')
disk.partition(layout)
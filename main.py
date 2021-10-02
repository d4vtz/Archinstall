from archinstall.lib.command import SysCommand

print(SysCommand('ls', cwd='/').split())
print(SysCommand('ls', cwd='/').split())
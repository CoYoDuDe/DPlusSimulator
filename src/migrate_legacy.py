#!/usr/bin/env python3
"""One-time, reversible migration of older package and settings identities."""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

NAME = 'DPlusSimulator'
ALIASES = ('DPlus_Simulator', 'DPlus-Simulator')
OLD_PREFIX = '/Settings/Devices/DPlusSim'
PREFIX = '/Settings/Devices/' + NAME
OPTIONS = Path('/data/setupOptions') / NAME
JOURNAL = OPTIONS / 'name-migration.json'
BACKUP = OPTIONS / 'migration-backup'
PACKAGE = Path(__file__).resolve().parents[1]


def write(value):
    OPTIONS.mkdir(mode=0o700, parents=True, exist_ok=True)
    if JOURNAL.is_symlink():
        raise ValueError('Refusing a symlink migration journal')
    fd, temporary = tempfile.mkstemp(prefix='.migration-', dir=OPTIONS)
    try:
        with os.fdopen(fd, 'w') as handle:
            json.dump(value, handle)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, JOURNAL)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def schema():
    return [json.loads(line) for line in (PACKAGE / 'DbusSettingsList').read_text().splitlines() if line.strip()]


def item(bus, path):
    import dbus
    return dbus.Interface(bus.get_object('com.victronenergy.settings', path), 'com.victronenergy.BusItem')


def get(bus, path):
    import dbus
    try:
        return item(bus, path).GetValue()
    except dbus.DBusException as error:
        if error.get_dbus_name() in ('org.freedesktop.DBus.Error.UnknownObject',
                                     'org.freedesktop.DBus.Error.UnknownMethod'):
            return None
        raise


def migrate_values(old, current):
    # Existing canonical settings always win, including explicit zero/empty.
    return {name: value for name, value in old.items() if name not in current}


def registry(bus):
    count = int(item(bus, '/Settings/PackageManager/Count').GetValue())
    entries = {}
    for index in range(count):
        path = '/Settings/PackageManager/' + str(index) + '/PackageName'
        entries[str(item(bus, path).GetValue())] = path
    return entries


def remove_legacy_menu(text):
    pattern = (r'(?m)(?:^[ \t]*//[^\n]*[dD]\+ [sS]imulator[^\n]*\n)?'
               r'^[ \t]*MbSubMenu\s*\{\s*\n'
               r'[ \t]*description:\s*qsTr\("(?:D\+ Simulator|DPlus[_ -]Simulator)"\)\s*\n'
               r'[ \t]*subpage:\s*Component\s*\{\s*PageSettingsDPlusSimulator\s*\{\s*\}\s*\}\s*\n'
               r'[ \t]*\}[ \t]*\n')
    return re.sub(pattern, '', text)


def clean_menu():
    target = Path('/opt/victronenergy/gui/qml/PageSettings.qml')
    if not target.exists():
        return
    original = target.read_text()
    updated = remove_legacy_menu(original)
    if original == updated:
        return
    backup = BACKUP / 'menu-before-cleanup.qml'
    if not backup.exists():
        shutil.copy2(target, backup)
    patch = BACKUP / 'cleanup-menu.patch'
    # Venus ships a reduced Python stdlib without difflib. A complete exact
    # hunk also refuses a concurrent change to any other addon's menu entries.
    before = original.splitlines(keepends=True)
    after = updated.splitlines(keepends=True)
    patch.write_text('--- ' + str(target) + '\n+++ ' + str(target) + '\n'
                     + '@@ -1,' + str(len(before)) + ' +1,' + str(len(after)) + ' @@\n'
                     + ''.join('-' + line for line in before)
                     + ''.join('+' + line for line in after))
    # Use SetupHelper's platform-tested patch binary for the surgical correction.
    binary = Path('/data/SetupHelper/patch')
    if subprocess.run([str(binary), '-v'], capture_output=True).returncode:
        binary = Path('/data/SetupHelper/patchBookworm')
    subprocess.run([str(binary), '--force', '--silent', '--reject-file=/dev/null',
                    str(target), str(patch)], check=True, capture_output=True, timeout=10)
    if target.read_text() != updated:
        raise RuntimeError('Legacy menu cleanup verification failed')
    print('Legacy DPlusSimulator menu entry removed')


def prepare(bus):
    entries = registry(bus)
    aliases = [name for name in ALIASES if name in entries]
    if len(aliases) > 1 or aliases and NAME in entries:
        raise RuntimeError('Both canonical and legacy package entries exist; resolve the duplicate before migration')
    state = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else None
    if state is None:
        old, current = {}, {}
        for definition in schema():
            suffix = definition['path'][len(PREFIX):]
            old_value = get(bus, OLD_PREFIX + suffix)
            new_value = get(bus, PREFIX + suffix)
            if old_value is not None:
                old[suffix] = old_value
            if new_value is not None:
                current[suffix] = new_value
        state = {'schema': 1, 'values': migrate_values(old, current),
                 'applied': False, 'finalized': False}
        write(state)
    BACKUP.mkdir(mode=0o700, parents=True, exist_ok=True)
    for index, name in enumerate(ALIASES):
        source = Path('/data') / name
        marker = Path('/etc/venus') / ('installedVersion-' + name)
        if source.is_symlink():
            raise RuntimeError('Refusing a symlink legacy package')
        if marker.exists():
            if not (source / 'setup').is_file():
                raise RuntimeError('Legacy uninstall source is missing')
            result = subprocess.run(['bash', str(source / 'setup'), 'uninstall', 'auto',
                                     'deferReboot', 'deferGuiRestart'], timeout=90)
            if result.returncode not in (0, 124) or marker.exists():
                raise RuntimeError('Legacy uninstall failed; settings backup retained')
        destination = BACKUP / ('package-' + str(index + 1))
        if source.exists():
            if destination.exists():
                raise RuntimeError('Legacy backup already exists; refusing overwrite')
            source.rename(destination)
        old_options = Path('/data/setupOptions') / name
        if old_options.exists():
            saved_options = BACKUP / ('options-' + str(index + 1))
            if old_options.is_symlink() or saved_options.exists():
                raise RuntimeError('Legacy options cannot be backed up safely')
            for candidate in old_options.iterdir():
                if candidate.is_symlink():
                    raise RuntimeError('Refusing symlink setup options')
                target = OPTIONS / candidate.name
                if not target.exists():
                    if candidate.is_dir():
                        shutil.copytree(candidate, target, symlinks=True)
                    else:
                        shutil.copy2(candidate, target)
            old_options.rename(saved_options)
    old_log = Path('/var/log/com.coyodude.dplussim')
    new_log = Path('/var/log/com.coyodude.DPlusSimulator')
    if old_log.exists():
        if old_log.is_symlink():
            raise RuntimeError('Refusing a symlink legacy log')
        old_log.rename(new_log if not new_log.exists() else BACKUP / 'previous-log')
    if aliases:
        import dbus
        if item(bus, entries[aliases[0]]).SetValue(dbus.String(NAME)) != 0:
            raise RuntimeError('PackageManager identity migration rejected')
        if str(item(bus, entries[aliases[0]]).GetValue()) != NAME:
            raise RuntimeError('PackageManager identity verification failed')
    clean_menu()
    print('DPlusSimulator package identity prepared; settings backup retained')


def apply(bus):
    state = json.loads(JOURNAL.read_text())
    if not state['applied']:
        import dbus
        for suffix, value in state['values'].items():
            typed = dbus.String(value) if isinstance(value, str) else dbus.Double(value) if isinstance(value, float) else dbus.Int32(value)
            target = item(bus, PREFIX + suffix)
            if target.SetValue(typed) != 0 or target.GetValue() != value:
                raise RuntimeError('Canonical settings migration rejected')
        state['applied'] = True
        write(state)
    print('DPlusSimulator settings preserved')


def finalize(bus):
    # IncludeHelpers may reconstruct the base menu during installation.
    # Retire orphaned legacy entries after that reconstruction as well.
    clean_menu()
    state = json.loads(JOURNAL.read_text())
    if state['finalized']:
        return
    if not state['applied'] or not Path('/etc/venus/installedVersion-DPlusSimulator').exists():
        raise RuntimeError('Canonical installation not complete; legacy settings retained')
    paths = [OLD_PREFIX + definition['path'][len(PREFIX):] for definition in schema()]
    # Use the same Venus settings command as SetupHelper's removeDbusSettings.
    subprocess.run(['dbus', '-y', 'com.victronenergy.settings', '/', 'RemoveSettings',
                    '%[ ' + ', '.join(json.dumps(path) for path in paths) + ' ]'],
                   check=True, capture_output=True, timeout=15)
    if any(get(bus, path) is not None for path in paths):
        raise RuntimeError('Legacy settings cleanup incomplete')
    state['finalized'] = True
    write(state)
    print('DPlusSimulator name migration complete')


if __name__ == '__main__':
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    import dbus
    bus = dbus.SystemBus()
    if sys.argv[1] == 'clean-menu':
        clean_menu()
    else:
        {'prepare': prepare, 'apply': apply, 'finalize': finalize}[sys.argv[1]](bus)

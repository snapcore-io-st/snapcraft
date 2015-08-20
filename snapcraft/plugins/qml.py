# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import snapcraft.common

from snapcraft.plugins.ubuntu import UbuntuPlugin


class QmlPlugin(snapcraft.BasePlugin):

    def __init__(self, name, options):
        super().__init__(name, options)

        class QmlPackageOptions:
            packages = [
                "qmlscene",
                "qtdeclarative5-qtmir-plugin",
                "mir-graphics-drivers-desktop",
                "qtubuntu-desktop",
                "ttf-ubuntu-font-family",
                # if there's a metapackage for these, please swap it in here:
                "qml-module-qt-labs-folderlistmodel",
                "qml-module-qt-labs-settings",
                "qml-module-qt-websockets",
                "qml-module-qtfeedback",
                "qml-module-qtgraphicaleffects",
                "qml-module-qtlocation",
                "qml-module-qtmultimedia",
                "qml-module-qtorganizer",
                "qml-module-qtpositioning",
                "qml-module-qtqml-models2",
                "qml-module-qtqml-statemachine",
                "qml-module-qtquick-controls",
                "qml-module-qtquick-dialogs",
                "qml-module-qtquick-layouts",
                "qml-module-qtquick-localstorage",
                "qml-module-qtquick-particles2",
                "qml-module-qtquick-privatewidgets",
                "qml-module-qtquick-window2",
                "qml-module-qtquick-xmllistmodel",
                "qml-module-qtquick2",
                "qml-module-qtsensors",
                "qml-module-qtsysteminfo",
                "qml-module-qttest",
                "qml-module-qtwebkit",
                "qml-module-ubuntu-connectivity",
                "qml-module-ubuntu-onlineaccounts",
                "qml-module-ubuntu-onlineaccounts-client",
            ]
            recommends = False

        self.ubuntu = UbuntuPlugin(name, QmlPackageOptions())

    def pull(self):
        return self.ubuntu.pull()

    def snap_files(self):
        include, exclude = self.ubuntu.snap_files()
        include.append('./etc/xdg/qtchooser/snappy-qt5.conf')
        return (include, exclude)

    def build_qt_config(self):
        arch = snapcraft.common.get_arch_triplet()
        configdir = os.path.join(self.installdir, 'etc', 'xdg', 'qtchooser')
        try:
            os.makedirs(configdir)
        except FileExistsError:
            pass
        config = open(os.path.join(configdir, 'snappy-qt5.conf'), 'w')
        config.write('./usr/lib/{}/qt5/bin\n'.format(arch))
        config.write('./usr/lib/{}\n'.format(arch))
        config.close
        return True

    def build(self):
        return self.ubuntu.build() and self.build_qt_config()

    def env(self, root):
        arch = snapcraft.common.get_arch_triplet()
        envs = self.ubuntu.env(root)
        envs.extend([
            "LD_LIBRARY_PATH=%s/usr/lib/%s:$LD_LIBRARY_PATH" % (root, arch),
            # Mir config
            "MIR_SOCKET=/run/mir_socket",
            "MIR_CLIENT_PLATFORM_PATH=%s/usr/lib/%s/mir/client-platform" % (root, arch),
            # XKB config
            "XKB_CONFIG_ROOT=%s/usr/share/X11/xkb" % root,
            # Qt Platform to Mir
            "QT_QPA_PLATFORM=ubuntumirclient",
            "QTCHOOSER_NO_GLOBAL_DIR=1",
            "QT_SELECT=snappy-qt5",
            # Qt Libs
            "LD_LIBRARY_PATH=%s/usr/lib/%s/qt5/libs:$LD_LIBRARY_PATH" % (root, arch),
            "LD_LIBRARY_PATH=%s/usr/lib/%s/pulseaudio:$LD_LIBRARY_PATH" % (root, arch),
            # Qt Modules
            "QT_PLUGIN_PATH=%s/usr/lib/%s/qt5/plugins" % (root, arch),
            "QML2_IMPORT_PATH=%s/usr/lib/%s/qt5/qml" % (root, arch),
            # Mesa Libs
            "LD_LIBRARY_PATH=%s/usr/lib/%s/mesa:$LD_LIBRARY_PATH" % (root, arch),
            "LD_LIBRARY_PATH=%s/usr/lib/%s/mesa-egl:$LD_LIBRARY_PATH" % (root, arch),
            # XDG Config
            "XDG_CONFIG_DIRS=%s/etc/xdg:$XDG_CONFIG_DIRS" % root,
            "XDG_CONFIG_DIRS=%s/usr/xdg:$XDG_CONFIG_DIRS" % root,
            "XDG_DATA_DIRS=%s/usr/share:$XDG_DATA_DIRS" % root,
            # Not good, needed for fontconfig
            "XDG_DATA_HOME=%s/usr/share" % root,
            # Font Config
            "FONTCONFIG_PATH=%s/etc/fonts/config.d" % root,
            "FONTCONFIG_FILE=%s/etc/fonts/fonts.conf" % root,
        ])
        return envs
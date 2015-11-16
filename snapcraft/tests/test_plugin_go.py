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

from unittest import mock

from snapcraft.plugins import go
from snapcraft import tests


class GoPluginTestCase(tests.TestCase):

    def setUp(self):
        super().setUp()

        patcher = mock.patch('snapcraft.common.run')
        self.run_mock = patcher.start()
        self.addCleanup(patcher.stop)

        patcher = mock.patch('sys.stdout')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_environment(self):
        class Options:
            source = 'http://github.com/testplug'

        plugin = go.GoPlugin('test', Options())
        self.assertEqual(plugin.env('myroot'), [
            'GOPATH=myroot/go',
            'CGO_LDFLAGS=$CGO_LDFLAGS"-Lmyroot/lib -Lmyroot/usr/lib '
            '-Lmyroot/lib/x86_64-linux-gnu '
            '-Lmyroot/usr/lib/x86_64-linux-gnu $LDFLAGS"'])

    def test_pull_local_sources(self):
        class Options:
            source = 'dir'

        plugin = go.GoPlugin('test-part', Options())

        os.makedirs(plugin.options.source)
        os.makedirs(plugin.sourcedir)

        plugin.pull()

        self.run_mock.assert_has_calls([
            mock.call(['env', 'GOPATH={}'.format(plugin._gopath),
                       'go', 'get', '-t', '-d', './dir/...'],
                      cwd=plugin._gopath_src)])

        self.assertTrue(os.path.exists(plugin._gopath))
        self.assertTrue(os.path.exists(plugin._gopath_src))
        self.assertFalse(os.path.exists(plugin._gopath_bin))

    def test_pull_with_no_local_sources(self):
        class Options:
            source = None

        plugin = go.GoPlugin('test-part', Options())
        plugin.pull()

        self.run_mock.assert_has_calls([])

        self.assertTrue(os.path.exists(plugin._gopath))
        self.assertTrue(os.path.exists(plugin._gopath_src))
        self.assertFalse(os.path.exists(plugin._gopath_bin))

    def test_build_with_local_sources(self):
        class Options:
            source = 'dir'

        plugin = go.GoPlugin('test-part', Options())

        os.makedirs(plugin.options.source)
        os.makedirs(plugin.sourcedir)

        plugin.pull()

        os.makedirs(plugin._gopath_bin)
        os.makedirs(plugin.builddir)

        plugin.build()

        self.run_mock.assert_has_calls([
            mock.call(['env', 'GOPATH={}'.format(plugin._gopath),
                       'go', 'get', '-t', '-d', './dir/...'],
                      cwd=plugin._gopath_src),
            mock.call(['env', 'GOPATH={}'.format(plugin._gopath),
                       'go', 'install', './dir/...'],
                      cwd=plugin._gopath_src),
        ])

        self.assertTrue(os.path.exists(plugin._gopath))
        self.assertTrue(os.path.exists(plugin._gopath_src))
        self.assertTrue(os.path.exists(plugin._gopath_bin))

    def test_build_with_no_local_sources(self):
        class Options:
            source = None

        plugin = go.GoPlugin('test-part', Options())

        os.makedirs(plugin.sourcedir)

        plugin.pull()

        os.makedirs(plugin._gopath_bin)
        os.makedirs(plugin.builddir)

        plugin.build()

        self.run_mock.assert_has_calls([])

        self.assertTrue(os.path.exists(plugin._gopath))
        self.assertTrue(os.path.exists(plugin._gopath_src))
        self.assertTrue(os.path.exists(plugin._gopath_bin))

# snapcraft.yaml syntax

The `snapcraft.yaml` file is the main entry point to create a snap through
Snapcraft. The main building blocks are parts and each defined part is
independent from each other. In addition to parts, there are attributes
that define the metadata for the snap package.

What follows is a list of all the attributes the `snapcraft.yaml` file can
contain.

* `name` (string)
  The name of the resulting snap.
* `version` (string)
  The version of the resulting snap.
* `summary` (string)
  A 78 character long summary for the snap.
* `description` (string)
  The description for the snap, this can and is expected to be a longer
  explanation for the snap.
* `icon` (string)
  Relative path in the snap to an icon to represent the package. It should
  be a 512x512 PNG or SVG file.
* `confinement` (string)
  The type of confinement supported by the snap. Can be either "devmode" (i.e.
  this snap doesn't support running under confinement) or "strict" (i.e. full
  confinement supported via interfaces).
* `grade` (string)
  This defines the quality grade of the snap. It can be either "devel" (i.e.
  a development version of the snap, so not to be published to the "stable" or
  "candidate" channels) or "stable" (i.e. a stable release or release
  candidate, which can be released to all channels).
* `assumes` (list of strings)
  A list of features that must be supported by the core in order for this snap
  to install.
* `epoch` (string)
  The epoch to which this revision of the snap belongs. This is used to specify
  upgrade paths. For example, `0` is epoch 0; `1*` is the upgrade path from 0 to
  1; `1` is epoch 1, etc.
* `apps` (yaml subsection)
  A map of keys for applications. These are either daemons or command line
  accessible binaries.
    * `command` (string)
      Specifies the internal command to expose. If it is a `daemon` this
      command is used to start the service.
    * `daemon` (string)
      If present, integrates the runnable as a system service. Valid values are
      `forking`, `notify`, `oneshot` and `simple`.
        - If set to `simple`, it is expected that the command configured is the
          main process.
        - If set to `oneshot`, it is expected that the command configured will
          exit once it's done (won't be a long-lasting process).
        - If set to `forking`, it is expected that the configured command will
          call fork() as part of its start-up. The parent process is expected
          to exit when start-up is complete and all communication channels are
          set up. The child continues to run as the main daemon process. This
          is the behavior of traditional UNIX daemons.
        - If set to `notify`, it is expected that the command configured will
          send a signal to systemd to indicate that it's running.
    * `stop-command` (string)
      Requires `daemon` to be specified and represents the command to run to
      stop the service.
    * `stop-timeout` (integer)
      Requires `daemon` to be specified. It is the length of time in seconds
      that the system will wait for the service to stop before terminating it
      via `SIGTERM` (and `SIGKILL` if that doesn't work).
* `icon` (string)
  Path to the icon that will be used for the snap.
* `parts` (yaml subsection)
  A map of part names to their own part configuration. Order in the file is
  not relevant (to aid copy-and-pasting). Check out the
  [parts section](snapcraft-parts.md) for some more concrete examples.
    * `plugin` (string)
      Specifies the plugin name that will manage this part. Snapcraft will pass
      to it all the other user-specified part options. If plugin is not
      defined, [the wiki](https://wiki.ubuntu.com/Snappy/Parts) will be
      searched for the part, the local values defined in the part will be used
      to compose the final part.
    * `after` (list of strings)
      Specifies any parts that should be built before this part is. This is
      mostly useful when a part needs a library or build tool built by another
      part. If the part defined in after is not defined locally, the part will
      be searched for in [the wiki](https://wiki.ubuntu.com/Snappy/Parts).
      *If a part is supposed to run after another, the prerequisite part will
      be staged before the dependent part starts its lifecycle.*
    * `stage-packages` (list of strings and/or sublists)
      A set of Ubuntu packages to be downloaded and unpacked to join the part
      before it's built. Note that these packages are not installed on the host.
      Like the rest of the part, all files from these packages will make it into
      the final snap unless filtered out via the `snap` keyword.

      One may simply specify packages in a flat list, in which case the packages
      will be fetched and unpacked regardless of build environment. In addition,
      a specific grammar made up of sub-lists is supported here that allows one
      to filter stage packages depending on various selectors (e.g. the target
      arch), as well as specify optional packages. The grammar is made up of two
      nestable statements: 'on' and 'try'.

          - on <selector>[,<selector>...]:
            - ...
          - else[ fail]:
            - ...

      The body of the 'on' clause is taken into account if every (AND, not OR)
      selector is true for the target build environment. Currently the only
      selectors supported are target architectures (e.g. amd64).

      If the 'on' clause doesn't match and it's immediately followed by an
      'else' clause, the 'else' clause must be satisfied. An 'on' clause without
      an 'else' clause is considered satisfied even if no selector matched. The
      'else fail' form allows erroring out if an 'on' clause was not matched.

          - try:
            - ...
          - else:
            - ...

      The body of the 'try' clause is taken into account only when all packages
      contained within it are valid. If not, if it's immediately followed by
      'else' clauses they are tried in order, and one of them must be satisfied.
      A 'try' clause with no 'else' clause is considered satisfied even if it
      contains invalid packages.
    * `build-packages` (list of strings)
      A list of Ubuntu packages to be installed on the host to aid in building
      the part. These packages will not go into the final snap.
    * `filesets` (yaml subsection)
      A dictionary with filesets, the key being a recognizable user defined
      string and its value a list of strings of files to be included or
      excluded. Globbing is achieved with `*` for either inclusions or
      exclusion. Exclusions are denoted by a `-`. Globbing is computed from
      the private sections of the part.
    * `organize` (yaml subsection)
      A dictionary exposing replacements, the key is the internal name whilst
      the value the exposed name, filesets will refer to the exposed named
      applied after organization is applied.
    * `stage` (list of strings)
      A list of files from a part's installation to expose in stage. Rules
      applying to the list here are the same as those of filesets. Referencing
      of fileset keys is done with a $ prefixing the fileset key, which will
      expand with the value of such key.
    * `prime` (list of strings)
      A list of files from a part's installation to expose in snap. Rules
      applying to the list here are the same as those of filesets. Referencing
      of fileset keys is done with a `$` prefixing the fileset key, which will
      expand with the value of such key.
    * `build-attributes` (list of strings)
      A list of special attributes that affect the build of this specific part.
      Supported attributes:

        - `no-system-libraries`:
          Do not automatically copy required libraries from the system to
          satisfy the dependencies of this part. This might be useful if one
          knows these dependencies will be satisfied in other manner, e.g. via
          content sharing from other snaps.

The `snapcraft.yaml` in any project is validated to be compliant to these
keywords, if there is any missing expected component or invalid value,
`snapcraft` will exit with an error.

Review the [metadata section](metadata.md) for some more explicit examples on
how to define commands, daemons or `config` declarations.

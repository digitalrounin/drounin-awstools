# drounin-awstools (draws)

Collection of simple AWS related tools.

Usage:

  ```
  $ draws-instance-statuses --help
  ```

## Installation

To install under `~/.local` with virtualenvs taken care of:

  ```
  $ pip install --user git+https://github.com/digitalrounin/drounin-awstools.git
  ```

Make sure that `~/.local/bin` is in your `PATH`.  Something like this in your
`~/.profile` helps:

  ```
  # local user bin
  export USER_LOCAL="$HOME/.local"
  if [ -d "$USER_LOCAL" ]; then
      if [ -d "$USER_LOCAL/bin" ]; then
          export PATH="$USER_LOCAL/bin:$PATH"
      fi

      if [ -d "$USER_LOCAL/share/man" ]; then
          export MANPATH="$USER_LOCAL/share/man:$MANPATH"
      fi
  fi
  ```



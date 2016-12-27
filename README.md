# drounin-awstools (draws)

Collection of simple AWS related tools:
  - `draws-instance-change-state` - Facilitates changing multiple _EC2_
    instance states to either running, shutdown or terminated.  Instances can
    be selected bit _instance_id_, _Name_ tage, or a regex against the
    _Name_ tag.
  - `draws-instance-statuses` - Displays status of all instances in pretty
    colors.

Usage:

  ```
  $ draws-instance-statuses --help
  $ draws-instance-change-state --help
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

## TODO

  - Add _IAM_ policy information.
  - Select instances by tags in `draws-instance-change-state`
  - Potential merge `draws-instance-statuses` and
    `draws-instance-change-state`.

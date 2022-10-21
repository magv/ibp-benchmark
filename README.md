# Integration-by-Parts relation solver benchmark

This project contains:
- templates for multiple IBP solver configurations;
- definitions of IBP reduction problems that can be filled into
  those templates;
- tool to run the solvers, and measure their performance and
  memory usage.

## How to use

Start by running

    ./generate.py

This will generate the problem directories in `problems/*`: one
directory for each problem and solution method.

To run the reduction, just execute `run.sh` in any given directory.
Alternatively (and better), run `./measure problem/<directory>`
to run `run.sh` and measure its memory and disk usage over time.

You will need to install the IBP solvers for this to work. In particular:

- the environment variable `$FIREPATH` should point to the [FIRE6] installation directory;
- the command `kira` should correspond to the latest [Kira] version;
- the command `ratracer` should correspond to the latest [Ratracer] build.

[FIRE6]: https://bitbucket.org/feynmanIntegrals/fire/src/master/
[Kira]: https://gitlab.com/kira-pyred/kira/
[Ratracer]: https://github.com/magv/ratracer

After `./measure` has been called on the problems of interest,
`./report.py` can print a nicely formatted report log.

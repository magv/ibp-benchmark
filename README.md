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

## Results

Results on an openSUSE 15.3 machine with an AMD EPYC 7282 processor:

### box1l

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    |     45.9 s |      -- |       -- |        -- |     -- |  407 MB |  1.6 GB |
| fire-nohint             |     38.0 s |      -- |       -- |        -- |     -- |  442 MB |  1.6 GB |
| kira                    |     13.6 s |      -- |       -- |        -- |     -- |  310 MB | 42.0 MB |
| kira-firefly            |     46.7 s |  38.5 s |  14.9 ms |  5.7 10^3 |  27.6% |  1.4 GB | 59.5 MB |
| kira-ratracer           |     43.8 s |  36.4 s |   4.8 ms |  6.9 10^3 |  11.3% |  1.4 GB | 87.2 MB |
| kira-ratracer-eps0      |      9.7 s |   3.5 s |   2.8 ms |  6.2 10^2 |   6.1% |  606 MB | 52.8 MB |
| kira-ratracer-eps0-scan |     12.5 s |   6.1 s |   2.9 ms |  9.2 10^2 |   5.5% |  514 MB | 51.9 MB |
| kira-ratracer-eps1      |     21.5 s |  12.7 s |   5.4 ms |  1.1 10^3 |   6.0% |  1.3 GB | 85.7 MB |
| kira-ratracer-eps1-scan |     22.2 s |  15.2 s |   5.0 ms |  1.2 10^3 |   4.8% |  1.1 GB | 84.0 MB |
| kira-ratracer-eps2      |     25.5 s |  17.0 s |   6.1 ms |  1.1 10^3 |   5.1% |  2.0 GB |  111 MB |
| kira-ratracer-eps2-scan |     32.2 s |  22.7 s |   5.6 ms |  1.3 10^3 |   3.9% |  1.6 GB |  108 MB |
| kira-ratracer-scan      |     40.5 s |  33.4 s |   5.0 ms |  5.7 10^3 |  10.6% |  1.2 GB | 74.1 MB |

### box2l

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    | !! 18000 s |      -- |       -- |        -- |     -- |  3.5 GB | 80.3 GB |
| fire-nohint             |     3848 s |      -- |       -- |        -- |     -- |  3.9 GB | 21.1 GB |
| kira                    |     1126 s |      -- |       -- |        -- |     -- |  5.8 GB |  1.9 GB |
| kira-firefly            |     3933 s |  3899 s |   225 ms |  6.3 10^4 |  45.8% | 28.8 GB |  3.1 GB |
| kira-ratracer           |      579 s |   518 s |  23.9 ms |  2.0 10^4 |  11.6% | 14.2 GB |  1.0 GB |
| kira-ratracer-eps0      |      101 s |  61.5 s |  23.3 ms |  2.5 10^3 |  11.8% | 12.3 GB |  1.3 GB |
| kira-ratracer-eps0-scan |      134 s |  95.6 s |  22.6 ms |  2.3 10^3 |   6.9% | 12.4 GB |  1.3 GB |
| kira-ratracer-eps1      |      189 s |   136 s |  38.7 ms |  2.8 10^3 |   9.9% | 12.6 GB |  1.4 GB |
| kira-ratracer-eps1-scan |      256 s |   205 s |  37.7 ms |  2.6 10^3 |   5.9% | 12.1 GB |  1.4 GB |
| kira-ratracer-eps2      |      272 s |   205 s |  50.9 ms |  2.8 10^3 |   8.6% | 18.1 GB |  1.5 GB |
| kira-ratracer-eps2-scan |      366 s |   304 s |  49.4 ms |  2.6 10^3 |   5.2% | 15.5 GB |  1.5 GB |
| kira-ratracer-scan      |      435 s |   383 s |  23.4 ms |  1.3 10^4 |  10.2% | 12.2 GB |  833 MB |

### diamond2l

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    |     20.2 s |      -- |       -- |        -- |     -- |  352 MB |  1.8 GB |
| fire-nohint             |     15.4 s |      -- |       -- |        -- |     -- |  269 MB |  1.8 GB |
| kira                    |      8.7 s |      -- |       -- |        -- |     -- |  177 MB | 26.6 MB |
| kira-firefly            |     23.2 s |  17.8 s |   3.8 ms |  5.8 10^3 |  15.3% |  762 MB | 29.4 MB |
| kira-ratracer           |     17.2 s |  12.1 s |   427 us |  9.1 10^3 |   4.0% |  1.0 GB | 45.8 MB |
| kira-ratracer-eps0      |      6.5 s |   2.6 s |   405 us |  4.7 10^2 |   0.9% |  562 MB | 16.5 MB |
| kira-ratracer-eps0-scan |      8.6 s |   4.9 s |   412 us |  7.6 10^2 |   0.8% |  408 MB | 15.9 MB |
| kira-ratracer-eps1      |      9.4 s |   5.0 s |   635 us |  5.6 10^2 |   0.9% |  917 MB | 27.7 MB |
| kira-ratracer-eps1-scan |     12.8 s |   8.5 s |   683 us |  8.1 10^2 |   0.8% |  815 MB | 26.8 MB |
| kira-ratracer-eps2      |     12.6 s |   7.3 s |   806 us |  5.5 10^2 |   0.8% |  1.3 GB | 38.4 MB |
| kira-ratracer-eps2-scan |     17.6 s |  12.6 s |   858 us |  8.1 10^2 |   0.7% |  1.1 GB | 37.1 MB |
| kira-ratracer-scan      |     16.0 s |  11.6 s |   438 us |  5.8 10^3 |   2.7% |  558 MB | 28.7 MB |

### diamond3l

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    |      134 s |      -- |       -- |        -- |     -- |  749 MB | 11.4 GB |
| fire-nohint             |      112 s |      -- |       -- |        -- |     -- |  805 MB | 11.4 GB |
| kira                    |     21.3 s |      -- |       -- |        -- |     -- |  858 MB |  118 MB |
| kira-firefly            |      116 s |  99.7 s |  57.8 ms |  3.3 10^3 |  23.8% |  2.8 GB |  116 MB |
| kira-ratracer           |     69.1 s |  48.2 s |   2.3 ms |  6.7 10^3 |   3.9% |  4.1 GB |  184 MB |
| kira-ratracer-eps0      |     29.7 s |  12.6 s |   3.2 ms |  4.1 10^2 |   1.3% |  3.7 GB |  103 MB |
| kira-ratracer-eps0-scan |     42.6 s |  25.9 s |   3.3 ms |  6.7 10^2 |   1.1% |  3.7 GB | 99.5 MB |
| kira-ratracer-eps1      |     41.7 s |  21.7 s |   5.8 ms |  4.1 10^2 |   1.4% |  4.9 GB |  159 MB |
| kira-ratracer-eps1-scan |     66.3 s |  47.0 s |   5.1 ms |  6.6 10^2 |   0.9% |  3.8 GB |  154 MB |
| kira-ratracer-eps2      |     51.1 s |  28.5 s |   6.7 ms |  4.1 10^2 |   1.2% |  6.7 GB |  208 MB |
| kira-ratracer-eps2-scan |     84.9 s |  63.2 s |   6.8 ms |  6.8 10^2 |   0.9% |  5.0 GB |  202 MB |
| kira-ratracer-scan      |     72.6 s |  55.7 s |   2.2 ms |  4.3 10^3 |   2.2% |  3.7 GB |  116 MB |

### tth2l_b16

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    |  !! 1936 s |      -- |       -- |        -- |     -- |  1.8 GB |  4.4 GB |
| fire-nohint             | !! 18000 s |      -- |       -- |        -- |     -- |  4.3 GB | 36.1 GB |
| kira                    |     21.8 s |      -- |       -- |        -- |     -- |  1.1 GB | 14.7 MB |
| kira-firefly            |      231 s |   224 s |   4.7 ms |  1.5 10^5 |  40.3% |  741 MB | 20.1 MB |
| kira-ratracer           |      210 s |   204 s |   555 us |  1.9 10^5 |   6.5% |  1.0 GB | 42.3 MB |
| kira-ratracer-eps0      |     20.3 s |  15.0 s |   578 us |  3.5 10^4 |  16.6% |  501 MB | 20.1 MB |
| kira-ratracer-eps0-scan |     27.1 s |  22.2 s |   571 us |  2.8 10^4 |   9.1% |  374 MB | 18.7 MB |
| kira-ratracer-eps1      |     28.1 s |  22.5 s |   686 us |  3.5 10^4 |  13.2% |  818 MB | 29.0 MB |
| kira-ratracer-eps1-scan |     41.6 s |  36.1 s |   691 us |  2.9 10^4 |   6.9% |  608 MB | 26.8 MB |
| kira-ratracer-eps2      |     32.8 s |  26.8 s |   767 us |  3.5 10^4 |  12.4% |  971 MB | 33.5 MB |
| kira-ratracer-eps2-scan |     50.6 s |  44.8 s |   773 us |  2.9 10^4 |   6.2% |  741 MB | 31.0 MB |
| kira-ratracer-scan      |      112 s |   106 s |   531 us |  1.2 10^5 |   7.5% |  537 MB | 30.2 MB |

### tth2l_b25

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    |   !! 513 s |      -- |       -- |        -- |     -- |  781 MB | 27.2 GB |
| fire-nohint             | !! 18000 s |      -- |       -- |        -- |     -- |  2.7 GB |  115 GB |
| kira                    |     3156 s |      -- |       -- |        -- |     -- |  4.4 GB |  1.4 GB |
| kira-firefly            |    13407 s | 13367 s |    1.2 s |  7.7 10^4 |  82.8% |  4.2 GB |  1.6 GB |
| kira-ratracer           |     2579 s |  2451 s |  59.0 ms |  7.6 10^4 |  23.0% |  3.3 GB |  2.2 GB |
| kira-ratracer-eps0      |      799 s |   697 s |  75.0 ms |  6.1 10^3 |   8.2% |  2.0 GB |  2.4 GB |
| kira-ratracer-eps0-scan |     3368 s |  3268 s |  74.5 ms |  1.7 10^4 |   4.7% |  2.4 GB |  2.2 GB |
| kira-ratracer-eps1      |     1088 s |   970 s |  90.6 ms |  6.1 10^3 |   7.1% |  3.1 GB |  2.2 GB |
| kira-ratracer-eps1-scan |     4906 s |  4789 s |  88.9 ms |  1.7 10^4 |   3.9% |  3.7 GB |  2.2 GB |
| kira-ratracer-eps2      |     1324 s |  1193 s |   106 ms |  6.1 10^3 |   6.7% |  4.0 GB |  2.4 GB |
| kira-ratracer-eps2-scan |     6032 s |  5905 s |   103 ms |  1.7 10^4 |   3.6% |  4.7 GB |  2.4 GB |
| kira-ratracer-scan      |     2759 s |  2659 s |  57.1 ms |  5.3 10^4 |  14.3% |  2.4 GB |  2.2 GB |

### xbox2l2m

| method                  |       time | ff_time | ff_probe | ff_probes | ff_eff |     ram |    disk |
| :---------------------- | ---------: | ------: | -------: | --------: | -----: | ------: | ------: |
| fire                    | !! 18000 s |      -- |       -- |        -- |     -- |  4.2 GB | 28.3 GB |
| fire-nohint             | !! 18000 s |      -- |       -- |        -- |     -- |  4.3 GB | 28.8 GB |
| kira                    |    15199 s |      -- |       -- |        -- |     -- |  9.0 GB |  549 MB |
| kira-firefly            |     2482 s |  2470 s |   182 ms |  1.0 10^5 |  95.9% |  2.1 GB | 74.8 MB |
| kira-ratracer           |      713 s |   692 s |  23.4 ms |  1.7 10^5 |  72.3% |  1.8 GB |  489 MB |
| kira-ratracer-eps0      |      190 s |   163 s |  47.8 ms |  2.4 10^4 |  89.3% |  865 MB |  2.7 GB |
| kira-ratracer-eps0-scan |      153 s |   126 s |  47.6 ms |  1.7 10^4 |  81.9% |  720 MB |  2.7 GB |
| kira-ratracer-eps1      |      382 s |   351 s |  58.5 ms |  4.2 10^4 |  88.2% |  1.3 GB |  2.8 GB |
| kira-ratracer-eps1-scan |      299 s |   269 s |  58.0 ms |  3.0 10^4 |  80.2% |  1.2 GB |  2.7 GB |
| kira-ratracer-eps2      |      710 s |   673 s |  70.1 ms |  6.6 10^4 |  86.3% |  2.2 GB |  2.9 GB |
| kira-ratracer-eps2-scan |      532 s |   497 s |  69.7 ms |  4.6 10^4 |  80.6% |  1.8 GB |  2.9 GB |
| kira-ratracer-scan      |      412 s |   393 s |  23.3 ms |  1.0 10^5 |  77.0% |  1.3 GB |  413 MB |

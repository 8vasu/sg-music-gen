# sg-music-gen
An [acestep.cpp](https://github.com/ServeurpersoCom/acestep.cpp)-based command-line music generator for *nix.

## Requirements and setup
1. Optionally, an NVIDIA GPU with a [driver](https://www.nvidia.com/en-us/drivers/) recent enough for the base image's CUDA; without one, generation runs on the CPU.

2. Install [Git](https://git-scm.com/), [Docker](https://docs.docker.com/engine/install/) and `make`; for the GPU, also the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

3. Clone this repository and `cd` to it:

```
$ git clone https://github.com/8vasu/sg-music-gen.git
$ cd sg-music-gen
```

## Build and test
1. Install:

```
$ make build && make models
```

2. Test, on the GPU if there is one, then on the CPU, then with the lyrics in `lyrics.txt`:

```
$ make test
$ make test-cpu
$ make test-lyrics
```

3. Clean up the test artifacts:

```
$ make clean
```

4. Remove the image and the downloaded models:

```
$ make remove
```

## Usage
Symlink `sg-music-gen.sh` into a directory in your `PATH`, under any name, say `sgsong`:

```
$ ln -s "$PWD/sg-music-gen.sh" ~/.local/bin/sgsong
```

Symlink it rather than copying it: the script finds this directory by resolving the link. `sgsong OUTPUT CAPTION` writes `OUTPUT.mp3`, and `OUTPUT.json` with the lyrics and metadata the language model chose, into the current directory. Check the help message for all options:

```
$ sgsong -h
```

Examples:

```
$ sgsong rain "ambient piano, soft rain" --lyrics "[Instrumental]" --duration 60
$ sgsong summer "upbeat indie pop, female vocals" --duration 90
$ sgsong ballad "slow acoustic ballad" --lyrics "$(cat lyrics.txt)" --bpm 70 --keyscale "D major"
$ sgsong again "slow acoustic ballad" --seed 42 --output-format wav16
$ GGML_BACKEND=CPU sgsong cpu "lo-fi hip hop" --duration 30
```

On a GPU with little memory, add `--vae-chunk 128`; if the output is silence or noise on an older GPU, add `--clamp-fp16`.

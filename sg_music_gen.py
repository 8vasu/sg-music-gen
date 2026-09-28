#!/usr/bin/python3

# sg-music-gen - An acestep.cpp-based command-line music generator for *nix.
# Copyright (C) 2026 Soumendra Ganguly

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import json
import shutil
import typing
import inspect
import pathlib
import argparse
import tempfile
import subprocess
from typing import Annotated

REQUEST, LM, SYNTH = "request", "ace-lm", "ace-synth"
OPTION_PREFIX, WORD_SEP, OPTION_SEP = "--", "_", "-"


def option(name):
    """Return the command line option spelled from a parameter name."""
    return OPTION_PREFIX + name.replace(WORD_SEP, OPTION_SEP)


def arguments(options):
    """Return a tool's argument list: a flag for True, a flag and its value otherwise."""
    return [part for key, value in options.items()
            for part in ([option(key)] if value is True else [option(key), str(value)])]


def tagged(func, values, tag):
    """Return the set values of func's parameters whose annotation carries tag."""
    return {name: values[name] for name, param in inspect.signature(func).parameters.items()
            if tag in typing.get_args(param.annotation)[2:]
            and values[name] is not None and values[name] is not False}


def gen(output: Annotated[str, "output file name, without extension"],
        caption: Annotated[str, "style: genre, mood, instruments, vocals", REQUEST],
        *,
        models: Annotated[str, "directory of GGUF models", LM, SYNTH],
        lyrics: Annotated[str, "lyrics with [Verse], [Chorus], ... tags, or [Instrumental]; "
                               "unset lets the language model write them", REQUEST] = None,
        duration: Annotated[float, "length in seconds", REQUEST] = None,
        bpm: Annotated[int, "tempo in beats per minute", REQUEST] = None,
        keyscale: Annotated[str, "key and scale, e.g. 'C major'", REQUEST] = None,
        timesignature: Annotated[str, "beats per bar", REQUEST] = None,
        vocal_language: Annotated[str, "lyrics language code, e.g. en", REQUEST] = None,
        seed: Annotated[int, "random seed for a reproducible result", REQUEST] = None,
        inference_steps: Annotated[int, "diffusion steps", REQUEST] = None,
        output_format: Annotated[str, "audio format, e.g. mp3 or wav16", REQUEST] = None,
        max_seq: Annotated[int, "language model context in tokens", LM] = None,
        vae_chunk: Annotated[int, "latent frames per VAE decode tile; lower saves GPU memory",
                             SYNTH] = None,
        clamp_fp16: Annotated[bool, "clamp values to the float16 range, for older GPUs",
                              LM, SYNTH] = False,
        lm: Annotated[bool, "run the language model, which fills in unset lyrics and "
                            "metadata"] = True):
    """Generate a song with acestep.cpp; save it and its final request as OUTPUT.<ext>."""
    values = locals()
    with tempfile.TemporaryDirectory() as tmp:
        work = pathlib.Path(tmp)
        current = work / pathlib.Path(output).name
        current.write_text(json.dumps(tagged(gen, values, REQUEST)))
        made = []
        for tool in (LM, SYNTH) if lm else (SYNTH,):
            before = set(work.iterdir())
            subprocess.run([tool, *arguments(tagged(gen, values, tool) | {REQUEST: current})],
                           check=True)
            new = set(work.iterdir()) - before
            if not new:
                sys.exit(f"{tool} produced no output")
            current, = new
            made.append(current)
        for file in made:
            target = output + file.suffix
            shutil.copyfile(file, target)
            print(target)


def parser_for(func):
    """Return a parser whose arguments come from func's signature and Annotated help."""
    parser = argparse.ArgumentParser(description=inspect.getdoc(func))
    for param in inspect.signature(func).parameters.values():
        kind, text = typing.get_args(param.annotation)[:2]
        if param.kind is param.POSITIONAL_OR_KEYWORD:
            parser.add_argument(param.name, type=kind, help=text)
            continue
        action = dict(action=argparse.BooleanOptionalAction) if kind is bool else dict(type=kind)
        parser.add_argument(option(param.name), help=text, required=param.default is param.empty,
                            default=argparse.SUPPRESS, **action)
    return parser


def main():
    """Parse the command line from gen's signature and run it."""
    try:
        gen(**vars(parser_for(gen).parse_args()))
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()

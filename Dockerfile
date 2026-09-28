FROM nvcr.io/nvidia/pytorch:26.05-py3

RUN apt-get update && \
    apt-get install -y --no-install-recommends aria2 && \
    rm -rf /var/lib/apt/lists/*

ARG UPSTREAM
ARG REFRESH
ARG SRC=/opt/acestep
WORKDIR $SRC
RUN git clone --depth 1 --recurse-submodules --shallow-submodules "$UPSTREAM" . && \
    cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON -DGGML_BACKEND_DL=ON -DGGML_CPU_ALL_VARIANTS=ON && \
    cmake --build build -j "$(nproc)"

ENV PATH=$SRC/build:$SRC:$PATH

NAME = sg-music-gen
UPSTREAM = https://github.com/ServeurpersoCom/acestep.cpp.git
MODELS = $(CURDIR)/models
APP = /app
DATA = /models
TEST = test
TEST_CPU = $(TEST)-cpu
TEST_LYRICS = $(TEST)-lyrics
LYRICS = lyrics.txt
TEST_ARGS = --duration 30 --vae-chunk 128
INSTRUMENTAL = "calm acoustic guitar" --lyrics "[Instrumental]" $(TEST_ARGS)
RUN = docker run --rm --user $$(id -u):$$(id -g) -v $(CURDIR):$(APP):ro

.PHONY: build models test test-cpu test-lyrics clean remove

build:
	docker build --build-arg UPSTREAM=$(UPSTREAM) --build-arg REFRESH=$$(date +%s) -t $(NAME) - < Dockerfile

models:
	mkdir -p $(MODELS)
	$(RUN) -v $(MODELS):$(DATA) $(NAME) sh -c 'cd "$$(mktemp -d)" && PATH=$(APP):$$PATH \
	    models.sh --quant Q4_K_M --lm 0.6B 3>&1 >/dev/null | aria2c -i - -d $(DATA) -c -x16 -s16'

test:
	./$(NAME).sh $(TEST) $(INSTRUMENTAL)

test-cpu:
	GGML_BACKEND=CPU ./$(NAME).sh $(TEST_CPU) $(INSTRUMENTAL)

test-lyrics:
	./$(NAME).sh $(TEST_LYRICS) "slow acoustic ballad, male vocals" --lyrics "$$(cat $(LYRICS))" $(TEST_ARGS)

clean:
	rm -f $(TEST).* $(TEST_CPU).* $(TEST_LYRICS).*

remove:
	docker rmi $(NAME)
	rm -rf $(MODELS)

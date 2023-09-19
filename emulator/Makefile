SDL2_CONFIG = sdl2-config

CXXFLAGS_FAST = -march=native -O3

CXXFLAGS += -Wall -Wextra $(CXXFLAGS_FAST) `$(SDL2_CONFIG) --cflags`
LDFLAGS += `$(SDL2_CONFIG) --libs`

profile: CXXFLAGS += -pg -g -O0 -Wall -Wextra `$(SDL2_CONFIG) --cflags`
profile: LDFLAGS += `$(SDL2_CONFIG) --libs` -pg -g


CXXFILES = src/main.cpp \
		   src/cpu.cpp \
		   src/mem.cpp

OBJS = $(addsuffix .o, $(basename $(CXXFILES)))

.PHONY: all
all: emu

emu: $(OBJS)
	$(CXX) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.cpp
	$(CXX) -o $@ -c $< $(CXXFLAGS)

clean:
	rm -f emu $(OBJS)

profile: emu
	./emu
	gprof --line emu gmon.out > profile.txt

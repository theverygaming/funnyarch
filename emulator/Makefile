SDL2_CONFIG = sdl2-config

CXXFLAGS += -O3 -Wall -Wextra `$(SDL2_CONFIG) --cflags`
LDFLAGS += `$(SDL2_CONFIG) --libs`

CXXFILES = src/main.cpp \
		   src/cpu.cpp \
		   src/mem.cpp \
		   src/sdl.cpp

OBJS = $(addsuffix .o, $(basename $(CXXFILES)))

.PHONY: all
all: emu

emu: $(OBJS)
	$(CXX) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.cpp
	$(CXX) -o $@ -c $< $(CXXFLAGS)

clean:
	rm -f emu $(OBJS)

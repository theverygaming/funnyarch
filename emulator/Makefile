SDL2_CONFIG = sdl2-config

CXXFLAGS_FAST = -march=native -O3

CXXFLAGS += -Wall -Wextra $(CXXFLAGS_FAST) `$(SDL2_CONFIG) --cflags`
LDFLAGS += `$(SDL2_CONFIG) --libs` -lGL

profile: CXXFLAGS += -pg -g -O0 -Wall -Wextra `$(SDL2_CONFIG) --cflags`
profile: LDFLAGS += `$(SDL2_CONFIG) --libs` -pg -g -lGL


CXXFILES = src/main.cpp \
		   src/cpu.cpp \
		   src/mem.cpp \
		   src/imgui/imgui_demo.cpp \
		   src/imgui/imgui_draw.cpp \
		   src/imgui/imgui_impl_sdl2.cpp \
		   src/imgui/imgui_impl_sdlrenderer2.cpp \
		   src/imgui/imgui_tables.cpp \
		   src/imgui/imgui_widgets.cpp \
		   src/imgui/imgui.cpp


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

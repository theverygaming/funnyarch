TARGET = linux
ifeq ($(TARGET),linux)
# default is used for CXX
SDL2_CONFIG = sdl2-config
CXXFLAGS_FAST = -march=native -O3
CXXFLAGS += -Wall -Wextra $(CXXFLAGS_FAST) `$(SDL2_CONFIG) --cflags`
LDFLAGS += `$(SDL2_CONFIG) --libs`
else
ifeq ($(TARGET),wasm)
CXX = em++
CXXFLAGS_FAST = -O3
CXXFLAGS += -Wall -Wextra $(CXXFLAGS_FAST) -sUSE_SDL=2
LDFLAGS += -s TOTAL_MEMORY=70057984 -sALLOW_MEMORY_GROWTH=1 -sUSE_SDL=2 --preload-file output.bin
TARGET_EXTRADEPS = output.bin
TARGET_FILE_EXTENSION = .html
else
ifeq ($(TARGET),linux-gcov)
# default is used for CXX
SDL2_CONFIG = sdl2-config
CXXFLAGS += -Wall -Wextra -g -fprofile-arcs -ftest-coverage `$(SDL2_CONFIG) --cflags`
LDFLAGS += `$(SDL2_CONFIG) --libs` -lgcov --coverage
else
$(error unknown TARGET)
endif
endif
endif


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
all: emu$(TARGET_FILE_EXTENSION)

emu$(TARGET_FILE_EXTENSION): $(TARGET_EXTRADEPS) $(OBJS)
	$(CXX) -o $@ $(OBJS) $(LDFLAGS)

%.o: %.cpp
	$(CXX) -o $@ -c $< $(CXXFLAGS)

clean:
	rm -f emu
	rm -f emu.data emu.html emu.js emu.wasm
	rm -f $(OBJS)

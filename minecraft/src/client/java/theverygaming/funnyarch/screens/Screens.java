package theverygaming.funnyarch.screens;

import net.minecraft.client.gui.screen.ingame.HandledScreens;
import theverygaming.funnyarch.block.Blocks;

public class Screens {
    public static void initialize() {
        HandledScreens.register(Blocks.SCREEN_SCREEN_HANDLER, ScreenScreen::new);
        theverygaming.funnyarch.Funnyarch.LOGGER.info("hello client screen world!!!!!!!!");
    }
}

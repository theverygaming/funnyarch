package theverygaming.funnyarch;

import net.fabricmc.api.ClientModInitializer;

public class FunnyarchClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        theverygaming.funnyarch.screens.Screens.initialize();
    }
}

package theverygaming.funnyarch.block;

import net.fabricmc.fabric.api.item.v1.FabricItemSettings;
import net.fabricmc.fabric.api.object.builder.v1.block.FabricBlockSettings;
import net.fabricmc.fabric.api.object.builder.v1.block.entity.FabricBlockEntityTypeBuilder;
import net.minecraft.block.Block;
import net.minecraft.block.entity.BlockEntityType;
import net.minecraft.item.BlockItem;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.resource.featuretoggle.FeatureFlags;
import net.minecraft.screen.ScreenHandlerType;
import net.minecraft.util.Identifier;

public class Blocks {
    public static final Identifier SCREEN_BLOCK_IDENTIFIER = new Identifier("funnyarch", "screen_block");
    public static final Block SCREEN_BLOCK = new ScreenBlock(
            FabricBlockSettings.create().hardness(1.5f).resistance(6.0f).requiresTool());
    public static final BlockEntityType<ScreenBlockEntity> SCREEN_BLOCK_ENTITY = Registry.register(
            Registries.BLOCK_ENTITY_TYPE, SCREEN_BLOCK_IDENTIFIER,
            FabricBlockEntityTypeBuilder.create(ScreenBlockEntity::new, SCREEN_BLOCK).build(null));
    public static final ScreenHandlerType<ScreenScreenHandler> SCREEN_SCREEN_HANDLER = new ScreenHandlerType<ScreenScreenHandler>(
            ScreenScreenHandler::new, FeatureFlags.VANILLA_FEATURES);

    public static void initialize() {
        Registry.register(Registries.BLOCK, SCREEN_BLOCK_IDENTIFIER, SCREEN_BLOCK);
        Registry.register(Registries.ITEM, SCREEN_BLOCK_IDENTIFIER,
                new BlockItem(SCREEN_BLOCK, new FabricItemSettings()));

        theverygaming.funnyarch.Funnyarch.LOGGER.info("hello screen world!!!!!!!!");
    }
}

package theverygaming.funnyarch.item;

import net.fabricmc.fabric.api.itemgroup.v1.FabricItemGroup;
import net.minecraft.item.ItemGroup;
import net.minecraft.item.ItemStack;
import net.minecraft.registry.Registries;
import net.minecraft.registry.Registry;
import net.minecraft.text.Text;
import net.minecraft.util.Identifier;

public class Items {
    public static final ItemGroup FUNNYARCH = FabricItemGroup.builder()
            .icon(() -> new ItemStack(theverygaming.funnyarch.block.Blocks.SCREEN_BLOCK))
            .displayName(Text.translatable("itemGroup.funnyarch.main_group"))
            .entries((context, entries) -> {
                entries.add(theverygaming.funnyarch.block.Blocks.SCREEN_BLOCK);
                entries.add(theverygaming.funnyarch.block.Blocks.BUS_CABLE_BLOCK);
            })
            .build();

    public static void initialize() {
        Registry.register(Registries.ITEM_GROUP, new Identifier("funnyarch", "main_group"), FUNNYARCH);
    }
}

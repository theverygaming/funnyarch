package theverygaming.funnyarch.block;

import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.item.ItemStack;
import net.minecraft.screen.ScreenHandler;

public class ScreenScreenHandler extends ScreenHandler {
    public ScreenScreenHandler(int syncId, PlayerInventory playerInventory) {
        super(Blocks.SCREEN_SCREEN_HANDLER, syncId);
    }

    public ScreenScreenHandler(int syncId) {
        super(Blocks.SCREEN_SCREEN_HANDLER, syncId);
    }

    @Override
    public boolean canUse(PlayerEntity player) {
        return true;
    }

    @Override
    public ItemStack quickMove(PlayerEntity player, int invSlot) {
        ItemStack newStack = ItemStack.EMPTY;

        return newStack;
    }
}

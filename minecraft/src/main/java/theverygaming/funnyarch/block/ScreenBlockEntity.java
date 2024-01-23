package theverygaming.funnyarch.block;

import com.mojang.serialization.MapCodec;
import net.minecraft.block.BlockState;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.screen.NamedScreenHandlerFactory;
import net.minecraft.screen.ScreenHandler;
import net.minecraft.util.math.BlockPos;
import net.minecraft.text.Text;

public class ScreenBlockEntity extends BlockEntity implements NamedScreenHandlerFactory {
    public ScreenBlockEntity(BlockPos pos, BlockState state) {
        super(Blocks.SCREEN_BLOCK_ENTITY, pos, state);
    }

    public MapCodec<ScreenBlock> getCodec() {
        throw new UnsupportedOperationException("getCodec is not implemented");
    }

    @Override
    public ScreenHandler createMenu(int syncId, PlayerInventory playerInventory, PlayerEntity player) {
        return new ScreenScreenHandler(syncId);
    }

    @Override
    public Text getDisplayName() {
        return Text.translatable(getCachedState().getBlock().getTranslationKey());
    }
}

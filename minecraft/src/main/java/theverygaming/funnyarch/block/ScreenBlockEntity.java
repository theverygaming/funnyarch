package theverygaming.funnyarch.block;

import java.util.ArrayList;

import com.mojang.serialization.MapCodec;
import net.minecraft.block.BlockState;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.screen.NamedScreenHandlerFactory;
import net.minecraft.screen.ScreenHandler;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;
import net.minecraft.text.Text;

public class ScreenBlockEntity extends BlockEntity implements NamedScreenHandlerFactory, BusCableInterface {
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

    private ArrayList<BlockPos> connectedBlocks = new ArrayList<>();

    @Override
    public void readNbt(NbtCompound nbt) {
        super.readNbt(nbt);
        BusCableInterface.readNbtHelper(nbt, connectedBlocks);
    }

    @Override
    public void writeNbt(NbtCompound nbt) {
        BusCableInterface.writeNbtHelper(nbt, connectedBlocks);
        super.writeNbt(nbt);
    }

    @Override
    public void addConnection(World world, BlockPos pos) {
        BusCableInterface.addConnectionHelper(world, pos, connectedBlocks);
    }

    @Override
    public void removeConnection(World world, BlockPos pos) {
        BusCableInterface.removeConnectionHelper(world, pos, connectedBlocks);
    }

    @Override
    public void busCableTransmit(World world, ArrayList<BlockPos> visited, int data[]) {
        System.out.println("received data: " + Integer.toString(data[0]));
        BusCableInterface.busCableTransmitHelper(world, visited, data, connectedBlocks, this.pos);
    }
}

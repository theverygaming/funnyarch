package theverygaming.funnyarch.block;

import java.util.ArrayList;

import com.mojang.serialization.MapCodec;
import net.minecraft.block.BlockState;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;

public class BusCableBlockEntity extends BlockEntity implements BusCableInterface {
    public BusCableBlockEntity(BlockPos pos, BlockState state) {
        super(Blocks.BUS_CABLE_BLOCK_ENTITY, pos, state);
    }

    public MapCodec<BusCableBlock> getCodec() {
        throw new UnsupportedOperationException("getCodec is not implemented");
    }

    private ArrayList<BlockPos> connectedBlocks = new ArrayList<>();

    public int getNConnections() {
        return connectedBlocks.size();
    }

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
        // System.out.println("transmitting data: " + Integer.toString(data[0]));
        BusCableInterface.busCableTransmitHelper(world, visited, data, connectedBlocks, this.pos);
    }
}

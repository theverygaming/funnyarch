package theverygaming.funnyarch.block;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.jetbrains.annotations.Nullable;

import net.minecraft.block.BlockState;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.nbt.NbtCompound;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.Direction;
import net.minecraft.world.World;

public interface BusCableInterface {
    void busCableTransmit(World world, @Nullable ArrayList<BlockPos> visited, int data[]);

    void addConnection(World world, BlockPos pos);

    void removeConnection(World world, BlockPos pos);

    public static void busCableTransmitHelper(World world, @Nullable ArrayList<BlockPos> visited, int data[],
            ArrayList<BlockPos> connectedBlocks, BlockPos ownPos) {
        // first block in chain?
        if (visited.size() == 0) {
            visited.add(ownPos);
        }
        for (BlockPos pos : connectedBlocks) {
            boolean isVisited = false;
            for (BlockPos v : visited) {
                if (pos.equals(v)) {
                    isVisited = true;
                    break;
                }
            }
            if (isVisited) {
                continue;
            }
            visited.add(pos);
            BlockEntity blockEntity = world.getBlockEntity(pos);
            if (blockEntity instanceof BusCableInterface) {
                BusCableInterface entity = (BusCableInterface) blockEntity;
                entity.busCableTransmit(world, visited, data);
            }
        }
    }

    public static void writeNbtHelper(NbtCompound nbt, ArrayList<BlockPos> connectedBlocks) {
        ArrayList<Integer> list = new ArrayList<>();
        for (BlockPos pos : connectedBlocks) {
            list.add(pos.getX());
            list.add(pos.getY());
            list.add(pos.getZ());
        }
        nbt.putIntArray("connectedBlocks", list);
    }

    public static void readNbtHelper(NbtCompound nbt, ArrayList<BlockPos> connectedBlocks) {
        int list[] = nbt.getIntArray("connectedBlocks");
        if ((list.length % 3) == 0) {
            for (int i = 0; i < list.length; i += 3) {
                connectedBlocks.add(new BlockPos(list[i], list[i + 1], list[i + 2]));
            }
        }
    }

    public static void addConnectionHelper(World world, BlockPos pos, ArrayList<BlockPos> connectedBlocks) {
        // TODO: error on double add or smth
        BlockEntity blockEntity = world.getBlockEntity(pos);
        if (blockEntity instanceof BusCableInterface) {
            connectedBlocks.add(pos);
        }
    }

    public static void removeConnectionHelper(World world, BlockPos pos, ArrayList<BlockPos> connectedBlocks) {
        connectedBlocks.removeAll(Collections.singleton(pos));
    }

    private static List<BlockPos> getAdjacentConnectable(World world, BlockPos pos) {
        List<BlockPos> positions = new ArrayList<>();
        for (Direction direction : Direction.values()) {
            BlockPos adjacentPos = pos.offset(direction);

            if (world.getBlockEntity(adjacentPos) instanceof BusCableInterface) {
                positions.add(adjacentPos);
            }
        }
        return positions;
    }

    public static void onBrokenHelper(World world, BlockPos pos, BlockState state) {
        for (BlockPos adjacentPos : getAdjacentConnectable(world, pos)) {
            BusCableInterface adjacentEntity = (BusCableInterface) world.getBlockEntity(adjacentPos);
            adjacentEntity.removeConnection(world, pos);
        }
    }

    public static void onPlacedHelper(World world, BlockPos pos, BlockState state) {
        BusCableInterface blockEntity = (BusCableInterface) world.getBlockEntity(pos);
        for (BlockPos adjacentPos : getAdjacentConnectable(world, pos)) {
            BusCableInterface adjacentEntity = (BusCableInterface) world.getBlockEntity(adjacentPos);
            adjacentEntity.addConnection(world, pos);
            blockEntity.addConnection(world, adjacentPos);
        }
    }
}

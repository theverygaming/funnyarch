package theverygaming.funnyarch.block;

import com.mojang.serialization.MapCodec;

import net.minecraft.block.BlockRenderType;
import net.minecraft.block.BlockState;
import net.minecraft.block.BlockWithEntity;
import net.minecraft.block.entity.BlockEntity;
import net.minecraft.entity.LivingEntity;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.item.ItemStack;
import net.minecraft.util.ActionResult;
import net.minecraft.util.Hand;
import net.minecraft.util.hit.BlockHitResult;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;
import net.minecraft.world.WorldAccess;
import net.minecraft.text.Text;

public class BusCableBlock extends BlockWithEntity {

    public BusCableBlock(Settings settings) {
        super(settings);
    }

    public MapCodec<BusCableBlock> getCodec() {
        throw new UnsupportedOperationException("getCodec is not implemented");
    }

    @Override
    public BlockEntity createBlockEntity(BlockPos pos, BlockState state) {
        return new BusCableBlockEntity(pos, state);
    }

    @Override
    public BlockRenderType getRenderType(BlockState state) {
        return BlockRenderType.MODEL;
    }

    @Override
    public ActionResult onUse(BlockState state, World world, BlockPos pos, PlayerEntity player, Hand hand,
            BlockHitResult hit) {
        if (!world.isClient) {
            BlockEntity blockEntity = world.getBlockEntity(pos);

            if (blockEntity instanceof BusCableBlockEntity) {
                BusCableBlockEntity entity = (BusCableBlockEntity) blockEntity;
                player.sendMessage(Text.literal(
                        "Hello world from cable .. got " + Integer.toString(entity.getNConnections()) + " connections"),
                        false);
            }
        }

        return ActionResult.SUCCESS;
    }

    @Override
    public void onPlaced(World world, BlockPos pos, BlockState state, LivingEntity placer, ItemStack itemStack) {
        super.onPlaced(world, pos, state, placer, itemStack);

        if (!world.isClient) {
            BusCableInterface.onPlacedHelper(world, pos, state);
        }
    }

    @Override
    public void onBroken(WorldAccess world, BlockPos pos, BlockState state) {
        if (!world.isClient()) {
            BusCableInterface.onBrokenHelper((World) world, pos, state);
        }

        super.onBroken(world, pos, state);
    }
}

package theverygaming.funnyarch.screens;

import com.mojang.blaze3d.systems.RenderSystem;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.ingame.HandledScreen;
import net.minecraft.client.render.GameRenderer;
import net.minecraft.client.texture.NativeImage;
import net.minecraft.client.texture.NativeImageBackedTexture;
import net.minecraft.entity.player.PlayerInventory;
import net.minecraft.text.Text;
import net.minecraft.util.Identifier;
import net.minecraft.client.MinecraftClient;

public class ScreenScreen extends HandledScreen<theverygaming.funnyarch.block.ScreenScreenHandler> {
    private Identifier textureID;
    private NativeImageBackedTexture nibt;

    private final int screen_width = 640;
    private final int screen_height = 480;

    public ScreenScreen(theverygaming.funnyarch.block.ScreenScreenHandler handler, PlayerInventory inventory,
            Text title) {
        super(handler, inventory, title);
    }

    @Override
    protected void drawBackground(DrawContext ctx, float delta, int mouseX, int mouseY) {
        generateTexture();
        double guiScale = MinecraftClient.getInstance().getWindow().getScaleFactor();

        RenderSystem.setShader(GameRenderer::getPositionTexProgram);
        RenderSystem.setShaderColor(1.0F, 1.0F, 1.0F, 0.0F);
        RenderSystem.setShaderTexture(0, textureID);
        int w = (int) (screen_width / guiScale);
        int h = (int) (screen_height / guiScale);
        int x = (width - w) / 2;
        int y = (height - h) / 2;
        ctx.drawTexture(textureID, x, y, 0, 0, w, h, w, h);
    }

    private void generateTexture() {
        // ByteBuffer buffer = ByteBuffer.allocate(10 * 10 * 3);
        NativeImage.Format fmt = NativeImage.Format.RGBA;
        NativeImage image = new NativeImage(fmt, screen_width, screen_height, true);
        image.fillRect(0, 0, screen_width, screen_height, 0xFF000000);
        for (int i = 0; i < screen_width; i++) {
            image.setColor(i, 0, 0xFFFFA000);
        }
        for (int i = 0; i < screen_height; i++) {
            image.setColor(0, i, 0xFFFFA000);
        }
        for (int i = 0; i < screen_height; i++) {
            image.setColor(i, i, 0xFF0000FF);
        }
        for (int i = 0; i < screen_height; i++) {
            image.setColor(screen_width - 1, i, 0xFF00FF00);
        }
        for (int i = 0; i < screen_width; i++) {
            image.setColor(i, screen_height - 1, 0xFF00FF00);
        }
        if (image != null) {
            if(nibt != null) {
                nibt.close();
            }
            nibt = new NativeImageBackedTexture(image);
            if (textureID != null) {
                MinecraftClient.getInstance().getTextureManager().destroyTexture(textureID);
            }
            textureID = MinecraftClient.getInstance().getTextureManager().registerDynamicTexture("screen_display",
                    nibt);
        }
    }

    @Override
    public void render(DrawContext ctx, int mouseX, int mouseY, float delta) {
        renderBackground(ctx, mouseX, mouseY, delta);
        drawMouseoverTooltip(ctx, mouseX, mouseY);
    }

    @Override
    protected void init() {
        super.init();
    }
}

package org.example.patterns;
public class CanvasStateTest {
    public static void main(String[] args) {
        CanvasContext ctx = new CanvasContext();
        if (!ctx.request().equals("was-off-canvas")) throw new AssertionError();
        if (!ctx.request().equals("was-on-canvas")) throw new AssertionError();
        System.out.println("ok");
    }
}

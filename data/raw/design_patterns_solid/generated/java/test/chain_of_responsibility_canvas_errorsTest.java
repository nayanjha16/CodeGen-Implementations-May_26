package org.example.patterns;
public class CanvasChainTest {
    public static void main(String[] args) {
        CanvasHandler h = new CanvasLowHandler();
        h.link(new CanvasHighHandler());
        if (!h.handle(2, "m").equals("high-canvas:m")) throw new AssertionError();
        System.out.println("ok");
    }
}

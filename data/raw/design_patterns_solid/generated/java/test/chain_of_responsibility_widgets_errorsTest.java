package org.example.patterns;
public class WidgetsChainTest {
    public static void main(String[] args) {
        WidgetsHandler h = new WidgetsLowHandler();
        h.link(new WidgetsHighHandler());
        if (!h.handle(2, "m").equals("high-widgets:m")) throw new AssertionError();
        System.out.println("ok");
    }
}

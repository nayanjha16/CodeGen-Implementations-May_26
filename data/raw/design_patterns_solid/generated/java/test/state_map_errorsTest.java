package org.example.patterns;
public class MapStateTest {
    public static void main(String[] args) {
        MapContext ctx = new MapContext();
        if (!ctx.request().equals("was-off-map")) throw new AssertionError();
        if (!ctx.request().equals("was-on-map")) throw new AssertionError();
        System.out.println("ok");
    }
}

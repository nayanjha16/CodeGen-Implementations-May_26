package org.example.patterns;
public class MapStrategyTest {
    public static void main(String[] args) {
        MapContext ctx = new MapContext(new MapDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

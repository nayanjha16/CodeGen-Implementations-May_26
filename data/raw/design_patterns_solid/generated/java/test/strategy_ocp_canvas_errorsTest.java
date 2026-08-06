package org.example.patterns;
public class CanvasStrategyTest {
    public static void main(String[] args) {
        CanvasContext ctx = new CanvasContext(new CanvasDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

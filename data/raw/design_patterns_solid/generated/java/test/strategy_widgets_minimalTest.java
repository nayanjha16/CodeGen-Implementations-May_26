package org.example.patterns;
public class WidgetsStrategyTest {
    public static void main(String[] args) {
        WidgetsContext ctx = new WidgetsContext(new WidgetsDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class PluginStrategyTest {
    public static void main(String[] args) {
        PluginContext ctx = new PluginContext(new PluginDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

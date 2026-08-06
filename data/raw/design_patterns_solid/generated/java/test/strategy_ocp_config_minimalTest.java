package org.example.patterns;
public class ConfigStrategyTest {
    public static void main(String[] args) {
        ConfigContext ctx = new ConfigContext(new ConfigDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

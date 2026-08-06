package org.example.patterns;
public class SensorsStrategyTest {
    public static void main(String[] args) {
        SensorsContext ctx = new SensorsContext(new SensorsDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

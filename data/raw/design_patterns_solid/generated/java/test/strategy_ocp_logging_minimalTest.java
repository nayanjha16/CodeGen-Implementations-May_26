package org.example.patterns;
public class LoggingStrategyTest {
    public static void main(String[] args) {
        LoggingContext ctx = new LoggingContext(new LoggingDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class StreamingStrategyTest {
    public static void main(String[] args) {
        StreamingContext ctx = new StreamingContext(new StreamingDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

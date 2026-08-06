package org.example.patterns;
public class FeedStrategyTest {
    public static void main(String[] args) {
        FeedContext ctx = new FeedContext(new FeedDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class VideoStrategyTest {
    public static void main(String[] args) {
        VideoContext ctx = new VideoContext(new VideoDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

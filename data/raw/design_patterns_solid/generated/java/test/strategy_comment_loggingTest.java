package org.example.patterns;
public class CommentStrategyTest {
    public static void main(String[] args) {
        CommentContext ctx = new CommentContext(new CommentDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

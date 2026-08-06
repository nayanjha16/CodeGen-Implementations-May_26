package org.example.patterns;
public class ChatStrategyTest {
    public static void main(String[] args) {
        ChatContext ctx = new ChatContext(new ChatDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

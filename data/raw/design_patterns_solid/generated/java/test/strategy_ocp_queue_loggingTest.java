package org.example.patterns;
public class QueueStrategyTest {
    public static void main(String[] args) {
        QueueContext ctx = new QueueContext(new QueueDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

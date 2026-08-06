package org.example.patterns;
public class NotificationsStrategyTest {
    public static void main(String[] args) {
        NotificationsContext ctx = new NotificationsContext(new NotificationsDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

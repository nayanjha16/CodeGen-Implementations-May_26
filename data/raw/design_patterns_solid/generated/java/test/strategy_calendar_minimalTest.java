package org.example.patterns;
public class CalendarStrategyTest {
    public static void main(String[] args) {
        CalendarContext ctx = new CalendarContext(new CalendarDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class BookingStrategyTest {
    public static void main(String[] args) {
        BookingContext ctx = new BookingContext(new BookingDiscountStrategy());
        if (ctx.execute(10) != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

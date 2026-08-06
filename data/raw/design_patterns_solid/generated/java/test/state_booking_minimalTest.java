package org.example.patterns;
public class BookingStateTest {
    public static void main(String[] args) {
        BookingContext ctx = new BookingContext();
        if (!ctx.request().equals("was-off-booking")) throw new AssertionError();
        if (!ctx.request().equals("was-on-booking")) throw new AssertionError();
        System.out.println("ok");
    }
}

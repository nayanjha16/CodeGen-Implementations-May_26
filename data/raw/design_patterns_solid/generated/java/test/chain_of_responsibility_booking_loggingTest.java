package org.example.patterns;
public class BookingChainTest {
    public static void main(String[] args) {
        BookingHandler h = new BookingLowHandler();
        h.link(new BookingHighHandler());
        if (!h.handle(2, "m").equals("high-booking:m")) throw new AssertionError();
        System.out.println("ok");
    }
}

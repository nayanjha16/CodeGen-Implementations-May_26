package org.example.patterns;
public class BookingSrpTest {
    public static void main(String[] args) {
        BookingRecord r = new BookingRecord("a", 3);
        if (!new BookingFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}

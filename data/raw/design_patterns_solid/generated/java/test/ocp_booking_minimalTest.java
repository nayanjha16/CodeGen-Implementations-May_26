package org.example.patterns;
public class BookingOcpTest {
    public static void main(String[] args) {
        if (new BookingPriceEngine(new BookingTenPercent()).quote(100) != 90) throw new AssertionError();
        System.out.println("ok");
    }
}

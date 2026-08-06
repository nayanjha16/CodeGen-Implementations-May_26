package org.example.patterns;
public class BookingFactoryTest {
    public static void main(String[] args) {
        BookingFactory f = new BookingFactory();
        if (!f.create("basic").operate().equals("basic-booking")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-booking")) throw new AssertionError();
        System.out.println("ok");
    }
}

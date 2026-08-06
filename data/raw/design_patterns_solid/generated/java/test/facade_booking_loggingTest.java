package org.example.patterns;
public class BookingFacadeTest {
    public static void main(String[] args) {
        BookingFacade f = new BookingFacade();
        if (!f.submit("x").equals("wrote-booking:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

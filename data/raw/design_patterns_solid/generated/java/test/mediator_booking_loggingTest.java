package org.example.patterns;
public class BookingMediatorTest {
    public static void main(String[] args) {
        BookingMediator m = new BookingMediator();
        new BookingColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}

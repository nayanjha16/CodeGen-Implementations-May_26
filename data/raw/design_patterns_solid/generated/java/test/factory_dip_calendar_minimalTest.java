package org.example.patterns;
public class CalendarFactoryTest {
    public static void main(String[] args) {
        CalendarFactory f = new CalendarFactory();
        if (!f.create("basic").operate().equals("basic-calendar")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-calendar")) throw new AssertionError();
        System.out.println("ok");
    }
}

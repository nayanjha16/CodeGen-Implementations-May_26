package org.example.patterns;
public class BookingSingletonTest {
    public static void main(String[] args) {
        BookingSingleton a = BookingSingleton.getInstance();
        BookingSingleton b = BookingSingleton.getInstance();
        a.setValue("booking-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("booking-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}

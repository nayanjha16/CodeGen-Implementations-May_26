package org.example.patterns;
public class BookingLspTest {
    public static void main(String[] args) {
        BookingShape[] arr = new BookingShape[] { new BookingRectangle(2,3), new BookingSquare(4) };
        if (BookingLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class BookingIspTest {
    public static void main(String[] args) {
        BookingStore st = new BookingStore();
        st.write("x");
        if (!BookingIspClient.mirror(st).equals("booking:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

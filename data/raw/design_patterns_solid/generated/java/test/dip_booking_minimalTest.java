package org.example.patterns;
public class BookingDipTest {
    public static void main(String[] args) {
        String out = new BookingAppService(new BookingHttpGateway()).publish("p");
        if (!out.equals("http-booking:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

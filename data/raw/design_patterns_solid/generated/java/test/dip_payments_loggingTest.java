package org.example.patterns;
public class PaymentsDipTest {
    public static void main(String[] args) {
        String out = new PaymentsAppService(new PaymentsHttpGateway()).publish("p");
        if (!out.equals("http-payments:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

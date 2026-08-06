package org.example.patterns;
public class ShippingDipTest {
    public static void main(String[] args) {
        String out = new ShippingAppService(new ShippingHttpGateway()).publish("p");
        if (!out.equals("http-shipping:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

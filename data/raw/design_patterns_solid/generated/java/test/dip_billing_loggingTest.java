package org.example.patterns;
public class BillingDipTest {
    public static void main(String[] args) {
        String out = new BillingAppService(new BillingHttpGateway()).publish("p");
        if (!out.equals("http-billing:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

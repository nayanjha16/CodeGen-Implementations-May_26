package org.example.patterns;
public class SmsDipTest {
    public static void main(String[] args) {
        String out = new SmsAppService(new SmsHttpGateway()).publish("p");
        if (!out.equals("http-sms:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

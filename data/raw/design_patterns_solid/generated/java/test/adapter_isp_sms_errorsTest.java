package org.example.patterns;
public class SmsAdapterTest {
    public static void main(String[] args) {
        SmsTarget t = new SmsAdapter(new SmsLegacyApi());
        if (!t.fetch().equals("modern-sms")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}

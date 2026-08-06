package org.example.patterns;
public class SmsAbstractFactoryTest {
    public static void main(String[] args) {
        String out = SmsAbstractFactoryDemo.run(new SmsCloudFactory());
        if (!out.equals("cloud-btn-sms|cloud-dlg-sms")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

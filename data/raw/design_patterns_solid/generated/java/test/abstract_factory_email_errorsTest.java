package org.example.patterns;
public class EmailAbstractFactoryTest {
    public static void main(String[] args) {
        String out = EmailAbstractFactoryDemo.run(new EmailCloudFactory());
        if (!out.equals("cloud-btn-email|cloud-dlg-email")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

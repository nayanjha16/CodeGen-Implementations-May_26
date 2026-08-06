package org.example.patterns;
public class PaymentsAbstractFactoryTest {
    public static void main(String[] args) {
        String out = PaymentsAbstractFactoryDemo.run(new PaymentsCloudFactory());
        if (!out.equals("cloud-btn-payments|cloud-dlg-payments")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

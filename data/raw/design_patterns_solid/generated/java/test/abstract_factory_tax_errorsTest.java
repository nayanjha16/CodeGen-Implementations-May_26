package org.example.patterns;
public class TaxAbstractFactoryTest {
    public static void main(String[] args) {
        String out = TaxAbstractFactoryDemo.run(new TaxCloudFactory());
        if (!out.equals("cloud-btn-tax|cloud-dlg-tax")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

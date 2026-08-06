package org.example.patterns;
public class DiscountAbstractFactoryTest {
    public static void main(String[] args) {
        String out = DiscountAbstractFactoryDemo.run(new DiscountCloudFactory());
        if (!out.equals("cloud-btn-discount|cloud-dlg-discount")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

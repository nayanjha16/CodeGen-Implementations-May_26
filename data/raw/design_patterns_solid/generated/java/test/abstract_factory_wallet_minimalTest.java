package org.example.patterns;
public class WalletAbstractFactoryTest {
    public static void main(String[] args) {
        String out = WalletAbstractFactoryDemo.run(new WalletCloudFactory());
        if (!out.equals("cloud-btn-wallet|cloud-dlg-wallet")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

package org.example.patterns;
public class WalletTemplateTest {
    public static void main(String[] args) {
        String out = new WalletUpperTemplate().run(" ab ");
        if (!out.equals("wallet|AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

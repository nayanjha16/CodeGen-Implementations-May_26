package org.example.patterns;
public class WalletVisitorTest {
    public static void main(String[] args) {
        String out = new WalletLeaf("n").accept(new WalletPrintVisitor());
        if (!out.equals("wallet:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

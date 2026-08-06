package org.example.patterns;
public class WalletIteratorTest {
    public static void main(String[] args) {
        WalletCollection col = new WalletCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("wallet:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}

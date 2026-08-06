package org.example.patterns;
public class WalletInterpreterTest {
    public static void main(String[] args) {
        WalletInterpreter i = new WalletInterpreter();
        if (i.eval("2+3") != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

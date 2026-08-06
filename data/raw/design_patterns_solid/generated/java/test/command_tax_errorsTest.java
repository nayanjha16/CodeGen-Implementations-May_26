package org.example.patterns;
public class TaxCommandTest {
    public static void main(String[] args) {
        TaxCommand cmd = new TaxActionCommand(new TaxReceiver(), "x");
        if (!cmd.execute().equals("done-tax:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class TaxDecoratorTest {
    public static void main(String[] args) {
        TaxComponent c = new TaxUpperDecorator(new TaxCore());
        String out = c.process("ab");
        if (!out.equals("TAX:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

package org.example.patterns;
public class LicenseDecoratorTest {
    public static void main(String[] args) {
        LicenseComponent c = new LicenseUpperDecorator(new LicenseCore());
        String out = c.process("ab");
        if (!out.equals("LICENSE:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

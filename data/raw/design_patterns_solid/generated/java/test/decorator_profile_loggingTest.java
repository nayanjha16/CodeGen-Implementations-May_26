package org.example.patterns;
public class ProfileDecoratorTest {
    public static void main(String[] args) {
        ProfileComponent c = new ProfileUpperDecorator(new ProfileCore());
        String out = c.process("ab");
        if (!out.equals("PROFILE:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

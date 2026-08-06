package org.example.patterns;
public class SyncDecoratorTest {
    public static void main(String[] args) {
        SyncComponent c = new SyncUpperDecorator(new SyncCore());
        String out = c.process("ab");
        if (!out.equals("SYNC:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

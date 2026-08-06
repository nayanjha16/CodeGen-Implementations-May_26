package org.example.patterns;
public class AudioDecoratorTest {
    public static void main(String[] args) {
        AudioComponent c = new AudioUpperDecorator(new AudioCore());
        String out = c.process("ab");
        if (!out.equals("AUDIO:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

package org.example.patterns;
public class FeedDecoratorTest {
    public static void main(String[] args) {
        FeedComponent c = new FeedUpperDecorator(new FeedCore());
        String out = c.process("ab");
        if (!out.equals("FEED:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

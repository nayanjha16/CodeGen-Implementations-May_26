package org.example.patterns;
public class VideoDecoratorTest {
    public static void main(String[] args) {
        VideoComponent c = new VideoUpperDecorator(new VideoCore());
        String out = c.process("ab");
        if (!out.equals("VIDEO:AB")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

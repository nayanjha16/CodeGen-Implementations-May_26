package org.example.patterns;
public class AudioVisitorTest {
    public static void main(String[] args) {
        String out = new AudioLeaf("n").accept(new AudioPrintVisitor());
        if (!out.equals("audio:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

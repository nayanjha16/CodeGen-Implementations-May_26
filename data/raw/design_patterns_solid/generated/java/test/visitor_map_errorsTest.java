package org.example.patterns;
public class MapVisitorTest {
    public static void main(String[] args) {
        String out = new MapLeaf("n").accept(new MapPrintVisitor());
        if (!out.equals("map:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

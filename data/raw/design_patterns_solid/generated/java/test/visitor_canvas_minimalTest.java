package org.example.patterns;
public class CanvasVisitorTest {
    public static void main(String[] args) {
        String out = new CanvasLeaf("n").accept(new CanvasPrintVisitor());
        if (!out.equals("canvas:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

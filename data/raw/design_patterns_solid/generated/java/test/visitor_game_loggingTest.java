package org.example.patterns;
public class GameVisitorTest {
    public static void main(String[] args) {
        String out = new GameLeaf("n").accept(new GamePrintVisitor());
        if (!out.equals("game:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

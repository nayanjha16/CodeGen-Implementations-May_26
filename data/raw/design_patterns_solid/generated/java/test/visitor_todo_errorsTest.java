package org.example.patterns;
public class TodoVisitorTest {
    public static void main(String[] args) {
        String out = new TodoLeaf("n").accept(new TodoPrintVisitor());
        if (!out.equals("todo:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

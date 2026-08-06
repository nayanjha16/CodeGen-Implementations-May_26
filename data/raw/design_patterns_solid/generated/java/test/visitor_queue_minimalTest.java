package org.example.patterns;
public class QueueVisitorTest {
    public static void main(String[] args) {
        String out = new QueueLeaf("n").accept(new QueuePrintVisitor());
        if (!out.equals("queue:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

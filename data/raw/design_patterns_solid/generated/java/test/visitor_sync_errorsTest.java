package org.example.patterns;
public class SyncVisitorTest {
    public static void main(String[] args) {
        String out = new SyncLeaf("n").accept(new SyncPrintVisitor());
        if (!out.equals("sync:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

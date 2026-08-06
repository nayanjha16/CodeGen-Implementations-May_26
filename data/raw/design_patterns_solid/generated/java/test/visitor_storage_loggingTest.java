package org.example.patterns;
public class StorageVisitorTest {
    public static void main(String[] args) {
        String out = new StorageLeaf("n").accept(new StoragePrintVisitor());
        if (!out.equals("storage:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

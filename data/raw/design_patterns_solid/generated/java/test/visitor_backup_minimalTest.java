package org.example.patterns;
public class BackupVisitorTest {
    public static void main(String[] args) {
        String out = new BackupLeaf("n").accept(new BackupPrintVisitor());
        if (!out.equals("backup:n")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

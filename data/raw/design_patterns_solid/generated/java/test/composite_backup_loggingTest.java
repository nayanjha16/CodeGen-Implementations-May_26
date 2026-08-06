package org.example.patterns;
public class BackupCompositeTest {
    public static void main(String[] args) {
        BackupComposite root = new BackupComposite();
        root.add(new BackupLeaf(2));
        root.add(new BackupLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

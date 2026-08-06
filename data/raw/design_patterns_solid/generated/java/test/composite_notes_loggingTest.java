package org.example.patterns;
public class NotesCompositeTest {
    public static void main(String[] args) {
        NotesComposite root = new NotesComposite();
        root.add(new NotesLeaf(2));
        root.add(new NotesLeaf(3));
        if (root.size() != 5) throw new AssertionError();
        System.out.println("ok");
    }
}

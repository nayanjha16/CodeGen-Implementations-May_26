package org.example.patterns;
public class EditorPrototypeTest {
    public static void main(String[] args) {
        EditorPrototype a = new EditorPrototype("editor", 2);
        EditorPrototype b = a.copy();
        b.setLabel("editor-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}

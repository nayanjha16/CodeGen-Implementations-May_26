package org.example.patterns;
public class EditorSingletonTest {
    public static void main(String[] args) {
        EditorSingleton a = EditorSingleton.getInstance();
        EditorSingleton b = EditorSingleton.getInstance();
        a.setValue("editor-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("editor-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}

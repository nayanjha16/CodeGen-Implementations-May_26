package org.example.patterns;
public class EditorMementoTest {
    public static void main(String[] args) {
        EditorOriginator o = new EditorOriginator();
        EditorMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("editor-init")) throw new AssertionError();
        System.out.println("ok");
    }
}

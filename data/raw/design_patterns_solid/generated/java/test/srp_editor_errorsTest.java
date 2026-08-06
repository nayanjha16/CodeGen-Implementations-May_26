package org.example.patterns;
public class EditorSrpTest {
    public static void main(String[] args) {
        EditorRecord r = new EditorRecord("a", 3);
        if (!new EditorFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}

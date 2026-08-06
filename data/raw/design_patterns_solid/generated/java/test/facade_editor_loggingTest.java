package org.example.patterns;
public class EditorFacadeTest {
    public static void main(String[] args) {
        EditorFacade f = new EditorFacade();
        if (!f.submit("x").equals("wrote-editor:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

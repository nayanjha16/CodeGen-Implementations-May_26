package org.example.patterns;
public class EditorCommandTest {
    public static void main(String[] args) {
        EditorCommand cmd = new EditorActionCommand(new EditorReceiver(), "x");
        if (!cmd.execute().equals("done-editor:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

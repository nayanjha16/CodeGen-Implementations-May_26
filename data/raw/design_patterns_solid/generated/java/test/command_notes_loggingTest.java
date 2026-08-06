package org.example.patterns;
public class NotesCommandTest {
    public static void main(String[] args) {
        NotesCommand cmd = new NotesActionCommand(new NotesReceiver(), "x");
        if (!cmd.execute().equals("done-notes:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

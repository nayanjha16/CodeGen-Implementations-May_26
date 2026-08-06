package org.example.patterns;
public class NotesDipTest {
    public static void main(String[] args) {
        String out = new NotesAppService(new NotesHttpGateway()).publish("p");
        if (!out.equals("http-notes:p")) throw new AssertionError(out);
        System.out.println("ok");
    }
}

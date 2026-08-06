package org.example.patterns;
public class NotesIspTest {
    public static void main(String[] args) {
        NotesStore st = new NotesStore();
        st.write("x");
        if (!NotesIspClient.mirror(st).equals("notes:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

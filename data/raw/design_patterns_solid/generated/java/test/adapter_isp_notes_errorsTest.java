package org.example.patterns;
public class NotesAdapterTest {
    public static void main(String[] args) {
        NotesTarget t = new NotesAdapter(new NotesLegacyApi());
        if (!t.fetch().equals("modern-notes")) throw new AssertionError(t.fetch());
        System.out.println("ok");
    }
}

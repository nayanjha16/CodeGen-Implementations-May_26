package org.example.patterns;
public class NotesMementoTest {
    public static void main(String[] args) {
        NotesOriginator o = new NotesOriginator();
        NotesMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("notes-init")) throw new AssertionError();
        System.out.println("ok");
    }
}

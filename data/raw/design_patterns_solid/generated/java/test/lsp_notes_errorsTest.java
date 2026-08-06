package org.example.patterns;
public class NotesLspTest {
    public static void main(String[] args) {
        NotesShape[] arr = new NotesShape[] { new NotesRectangle(2,3), new NotesSquare(4) };
        if (NotesLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}

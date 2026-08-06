package org.example.patterns;
public class NotesIteratorTest {
    public static void main(String[] args) {
        NotesCollection col = new NotesCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("notes:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}

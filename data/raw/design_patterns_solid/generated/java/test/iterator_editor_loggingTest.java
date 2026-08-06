package org.example.patterns;
public class EditorIteratorTest {
    public static void main(String[] args) {
        EditorCollection col = new EditorCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("editor:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}

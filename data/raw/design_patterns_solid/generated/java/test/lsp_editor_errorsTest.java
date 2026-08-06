package org.example.patterns;
public class EditorLspTest {
    public static void main(String[] args) {
        EditorShape[] arr = new EditorShape[] { new EditorRectangle(2,3), new EditorSquare(4) };
        if (EditorLspUtil.total(arr) != 22) throw new AssertionError();
        System.out.println("ok");
    }
}

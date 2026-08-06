package org.example.patterns;
public class WidgetsIteratorTest {
    public static void main(String[] args) {
        WidgetsCollection col = new WidgetsCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("widgets:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}

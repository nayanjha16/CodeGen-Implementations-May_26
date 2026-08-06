package org.example.patterns;
public class TodoIteratorTest {
    public static void main(String[] args) {
        TodoCollection col = new TodoCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("todo:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}

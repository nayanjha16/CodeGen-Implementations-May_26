package org.example.patterns;
public class TodoSrpTest {
    public static void main(String[] args) {
        TodoRecord r = new TodoRecord("a", 3);
        if (!new TodoFormatter().format(r).equals("a=3")) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class TodoStateTest {
    public static void main(String[] args) {
        TodoContext ctx = new TodoContext();
        if (!ctx.request().equals("was-off-todo")) throw new AssertionError();
        if (!ctx.request().equals("was-on-todo")) throw new AssertionError();
        System.out.println("ok");
    }
}

package org.example.patterns;
public class TodoChainTest {
    public static void main(String[] args) {
        TodoHandler h = new TodoLowHandler();
        h.link(new TodoHighHandler());
        if (!h.handle(2, "m").equals("high-todo:m")) throw new AssertionError();
        System.out.println("ok");
    }
}

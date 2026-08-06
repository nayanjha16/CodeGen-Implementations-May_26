package org.example.patterns;
public class TodoPrototypeTest {
    public static void main(String[] args) {
        TodoPrototype a = new TodoPrototype("todo", 2);
        TodoPrototype b = a.copy();
        b.setLabel("todo-copy");
        if (a.describe().equals(b.describe())) throw new AssertionError();
        System.out.println("ok");
    }
}

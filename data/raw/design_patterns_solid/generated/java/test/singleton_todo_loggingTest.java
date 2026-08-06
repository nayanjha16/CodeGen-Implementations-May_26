package org.example.patterns;
public class TodoSingletonTest {
    public static void main(String[] args) {
        TodoSingleton a = TodoSingleton.getInstance();
        TodoSingleton b = TodoSingleton.getInstance();
        a.setValue("todo-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("todo-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}

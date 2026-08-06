package org.example.patterns;
public class TodoFactoryTest {
    public static void main(String[] args) {
        TodoFactory f = new TodoFactory();
        if (!f.create("basic").operate().equals("basic-todo")) throw new AssertionError();
        if (!f.create("premium").operate().equals("premium-todo")) throw new AssertionError();
        System.out.println("ok");
    }
}

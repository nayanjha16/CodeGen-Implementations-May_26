package org.example.patterns;
public class TodoMediatorTest {
    public static void main(String[] args) {
        TodoMediator m = new TodoMediator();
        new TodoColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}

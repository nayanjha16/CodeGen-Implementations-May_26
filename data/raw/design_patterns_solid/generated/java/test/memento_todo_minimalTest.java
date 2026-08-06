package org.example.patterns;
public class TodoMementoTest {
    public static void main(String[] args) {
        TodoOriginator o = new TodoOriginator();
        TodoMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("todo-init")) throw new AssertionError();
        System.out.println("ok");
    }
}

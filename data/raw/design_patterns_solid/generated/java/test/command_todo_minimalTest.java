package org.example.patterns;
public class TodoCommandTest {
    public static void main(String[] args) {
        TodoCommand cmd = new TodoActionCommand(new TodoReceiver(), "x");
        if (!cmd.execute().equals("done-todo:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

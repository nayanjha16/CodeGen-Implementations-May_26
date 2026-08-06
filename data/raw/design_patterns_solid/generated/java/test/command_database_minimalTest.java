package org.example.patterns;
public class DatabaseCommandTest {
    public static void main(String[] args) {
        DatabaseCommand cmd = new DatabaseActionCommand(new DatabaseReceiver(), "x");
        if (!cmd.execute().equals("done-database:x")) throw new AssertionError();
        System.out.println("ok");
    }
}

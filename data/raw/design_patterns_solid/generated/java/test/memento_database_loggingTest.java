package org.example.patterns;
public class DatabaseMementoTest {
    public static void main(String[] args) {
        DatabaseOriginator o = new DatabaseOriginator();
        DatabaseMemento m = o.save();
        o.setState("changed");
        o.restore(m);
        if (!o.getState().equals("database-init")) throw new AssertionError();
        System.out.println("ok");
    }
}

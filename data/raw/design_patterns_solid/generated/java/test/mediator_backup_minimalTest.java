package org.example.patterns;
public class BackupMediatorTest {
    public static void main(String[] args) {
        BackupMediator m = new BackupMediator();
        new BackupColleague("a", m).send("hi");
        if (!m.history().equals("a->hi")) throw new AssertionError();
        System.out.println("ok");
    }
}

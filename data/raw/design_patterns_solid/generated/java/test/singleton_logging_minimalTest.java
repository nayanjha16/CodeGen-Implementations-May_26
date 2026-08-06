package org.example.patterns;
public class LoggingSingletonTest {
    public static void main(String[] args) {
        LoggingSingleton a = LoggingSingleton.getInstance();
        LoggingSingleton b = LoggingSingleton.getInstance();
        a.setValue("logging-one");
        if (a != b) throw new AssertionError("not singleton");
        if (!b.getValue().equals("logging-one")) throw new AssertionError("state not shared");
        System.out.println("ok");
    }
}

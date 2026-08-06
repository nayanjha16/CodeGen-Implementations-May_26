package org.example.patterns;
public class LoggingIteratorTest {
    public static void main(String[] args) {
        LoggingCollection col = new LoggingCollection();
        col.add("a"); col.add("b");
        if (!col.join().equals("logging:a:b")) throw new AssertionError(col.join());
        System.out.println("ok");
    }
}
